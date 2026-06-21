# Flink Checkpoint 分析与优化方案

## 一、当前代码 Checkpoint 存储内容

### 1. Broadcast State（广播状态）
代码中定义了 5 个广播状态描述符：

| 状态名称 | 数据类型 | 说明 |
|---------|---------|------|
| `cmDimMapStateDesc` | `MapStateDescriptor<String, CmDim>` | 4G 电信工参 |
| `cmCorDimMapStateDesc` | `MapStateDescriptor<String, CmCorDim>` | 4G 电信纠偏工参 |
| `cuDimMapStateDesc` | `MapStateDescriptor<String, CuDim>` | 4G 联通工参 |
| `nrCmCorDimMapStateDesc` | `MapStateDescriptor<String, NrCmCorDim>` | 5G 纠偏工参 |
| `nrCmDimMapStateDesc` | `MapStateDescriptor<String, NrCmDim>` | 5G 电联工参 |

这些广播状态存储了从 HDFS 读取的工参数据，会被广播到所有并行实例。

### 2. Kafka Consumer Offset
Flink Kafka Source 自动将消费的 offset 保存到 Checkpoint，用于故障恢复时从断点继续消费。

### 3. File Source 状态
- `cmSource` 使用 `FileSource`，会保存文件读取进度状态

---

## 二、优化方案对比

### 当前方案（Broadcast State）

```java
// 工参数据通过 broadcast 分发
cmDimData.broadcast(cmDimMapStateDesc)
    .process(new BroadcastProcessFunction<>() {...})
```

**特点：**
- 工参数据存储在 **BroadcastState** 中
- 每个 TaskManager 实例都有一份完整的工参数据副本
- Checkpoint 中会保存完整的工参 Map 状态

### 优化方案（Map 本地缓存）

```java
volteStream
    .map(new RichMapFunction<VolteObject, VolteObject>() {
        private Map<String, CmDim> cmDimCache; // 普通成员变量
        
        @Override
        public void open(Configuration parameters) {
            // 从广播数据或HDFS初始化缓存
        }
        
        @Override
        public VolteObject map(VolteObject value) {
            // 直接查本地缓存关联
            CmDim dim = cmDimCache.get(key);
            return value;
        }
    });
```

---

## 三、Checkpoint 大小变化分析

| 方面 | Broadcast State 方案 | Map 缓存方案 |
|------|---------------------|-------------|
| **状态存储位置** | Managed State (Checkpoint) | 堆内存 (非状态) |
| **Checkpoint 内容** | 包含完整工参数据 | 不包含工参数据 |
| **故障恢复** | 从 Checkpoint 恢复工参 | 需要重新加载工参 |
| **内存占用** | 相同（都有副本） | 相同 |

---

## 四、几百MB工参数据的场景分析

### Broadcast 方案的问题

假设工参数据量为 500MB，并行度=100：

| 问题 | 计算 | 结果 |
|------|------|------|
| **Checkpoint 膨胀** | 500MB × 100 并行实例 | **~50GB** |
| **Checkpoint 耗时** | 序列化+写入分布式存储 | **分钟级** |
| **恢复耗时** | 从分布式存储读取 50GB | **分钟级** |

### 优化方案的优势

| 方案 | Checkpoint大小 | Checkpoint时间 | 恢复时间 | 推荐度 |
|------|---------------|---------------|---------|--------|
| **Broadcast State** | ~50GB | 慢（分钟级）| 慢 | ❌ 不推荐 |
| **Map本地缓存** | ~几MB | 快（秒级）| 中等 | ✅ 推荐 |
| **Async外部查询** | ~几MB | 快 | 快 | ✅✅ 最推荐 |

**结论：** 几百MB工参数据时，应避免使用 Broadcast State，改用本地内存缓存或外部查询。

---

## 五、推荐优化代码

### 方案1：Map 本地缓存（推荐）

```java
final SingleOutputStreamOperator<VolteObject> volteConnected = volteStream
    .connect(cmDimData.broadcast())  // 不指定 StateDescriptor
    .process(new BroadcastProcessFunction<VolteObject, CmDim, VolteObject>() {
        
        private Map<String, CmDim> localCache = new HashMap<>();
        
        @Override
        public void processBroadcastElement(CmDim value, Context ctx, Collector<VolteObject> out) {
            // 只更新本地缓存，不写入 BroadcastState
            localCache.put(value.getKey(), value);
        }
        
        @Override
        public void processElement(VolteObject value, ReadOnlyContext ctx, Collector<VolteObject> out) {
            String cellKey = String.join("_", value.getEnodebId(), value.getCellId());
            CmDim dim = localCache.get(cellKey);
            if (dim != null) {
                value.connect(dim);
            }
            out.collect(value);
        }
    });
```

### 方案2：open() 中一次性加载

```java
.open(new RichFunction() {
    private Map<String, CmDim> cmDimCache;
    
    @Override
    public void open(Configuration parameters) {
        // 直接读取 HDFS 文件到 HashMap
        this.cmDimCache = loadCmDimFromHdfs();
    }
    
    @Override
    public VolteObject map(VolteObject value) {
        CmDim dim = cmDimCache.get(key);
        // ...
    }
})
```

---

## 六、总结

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 工参数据 < 100MB | Broadcast State | Checkpoint 开销可接受，恢复简单 |
| 工参数据 100MB~1GB | **Map 本地缓存** | Checkpoint 大小从几十GB降到几MB，恢复时重新加载成本低 |
| 工参数据 > 1GB | Async 外部查询 | 避免内存压力，动态查询 |

**核心原则：**
- Checkpoint 存储的是**需要持久化的状态**（如 Kafka offset、聚合结果）
- 维度表（工参）属于**可重新加载的数据**，不应进入 Checkpoint
- 几百MB数据从 HDFS 重新加载很快，远小于 Checkpoint 序列化/反序列化的开销
