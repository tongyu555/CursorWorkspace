# Spark SQL 性能调优核心知识点总结（面试必备）

Spark SQL 的调优可以系统地分为以下八个核心板块：**资源配置、SQL逻辑、Shuffle、数据倾斜、小文件、存储格式、内存与缓存、Spark 3.x 新特性**。

## 一、 资源配置优化 (Resource Allocation)

资源是性能的基石，合理的资源分配能避免大多数的 OOM 和任务缓慢问题。

- **Executor 内存与 CPU 比例**：
  - `spark.executor.cores`：建议设置为 **2~5**。如果设置为 1，无法利用多线程优势；如果过大（如 >5），会导致同一个 Executor 内的多个 Task 竞争内存和 CPU 线程上下文切换开销过大。
  - `spark.executor.memory`：根据集群资源分配，通常 4G~16G。
- **堆外内存 (Overhead Memory)**：
  - `spark.yarn.executor.memoryOverhead`：默认是 Executor 内存的 10% 或 384MB。当处理复杂 SQL（如大量复杂 UDF、大窗口函数）或遇到 `Yarn kill container (memory limit exceeded)` 时，需适当调大（如 1G 或 20%）。
- **动态资源分配**：
  - ：`spark.dynamicAllocation.enabled=true`根据任务负载自动增减 Executor，提高集群整体资源利用率。

## 二、 SQL 语法与逻辑优化 (SQL Logic & Catalyst)

利用 Spark SQL 底层的 Catalyst 优化器机制，写出更友好的 SQL。

- **列裁剪与谓词下推**：
  - **列裁剪**：只 `SELECT` 需要的字段，坚决避免 `SELECT `*。
  - **谓词下推 (Predicate Pushdown)**：尽早在 `WHERE` 中过滤数据，减少 Join 和 Shuffle 的数据量。Spark 会尽量自动下推，但在某些复杂子查询或特定 UDF 中可能失效，需手动提前过滤。
- **避免笛卡尔积**：
  - 确保 Join 语句中包含有效的 `ON` 条件，否则会触发极其低效的 Cartesian Product。
- **慎用 UDF (User Defined Functions)**：
  - **痛点**：普通的 UDF 对 Catalyst 优化器是“黑盒”，无法进行谓词下推等优化；且 Python UDF 会产生 JVM 与 Python 进程间的序列化通信开销。
  - **优化**：优先使用 Spark 内置函数（Built-in Functions）；如果是 Python，尽量使用 **Pandas UDF (基于 Apache Arrow)** 提升向量化运算性能。
- **使用 CTE (WITH 语句)**：
  - 提高代码可读性。但在 Spark 3.x 之前，CTE 会被内联（展开）多次计算。Spark 3.x 引入了 CTE 缓存机制，可以避免重复计算。

## 三、 Shuffle 优化 (Shuffle Tuning)

Shuffle 是 Spark 中最昂贵的操作（涉及磁盘 I/O、网络传输、序列化）。

- **调整 Shuffle 分区数**：
  - `spark.sql.shuffle.partitions`：默认 200。在处理大数据量时 200 往往太小，导致单个 Task 处理数据量过大甚至 OOM。
  - **经验值**：调整分区数，使每个 Task 处理的数据量在 **100MB~200MB** 之间最为合理。
- **增加 Shuffle Map 端 Buffer**：
  - `spark.shuffle.file.buffer`：默认 32KB。调大（如 64KB/128KB）可以减少 Map 端写磁盘的溢写（Spill）次数。
- **增加 Reduce 端拉取数据的内存限制**：
  - `spark.reducer.maxSizeInFlight`：默认 48MB。调大（如 96MB）可以减少 Reduce 端拉取数据的网络请求次数。

## 四、 数据倾斜调优 (Data Skew) ⭐ 面试最高频

数据倾斜是指个别 Task 处理的数据量远大于其他 Task，导致“长尾效应”（99%的任务完成了，剩下1%跑了几个小时）。

- **现象定位**：Spark UI 中发现某个 Stage 的 Max 耗时远大于 Median 耗时。
- **解决方案 1：过滤异常值**：
  - 如果倾斜是由大量的 `NULL` 值或无意义的空字符串引起，直接在 Join/Group 前过滤掉。
- **解决方案 2：Broadcast Join 绕过 Shuffle**：
  - 如果是一大一小表 Join 倾斜，使用 `/*+ BROADCAST(small_table) */`，将小表广播到各个 Executor，直接将 Reduce Join 转为 Map Join，彻底消除 Shuffle 倾斜。
- **解决方案 3：两阶段聚合（针对 Group By 倾斜）**：
  - **局部聚合 + 全局聚合**：给倾斜 Key 加上随机前缀（Salting）进行第一轮打散聚合，然后再去掉前缀进行第二轮全局聚合。
