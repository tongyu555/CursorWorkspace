# 工参并行加载分析（并行度 5）与 ScheduledExecutorService 说明

## 一、并行度 5 时：是 5 个 Map 还是 1 个 Map？

### 结论：**取决于 5 个 subtask 是否在同一 JVM**

- **Java 的 static 是“按 JVM 隔离”的**：每个 JVM 进程有自己的一份静态变量，不同 JVM 之间不共享。
- **服务器上常见部署（parallelism=5）**：5 个 subtask 通常分布在 **5 个 TaskManager**（或至少多个 TM），即 **5 个 JVM** → 每个 JVM 里各有一份 `SetHdfsCmCu.nrCmDimMap` / `nrCmCorDimMap` → **一共 5 份 Map**（每种工参 5 个）。所以**在服务器上执行、并行度为 5 时，确实可以认为有 5 个 map**。
- **只有 1 个 Map 的情况**：当 5 个 subtask 都跑在 **同一个 TaskManager（同一 JVM）** 上时（例如单机 5 slot），静态变量只有一份，才是“1 个 Map、5 个 task 共享”。

---

### 1.1 代码与“静态”的含义

```text
SetHdfsCmCu（工具类）
├── public static final Map<String, NrCmDim> nrCmDimMap = new ConcurrentHashMap<>();   // 每个 JVM 内唯一
└── public static final Map<String, NrCmCorDim> nrCmCorDimMap = new ConcurrentHashMap<>();  // 每个 JVM 内唯一

ConnectNrMapFunction（每个 subtask 一个实例，共 5 个实例）
├── private Map<String, NrCmDim> nrCmDimMap = new ConcurrentHashMap<>();      // 初始是“自己的”空 Map
├── private Map<String, NrCmCorDim> nrCmCorDimMap = new ConcurrentHashMap<>();
└── open() 里：
        SetHdfsCmCu.setNrCmDimMap(...);        // 往【本 JVM 的】静态 Map 里 put
        SetHdfsCmCu.setNrCmCorDimMap(...);
        nrCmDimMap = SetHdfsCmCu.nrCmDimMap;   // 引用【本 JVM 的】静态 Map
        nrCmCorDimMap = SetHdfsCmCu.nrCmCorDimMap;
```

- **静态 Map**：在每个 **JVM 内** 每种只有 1 个；**不同 JVM 之间各有各的一份**，互不共享。
- **实例引用**：每个 subtask 的 `nrCmDimMap` / `nrCmCorDimMap` 指向**自己所在 JVM** 里的那份静态 Map。

---

### 1.2 两种部署下的实际行为

| 部署方式 | JVM 数量 | Map 数量（nrCmDimMap / nrCmCorDimMap） | 行为简述 |
|----------|----------|----------------------------------------|----------|
| **服务器典型：5 个 TM，各 1 个 subtask** | 5 | **5 份**（每种 5 个） | 每个 TM 的 open() 只往**本 JVM** 的静态 Map 写；每个 subtask 只读**本 JVM** 的 Map；定时任务也只更新本 JVM 的 Map。**相当于 5 个 map，各管各的。** |
| **单 TM 多 slot：1 个 TM 上 5 个 subtask** | 1 | **1 份**（每种 1 个） | 5 个 open() 都写**同一份**静态 Map；5 个定时任务都更新同一份 Map；5 个 map() 都读同一份。多路写同一 Map，易有覆盖/条数不一致等问题。 |

所以：

- **在服务器上、parallelism=5、且 5 个 subtask 分布在 5 个 TaskManager 时**：就是 **5 个 map**（每个 JVM 一份），每个 subtask 只加载和刷新自己所在 JVM 的那一份，互不干扰。
- **只有在“5 个 subtask 挤在 1 个 JVM”时**（例如本地或单 TM 多 slot），才是 1 个 Map、5 路写入。

---

### 1.3 小结（并行度 5）

- **服务器上执行、parallelism=5**：通常 5 个 subtask 在 5 个（或更多）TaskManager 上 → **5 个 JVM → 5 份静态 Map → 可以认为有 5 个 map**，每个 task 只使用本 JVM 的那一份。
- **单 JVM 上 5 个 subtask**：只有 1 份静态 Map，5 个 task 共享，会出现多路写同一 Map、重复加载等问题。
- 之前文档按“同一 JVM”分析，忽略了分布式下 static 按 JVM 隔离；在集群上你的理解是对的：**服务器上 parallelism=5 时，就是 5 个 map。**

---

## 二、ScheduledExecutorService 使用说明

### 2.1 是什么？

`ScheduledExecutorService` 是 JDK 提供的 **可调度线程池**：在指定延迟后执行一次，或按固定周期/固定间隔重复执行。适合“每隔一段时间做一件事”（如定时拉工参）。

---

### 2.2 常用创建方式

```java
// 单线程的调度池：所有任务在一个线程里按顺序执行，不会并发
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

// 多线程：可同时跑多个定时任务（注意任务是否线程安全）
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(4);
```

