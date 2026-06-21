# ConnectNrMapFunction 定时加载工参问题分析

## 当前实现简述

- 在 `open()` 里：先同步加载一次工参到 `SetHdfsCmCu` 的静态 Map，再把本地的 `nrCmDimMap` / `nrCmCorDimMap` 引用指向这两个静态 Map，然后启动一个 **ScheduledExecutorService**，按 `intervalGetFile`（毫秒）周期执行：
  - `SetHdfsCmCu.setNrCmDimMap(...)`、`SetHdfsCmCu.setNrCmCorDimMap(...)`
  - 再执行 `nrCmDimMap = SetHdfsCmCu.nrCmDimMap`、`nrCmCorDimMap = SetHdfsCmCu.nrCmCorDimMap`（引用未变，可省略）
- `map()` 只读这两个 Map，不做写操作。

---

## 问题一：ScheduledExecutorService 未关闭，导致线程泄漏

- **现象**：`open()` 中 `Executors.newScheduledThreadPool(1)` 创建了调度线程池，但**没有保存引用**，也**没有重写 `close()`**。Flink 在算子关闭（cancel、失败、作业结束）时不会自动关闭这个线程池。
- **后果**：任务结束后调度线程仍存在，造成**线程泄漏**；若作业频繁启停，线程数会累积。
- **建议**：将 `ScheduledExecutorService` 存为成员变量，在 `RichMapFunction` 的 **`close()`** 中调用 `shutdown()`/`shutdownNow()` 并做适当 `awaitTermination`。

---

## 问题二：定时任务内异常未处理，失败不可见且易导致状态不一致

- **现象**：定时执行的 lambda 中直接调用 `setNrCmDimMap` / `setNrCmCorDimMap`，若 HDFS 超时、路径不存在、解析异常等，会抛出 `RuntimeException`。ScheduledExecutorService 会吞掉任务抛出的异常，只打印到 stderr，**不会重试、不会告警**，业务侧难以感知。
- **后果**：某次加载失败后，静态 Map 可能处于“只更新了 NrCmDim 或只更新了 NrCmCorDim”的**半更新状态**，或维持旧数据；若之前已讨论过“先 clear 再 put”的改动，未 clear 时还会出现新旧数据混杂。
- **建议**：在定时任务 lambda 内 **try-catch**，失败时打 error 日志、上报监控或置标志位；若需要“全量替换才生效”，可改为先加载到临时 Map，成功后再整体替换或先 clear 再 put，避免半更新。

---

## 问题三：reload 时静态 Map 未清空，存在旧数据残留与语义混乱

- **现象**：`SetHdfsCmCu.setNrCmDimMap` / `setNrCmCorDimMap` 当前实现是**直接往静态 Map 里 put**，没有在本次加载前 **clear()**。
- **后果**：
  - 若某次 HDFS 列表或读取不完整（如 viewfs 只返回部分文件），新数据条数变少，旧 key 仍留在 Map 里，会出现“部分小区用旧工参、部分用新工参”的不一致。
  - 若工参中某 cellKey 在新数据里被删除（下线小区），不 clear 会一直保留旧记录，无法体现“已下线”。
- **建议**：在 `setNrCmDimMap` / `setNrCmCorDimMap` 中，在本次 `put` 之前对对应静态 Map 执行 **clear()**（或先装到临时 Map，成功后再 clear + putAll），保证每次 reload 都是“全量替换”语义。

---

## 问题四：并行度 > 1 时多实例并发写同一静态 Map

- **现象**：若该 Map 算子并行度大于 1，每个 subtask 的 `open()` 都会启动自己的定时任务，**多个线程周期性地对 `SetHdfsCmCu.nrCmDimMap` / `nrCmCorDimMap` 这两个静态 Map 执行 put**（且当前实现无 clear）。
- **后果**：之前已出现过“同一 reload 周期内两次加载条数不一致（如约 14 万 vs 7 万）”的现象，与 viewfs listStatus 非确定性 + 多实例并发写同一 Map 有关；且多实例重复拉同一路径，浪费 HDFS 与 CPU。
- **建议**：该算子**设为并行度 1**（例如 `.setParallelism(1)`），保证全集群只有一处加载/更新 5G 工参；若必须多实例，应改为“单实例加载 + 广播”或“外部存储/服务 + 单点更新”，避免多实例同时写静态 Map。

---

## 问题五：intervalGetFile 为 0 时调度行为异常

- **现象**：若构造时传入 `intervalGetFile = 0`，`scheduleAtFixedRate(..., 0, 0, TimeUnit.MILLISECONDS)` 会以**极短周期**（约 0ms）反复执行。
- **后果**：HDFS 与 JVM 会被频繁调用，可能打满 HDFS 连接、CPU，甚至 OOM（每次加载大量对象）。
- **建议**：在 `open()` 中对 `intervalGetFile` 做校验，若 `<= 0` 则抛异常或设为合理下限（如 60_000 ms），避免 0 周期。

---

## 问题六：加载耗时长于周期时的调度堆积

- **现象**：`scheduleAtFixedRate` 的语义是“按固定周期触发”；若单次执行时间超过 `intervalGetFile`（例如 HDFS 慢、数据量大），下一次会在**上一次执行完成后**立即被调度，不会并发执行（单线程池），但会出现“连续执行、无间隔”的堆积。
- **后果**：周期被拉长、HDFS 压力集中，若持续慢于间隔，会形成“刚跑完又跑”的链式调用。
- **建议**：若更关心“两次加载之间间隔至少 N 毫秒”，可改用 **`scheduleWithFixedDelay`**（上次结束到下次开始的间隔）；或在任务内记录开始时间，若本次执行超过一定时长则打告警，便于发现 HDFS 或集群问题。

---

## 问题七：map() 与定时任务的可见性（相对安全）

- **说明**：`nrCmDimMap` / `nrCmCorDimMap` 引用的是 `SetHdfsCmCu` 的静态 Map，定时任务只更新静态 Map 内容，不替换引用；`map()` 读的是同一引用。**ConcurrentHashMap** 的 put/get 本身有 happens-before 保证，因此**对已 put 的条目**，map() 能读到更新，不存在“永远看不到新数据”的可见性问题。但若 reload 时先 clear 再 put，在 clear 与 put 完成之间，map() 可能读到空或部分数据，若要求“要么全旧要么全新”，需要把“全量新数据”先准备好再一次性替换（例如用 volatile 引用指向新 Map 或做一次性 clear + putAll）。

---

## 小结与建议优先级

| 优先级 | 问题 | 建议 |
|--------|------|------|
| 高 | 线程泄漏 | 保存 Scheduler 引用并在 close() 中 shutdown |
| 高 | 多实例写静态 Map | 该算子 setParallelism(1) 或改为单点加载+广播 |
| 高 | reload 未 clear | 在 setNrCmDimMap/setNrCmCorDimMap 中先 clear 再 put |
| 中 | 定时任务异常 | 定时任务内 try-catch，失败打日志/告警，避免静默失败 |
| 中 | interval=0 | open() 中校验 intervalGetFile 下限 |
| 低 | 加载时间超过周期 | 视需求改用 scheduleWithFixedDelay 或加执行时长监控 |

按上述顺序整改后，定时加载工参在生命周期、一致性、可观测性上会更安全、可控。