- **解决方案 4：加盐打散（针对大表 Join 大表倾斜）**：
  - 将倾斜的大表 A 的 Key 加上 1~~N 的随机前缀，将另一张大表 B 的对应行扩容 N 倍（加上 1~~N 的后缀），然后进行 Join。
- **解决方案 5：利用 Spark 3.x AQE**：
  - 开启 `spark.sql.adaptive.skewJoin.enabled=true`，Spark 会自动检测倾斜分区，并将其拆分成多个子分区处理。

## 五、 小文件与文件数优化 (Small Files)

大量小文件会导致 NameNode 内存压力剧增，并在读取时产生大量 Task，引发调度瓶颈。

- **写入前合并（Coalesce vs Repartition）**：
  - `coalesce(n)`：不产生 Shuffle，适用于缩小分区数（如过滤了大量数据后）。
  - `repartition(n)`：产生 Shuffle，适用于扩大分区数或解决数据分布不均。
  - 在 `INSERT OVERWRITE` 之前，通常使用 `DISTRIBUTE BY` 或 `repartition` 控制输出文件数。
- **Spark 3.x AQE 自动合并**：
  - `spark.sql.adaptive.coalescePartitions.enabled=true`：在 Shuffle 结束后，自动合并过小的分区，极大地缓解了小文件问题。
- **控制单文件最大记录数**：
  - `spark.sql.files.maxRecordsPerFile`：限制写入单个文件的最大条数，防止产生超大文件。

## 六、 存储格式与压缩优化 (Storage & Compression)

- **首选列式存储 (Columnar Storage)**：
  - **Parquet / ORC**：Spark 极度偏爱 Parquet。列式存储天然支持**列裁剪**和**谓词下推**，且同列数据类型一致，压缩比极高。
- **压缩算法选择**：
  - `spark.sql.parquet.compression.codec`：默认是 **Snappy**，在压缩率和 CPU 消耗之间取得了极好的平衡。
  - 在 Spark 3.x 中，对于冷数据归档，推荐使用 **Zstandard (ZSTD)**，压缩率更高且解压速度极快。

## 七、 内存与缓存优化 (Memory & Cache)

- **统一内存管理模型**：
  - `spark.memory.fraction`：默认 0.6。控制 Execution 内存（用于 Shuffle、Join、Sort）和 Storage 内存（用于 Cache、Broadcast）的总占比。
  - 如果代码中不需要 Cache 数据，可以适当调大该值或调整 `spark.memory.storageFraction`（默认 0.5），给 Execution 留出更多内存，减少 Spill 到磁盘的概率。
- **中间结果复用 (Cache / Persist)**：
  - 如果一个 DataFrame/Table 被多次 Action 触发计算，务必使用 `CACHE TABLE` 或 `df.persist(StorageLevel.MEMORY_AND_DISK)` 缓存中间结果。
- **广播变量 (Broadcast Variables)**：
  - 除了 Broadcast Join，在代码中如果用到外部的小字典数据（如 IP 库、配置表），应将其封装为 Broadcast 变量下发，避免每个 Task 拷贝一份导致 OOM。

## 八、 Spark 3.x 核心新特性 (Spark 3.x Features) ⭐ 提分项

在面试中主动提到 Spark 3.x 的特性，会极大提升你的技术深度评分。

- **AQE (Adaptive Query Execution, 自适应查询执行)**：
基于运行时（Runtime）真实的统计信息来动态调整执行计划，主要包含三大特性：
  1. **动态合并 Shuffle 分区**：解决分区数设置不合理导致的小文件或 Task 过多问题。
  2. **动态切换 Join 策略**：如果 Shuffle 阶段发现某张表过滤后变得很小，会自动将 Sort Merge Join 降级为性能更高的 Broadcast Hash Join。
  3. **动态优化倾斜 Join**：自动拆分倾斜的数据块。
- **DPP (Dynamic Partition Pruning, 动态分区裁剪)**：
  - 在星型模型（事实表 Join 维度表）中，Spark 会在运行时将维度表的过滤条件（如 `date = '2023-01-01'`）动态提取出来，下推到事实表的扫描阶段，直接裁剪掉不需要的分区目录，极大幅度减少 I/O。

---

### 💡 面试答题小技巧：

当面试官问：“你是如何进行 Spark SQL 调优的？”
**不要**直接背参数！**要采用 STAR 法则（情境、任务、行动、结果）**：

> "在我们的业务中，最常遇到的是**数据倾斜**和**小文件**问题。
> 比如在做用户行为日志与维表 Join 时，由于某些默认值（如未登录用户的 ID 为 0）导致严重倾斜。我首先通过 Spark UI 定位到长尾 Task，然后采取了**两步走**的策略：第一步，在 SQL 层面过滤掉无效的空值；第二步，对于依然倾斜的热点 Key，我使用了加盐（Salting）打散的局部聚合+全局聚合策略。同时，为了避免落盘产生大量小文件，我开启了 Spark 3.x 的 AQE 特性动态合并分区。最终将该任务的执行时间从 2 小时优化到了 15 分钟。"