- 当前代码用的是 `newScheduledThreadPool(1)`，即 **单线程**：同一时刻只会执行一个已提交的定时任务，不会出现“两个周期任务同时跑”；但若有 5 个 subtask，就有 5 个这样的“单线程调度器”，彼此独立。

---

### 2.3 核心 API

| 方法 | 含义 |
|------|------|
| **schedule(Runnable, delay, unit)** | 延迟 `delay` 后**只执行一次**。 |
| **scheduleAtFixedRate(Runnable, initialDelay, period, unit)** | 首次在 `initialDelay` 后执行，之后**按固定周期** `period` 执行（以“上一次**开始**时间”为基准，到下一次**开始**的间隔）。若任务耗时超过 period，下次会在本次**结束后**立即开始（不会并发执行，单线程时）。 |
| **scheduleWithFixedDelay(Runnable, initialDelay, delay, unit)** | 首次在 `initialDelay` 后执行，之后**固定间隔**：上一次**结束**到下一次**开始**的间隔为 `delay`。适合“每次执行完再等一段时间再执行”。 |
| **shutdown()** | 不再接受新任务，已提交的任务会执行完。 |
| **shutdownNow()** | 尝试取消未执行的任务并中断正在执行的任务，返回未执行任务列表。 |
| **awaitTermination(timeout, unit)** | 阻塞直到：所有任务执行完、或超时、或当前线程被中断。常与 shutdown 配合使用。 |

---

### 2.4 当前代码中的用法

```java
scheduledExecutorService.scheduleAtFixedRate(() -> {
    SetHdfsCmCu.setNrCmDimMap(...);
    SetHdfsCmCu.setNrCmCorDimMap(...);
    nrCmDimMap = SetHdfsCmCu.nrCmDimMap;
    nrCmCorDimMap = SetHdfsCmCu.nrCmCorDimMap;
}, intervalGetFile, intervalGetFile, TimeUnit.MILLISECONDS);
```

- **含义**：首次在 `intervalGetFile` 毫秒后执行，之后每隔 `intervalGetFile` 毫秒**再开始**一次（固定周期）。
- **单位**：`TimeUnit.MILLISECONDS` 表示 `intervalGetFile` 的单位是毫秒。
- 若某次执行时间超过 `intervalGetFile`，在单线程池下下一次会在本次**结束后**再开始，不会重叠执行。

---

### 2.5 使用注意点（结合本场景）

| 点 | 说明 |
|------|------|
| **生命周期** | 当前在 `open()` 里创建后没有保存引用，也没有在 `close()` 里关闭，会导致**线程泄漏**。应把 scheduler 存为成员变量，在 `close()` 中调用 `shutdown()` 或 `shutdownNow()`，必要时再 `awaitTermination`。 |
| **异常** | 定时任务中的未捕获异常会导致该次执行失败，异常会被线程池吞掉（只打印到 stderr），不会自动重试。应在任务内 try-catch，打日志或告警。 |
| **AtFixedRate vs WithFixedDelay** | 若希望“严格每隔 N 毫秒执行一次”，用 `scheduleAtFixedRate`；若希望“每次执行完再等 N 毫秒再执行”，用 `scheduleWithFixedDelay`。当前是“按周期触发”，适合用 AtFixedRate；若单次加载很慢，可能造成“刚结束又马上开始”，可考虑 WithFixedDelay 或加大 period。 |
| **多实例** | 并行度 5 时，会创建 5 个 Scheduler、5 个定时任务，都写同一静态 Map，且无法在 close 时关闭（未保存引用）。建议该算子并行度改为 1，或改为“单点加载 + 广播”，避免多路写同一 Map 和多个调度器。 |

---

### 2.6 正确关闭示例（在 RichMapFunction 中）

```java
private volatile ScheduledExecutorService scheduler;

@Override
public void open(Configuration parameters) throws Exception {
    // ... 现有加载逻辑 ...
    scheduler = Executors.newScheduledThreadPool(1);
    scheduler.scheduleAtFixedRate(() -> { ... }, intervalGetFile, intervalGetFile, TimeUnit.MILLISECONDS);
}

@Override
public void close() throws Exception {
    if (scheduler != null) {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(30, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}
```

这样在算子关闭时才能回收调度线程，避免泄漏。

---

## 三、总结

- **并行度 5**：在**服务器上**（5 个 subtask 分布在 5 个 TaskManager）时，static 按 JVM 隔离，所以是 **5 份** nrCmDimMap + **5 份** nrCmCorDimMap，即 **5 个 map**，每个 subtask 只加载和刷新本 JVM 的那份；只有在**单 JVM 多 slot**（5 个 subtask 在同一 TM）时才是 1 份 Map、5 路写入。
- **ScheduledExecutorService**：用于按周期执行“拉工参”等任务；需注意创建方式、AtFixedRate/WithFixedDelay 区别、异常处理，以及在 Flink 算子中保存引用并在 `close()` 中关闭，避免线程泄漏。若希望行为清晰、数据一致，建议将该 Map 算子设为 **并行度 1**，并做好 scheduler 的关闭与异常处理。
