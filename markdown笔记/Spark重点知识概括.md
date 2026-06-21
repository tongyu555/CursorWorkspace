# Spark 重点知识复习（体系化梳理）

> 基于 `test1` 复习稿整理，并补充 Spark 3.x / 生产实践要点。偏 RDD 1.x 的表述在文中标注「演进说明」。

---

## 1. RDD 与 Spark 核心思想

### 1.1 什么是 RDD

- **弹性（Resilient）**
  - 优先内存；内存不足可落盘。
  - **容错**：通过 **血缘（Lineage）** 与 **宽窄依赖** 决定重算范围——窄依赖往往只需重算部分父分区。
- **分布式（Distributed）**
  - RDD 由多个 **Partition** 组成；每个分区对应一个 **Task**，可在不同节点并行执行。

### 1.2 Spark 程序在算什么

- 开发本质是描述 **RDD（或后续 DataFrame/Dataset）的依赖关系**。
- 依赖图经 **DAGScheduler** 切分为多个 **Stage**：**遇到宽依赖（Shuffle）** 就会切出新 Stage。

**补充（重要）**

- 现代项目以 **Spark SQL / DataFrame** 为主，底层仍会生成 RDD 级 DAG，但业务侧少直接写 RDD。
- **Structured Streaming** 是流处理的主流 API，与旧版 **DStream** 并存，新项目优先学 Structured Streaming。

---

## 2. 与 Hadoop / MapReduce 的对比


| 维度           | 要点（原文归纳）                                | 补充                                                            |
| ------------ | --------------------------------------- | ------------------------------------------------------------- |
| 与 HDFS       | Spark 常替代 **MR 计算层**，一般不替代 **HDFS 存储**  | 也可接 S3、OSS 等                                                  |
| 集群管理         | 有 **Standalone**；企业常用 **YARN / K8s**    | K8s 在云原生场景很常见                                                 |
| 窄依赖          | 各分区可独立算，不必等其它分区                         | 仍受资源调度影响                                                      |
| Shuffle / 排序 | MR 常强排序；Spark 可按需排序，聚合更多在内存/Shuffle 中完成 | Spark 3 **AQE** 可动态优化 Join/倾斜                                 |
| 落盘           | MR 多阶段写盘；Spark Shuffle 仍涉及磁盘/网络（视配置与版本） | **ESS（External Shuffle Service）**、本地磁盘与 `spark.local.dir` 很重要 |
| 复用           | 可 **cache/persist** 复用中间结果              | 注意 **StorageLevel** 与 **内存+磁盘** 策略                            |
| 资源粒度         | MR 多进程；Spark Executor 内多 **Task 线程**    | Executor OOM、GC 会拖慢整批 Task                                    |


---

## 3. Spark 任务启动链路（概念版）

原文：`driver → master → worker → executor → driver → task → executor`

**更贴近当前术语的表述：**

- **Driver**：解析程序、生成 DAG、调度 Stage、跟踪 Task。
- **Cluster Manager**：Standalone / **YARN ResourceManager** / K8s 等，负责资源分配。
- **Executor**：真正执行 Task，持有 block 缓存、Shuffle 读写等。

**补充**

- **YARN cluster 模式**：Driver 跑在 **ApplicationMaster** 进程内。
- **client 模式**：Driver 在提交机，适合调试但可能占满本机带宽。

---

## 4. RDD 里存的是「真数据」吗？

- **不是实体数据本身**，而是 **分区规划 + 血缘 + 如何读数据源** 的抽象。
- 实际数据在 **HDFS / HBase / 对象存储** 等；Task 到各节点 **拉取或本地读** 对应 Split/Region。

**分区来源（原文）**

- **HDFS**：类似 `FileInputFormat#getSplit` 思想，通常 **与块大小相关**（具体还受 `maxPartitionBytes` 等影响）。
- **HBase**：Region 级划分，与 **TableInputFormat** 一类思路对应。

**补充**

- DataFrame 读 Parquet/ORC 时，分区数还受 `spark.sql.files.maxPartitionBytes` 等参数影响。

---

## 5. 宽窄依赖与 Shuffle

### 5.1 定义（原文口径）

- **宽依赖**：会产生 **Shuffle**（跨分区、按 key 重分布，经网络或本地 shuffle 服务）。
- **窄依赖**：除宽依赖外，多为 **一对一 / 窄范围** 依赖，可 **流水线** 合并。

### 5.2 容错差异

- **宽依赖**：失败时可能需 **重算多条父分区**（视血缘与 checkpoint）。
- **窄依赖**：常只需 **重算对应父分区**。
- **Stage 边界**：**宽依赖处** 切 Stage。

### 5.3 数据本地化

- **移动计算，不移动数据**：尽量把 Task 调度到 **数据所在节点**（PROCESS_LOCAL / NODE_LOCAL / RACK_LOCAL …），减少网络 IO。

**补充**

- Spark 3 中 **AQE**、**动态分区合并** 等会改变 Shuffle 与分区形态，但「宽依赖 ≈ Shuffle」仍成立。

---

## 6. Transformations 与 Actions

### 6.1 典型分类（原文）

- **Transform**：`map`、`filter`、`flatMap`、`groupBy`、`join`、`union`、`distinct` …
- **Action**：`count`、`collect`、`foreach`、`reduce`、`first`、`take`、`saveAsTextFile` …

### 6.2 `reduceByKey` vs `groupByKey`（原文重点）

- `**reduceByKey`**：可在 **Map 端做预聚合（combiner）**，Shuffle 量通常更小。
- `**groupByKey` + map**：往往 **全量拉取 value**，网络与内存压力大，一般更慢。
- **语义**：`groupByKey` 后你能拿到 **key**；`reduceByKey` 直接得到 **聚合后的 value**（拿不到未聚合的每组全量列表）。

**补充**

- DataFrame 侧多用 `**groupBy` + `agg`**；注意 `**distinct` / 大 Join** 也会引入 Shuffle。

### 6.3 `coalesce` vs `repartition`


| 算子                | 行为要点                                                                        |
| ----------------- | --------------------------------------------------------------------------- |
| `**repartition`** | 一般 **会 Shuffle**，适合 **增加分区** 或 **强烈打乱数据**（均衡）。                              |
| `**coalesce`**    | 可 **不 Shuffle** 地 **减少分区**（窄依赖合并）；**剧降分区**（如 1000→1）易导致 **单 Task 过大、单点瓶颈**。 |


**其它调分区方式（原文）**

- 部分算子可指定分区数；`**spark.default.parallelism`**（RDD）；SQL 侧常用 `**spark.sql.shuffle.partitions**`（默认 200，生产常需调大或配合 AQE）。

### 6.4 `mapPartitionsWithIndex`

- 可拿到 **分区索引**，用于 **按分区写文件**、自定义分片逻辑等。

### 6.5 `checkpoint` vs `cache`


|          | **checkpoint**            | **cache/persist**             |
| -------- | ------------------------- | ----------------------------- |
| 存储       | 常落 **HDFS** 等可靠存储         | 多在 **Executor 内存**，可溢写磁盘（视级别） |
| 是否触发 Job | **会**（物化计算）               | 遇 Action 且未命中时才计算并缓存          |
| 血缘       | **截断血缘**（从 checkpoint 重算） | **不截断**，仍保留 lineage 做容错       |


### 6.6 `cache` vs `persist`

- `**cache`** ≈ `persist(MEMORY_ONLY)` 的便捷写法。
- `**persist(LEVEL)**` 可选 **MEMORY_AND_DISK**、**DISK_ONLY**、**序列化** 等。

### 6.7 `collect` 与 Action 运行位置（原文）

- `**collect`**：把各 Executor 结果 **拉回 Driver**，数据量过大易 **OOM / 卡死**。
- 适合小结果集或调试。
- 原文：**只有传到算子里的闭包函数在 Executor 上执行**（Streaming 里 `foreachRDD`/`transform` 等需单独理解）。

**补充**

- Driver 上避免对大 RDD 做 `collect`；写库可用 `**foreachPartition`** + 连接池。

---

## 7. 共享变量

### 7.1 广播变量（Broadcast）

- Driver 创建，**一次性** 下发到各 Executor，**只读**。
- 用于 **小表 Join / 配置表**，等价思想接近 MR 的 **DistributedCache / Map-side join**。
- 避免在 Task 中反复 **序列化大对象**。

**补充**

- Spark SQL 的 **Broadcast Hash Join** 会自动广播小表（受 `spark.sql.autoBroadcastJoinThreshold` 等约束）。

### 7.2 累加器（Accumulator）

- Task 内累加，**Driver 汇总**；适合 **计数、监控**。
- **不要用** 普通闭包变量在 map 里做全局累加——**不会回传到 Driver**（除非用累加器）。

**补充**

- Spark 3 推荐 `**AccumulatorV2`**；注意 **只应 add，不要在 Task 里读最终值**（Task 侧可能不准）。

---

## 8. BlockManager 与存储

- **BlockManagerMaster（Driver）**：块元数据、调度与本地化相关。
- **BlockManager（Executor）**：管理 **内存/磁盘** 块、**Shuffle 读写**、拉取远程块等。

---

## 9. Executor 内存与 GC

### 9.1 Executor 内存模型（原文 + 演进）

- 老版本有 **静态划分**（storage/execution）；**1.5+** 后默认 **统一内存管理（Unified Memory）**，可互相借用。
- 可通过 `**spark.memory.useLegacyMode`** 切回旧模式（一般不推荐）。

### 9.2 何时调内存

- 几乎 **不 cache** 时，可适当让 **执行内存** 更充裕（结合统一内存机制理解，而非简单「关掉 cache 区」）。

### 9.3 JVM GC（原文新生代/老年代流程）

- 控制 **频繁 new 大对象**，减少 **Full GC** 导致的 **Shuffle 停顿**。
- 生产上结合 **G1/ZGC**、**堆外内存（off-heap）**、**Kryo** 等一并看。

---

## 10. Shuffle 优化（原文要点 + 补充）

原文条目整理：

1. **Consolidation / 文件合并**：减少 Map 端小文件（老参数 `spark.shuffle.consolidateFiles`；新版本实现已演进，以 **Shuffle 架构 + ESS** 为主）。
2. **重试**：`spark.shuffle.io.maxRetries`、`spark.shuffle.io.retryWait`。
3. **缓冲**：`spark.shuffle.file.buffer`、`spark.reducer.maxSizeInFlight`（注意过大占内存）。
4. **减少数据量**：**Kryo**、**Shuffle 压缩**（如 lz4/snappy/zstd）。
5. **算子选择**：**预聚合** 类优于全量 group。
6. **减少对象分配**：降低 GC 对 Shuffle 的影响。

**重要补充**

- `**spark.sql.shuffle.partitions`**、**AQE**（`spark.sql.adaptive.enabled`）、**倾斜处理（skew join hint / AQE）**。
- **磁盘与网络**：Executor 本地盘要快、`spark.local.dir` 勿用慢盘。

---

## 11. 自定义 Key 与序列化

- 作为 **Shuffle 的 Key**：需 `**Serializable`** + `**Comparable**`（或提供 **Ordering**）。
- **Value**：至少 `**Serializable`**。
- **排序**：与 Java `compare` 思想一致。
- **序列化**：**Kryo** 更小更快，但需 **注册类**；Java 序列化兼容广但慢。

---

## 12. Spark 访问 HBase（原文模式归纳）

**写：**

1. 每分区建连接、逐条写（慢）。
2. 每分区建连接、**批量写**（快）。
3. `**TableOutputFormat`**：连接可复用。

**读：**

- `**TableInputFormat` + Scan**：`setCaching`、`setCacheBlocks(false)` 等控制批量与缓存。

**大批量导入：**

- **BulkLoad：生成 HFile + bulk load**（与 MR 思路一致，吞吐高）。

---

## 13. Spark on YARN

### 13.1 Jar 分发

- 各节点从 **HDFS 目录** 取依赖，**不必每台装 Spark**。
- **推荐**：`spark-defaults.conf` 配 `**spark.yarn.jars`**（或 `**spark.yarn.archive**`），**预先上传**；避免每次提交重复上传。

### 13.2 `yarn-client` vs `yarn-cluster`


| 模式          | 特点                                                      |
| ----------- | ------------------------------------------------------- |
| **client**  | Driver 在客户端，日志直观；**Driver↔Executor 流量大**，易打满网卡，适合调试     |
| **cluster** | Driver 在集群内，适合生产；日志用 **YARN / Spark History Server** 查看 |


---

## 14. Spark SQL

### 14.1 能否替代 Hive？

- **大部分可替代**：元数据、SQL、窗口函数、UDF、ThriftServer 等。
- **部分 DDL/方言** 可能与 Hive 不完全一致，需实测。

### 14.2 运行形态（原文）

1. 独立 Spark SQL 环境（数据共享弱）。
2. **共享 ThriftServer**（类似 HiveServer2，多会话共享）。

### 14.3 Catalyst 优化器（原文「六步」的规范表述）

1. **解析（Parse）** → 抽象语法树
2. **绑定/分析（Analyze）** → 列、表、类型校验
3. **逻辑优化（Logical Optimization）** → 谓词下推、列裁剪、常量折叠等
4. **物理规划（Physical Planning）** → 选 Join、选扫描方式
5. **代码生成（Whole-Stage Codegen）**（若启用）
6. **执行**

### 14.4 DataFrame / Dataset / RDD


|      | RDD | DataFrame          | Dataset |
| ---- | --- | ------------------ | ------- |
| SQL  | 否   | 是                  | 是       |
| 类型安全 | 弱   | **Row**（弱）         | **强类型** |
| 关系   | —   | 可视为 `Dataset[Row]` | 泛型 DS   |


- **互转**：`rdd.toDF()`、`spark.createDataFrame(rdd)`、`df.rdd` 等；需 `**import spark.implicits._`**（`spark` 为 `SparkSession` 变量名）。

**原文补充点**

- **默认 shuffle 分区**：SQL 侧常提 `**spark.sql.shuffle.partitions`（默认 200）**。
- **cache 存储级别**：DF/DS 的 `cache` 实际仍基于执行计划缓存/物化策略，理解时以 **StorageLevel + 触发 Action** 为准。

---

## 15. Spark Streaming（DStream）与流式补充

### 15.1 本质（原文）

- **微批（Micro-batch）**：按批次将流拆成 **小 RDD**（DStream），底层仍是 Spark Core。
- **不是逐条超低延迟** 的「纯流」（与 Flink 单条流对比时常这么说）。

### 15.2 与 RDD 相似的 API + 特殊算子

- `**updateStateByKey`**：有状态；通常要 **checkpoint + StreamingContext.getOrCreate**。
- **Window**：**窗口长度、滑动间隔、批次间隔** 需成合理倍数关系；**滑动间隔 ≤ 窗口长度**，否则易丢数据。
- `**foreachRDD` / `transform`**：把 DStream 转成 **每批 RDD**，便于接 **Spark SQL**；`foreachRDD` 为 **输出型**，`transform` 返回新 DStream。

### 15.3 数据源与 Receiver

- **Socket**：练习。
- **FileStream**：配置热加载等。
- **Kafka**：生产常用。
- **Receiver 模式**：占 Executor 资源；**两个 Receiver 流合并** 时注意 **core 数**。
- **Direct / Kafka 0.10+ Consumer API**：**无 Receiver**，直连分区，一般 **更推荐**。

### 15.4 Offset 管理（原文 + 必补）

- **必须可靠保存 offset**（ZK / Kafka __consumer_offsets / **HDFS/S3 checkpoint** / MySQL / Redis 等）。
- 选择 **高可用存储**，避免与 Kafka 过紧耦合时单点故障。
- **过期 offset**：与 **Kafka 最早可用 offset** 取 **较大者**，避免 **OffsetOutOfRange** 类问题。

**重要补充（考试/面试常考）**

- 新项目优先：**Structured Streaming + Kafka Source**，offset 由 **checkpoint** 与引擎管理，语义更清晰（at-least-once / exactly-once 与 sink 有关）。
- **DStream** 在维护项目中仍会遇到，但新开发应学 **Structured Streaming**。

---

## 16. Kafka 基础（原文体系化）

### 16.1 概念

- **Producer / Consumer / Consumer Group / Broker / Topic / Partition / Offset**
- **同一 Group**：每个 Partition 同一时刻通常只被一个 Consumer 消费；**Consumer 少则一人多读多分区**；**Consumer 多则闲置**。

### 16.2 分区均衡

- **由 Producer 策略决定**：随机、轮询、key hash、自定义 **Partitioner**。

### 16.3 分区数权衡

- **更多分区**：更高并行与吞吐潜力。
- **代价**：更多文件句柄、副本复制与故障恢复成本、可能 **增大端到端延迟**、Consumer 侧元数据/分配开销上升。

**粗算（原文经验）**

- 单分区吞吐量级经验值（视消息大小与业务而定）；再结合 **下游并行度** 定分区数，并留约 **10% 余量** 应对峰值。

### 16.4 参数与运维

- 关注 **buffer、batch、线程、压缩、acks、linger.ms** 等。
- 工具：**CMAK（原 kafka-manager）**、**Kafka UI**、**AKHQ** 等。

### 16.5 API 要点

- **自定义 Partitioner**：实现 **按 key 进固定分区**，辅助 **顺序消费**（单分区有序）。
- **Offset 提交**：`enable.auto.commit` **自动 vs 手动**；与 **重复消费/丢消息** 语义强相关。
- **消费起始**：`earliest` / `latest` 等与 **group 无 offset 时** 的行为要分清。

---

## 17. Spark Streaming + Kafka：直连 vs Receiver（原文）

- **Receiver**：内存缓冲、WAL，资源与安全面更差，新版本趋势是 **淘汰**。
- **Direct（0.8+）/ Kafka 0.10+ 集成**：**直连 Partition**，无 Receiver，**更主流**。

**数据本地化**

- 若 **Streaming 与 Broker 同机**（条件苛刻）可减轻网络；多数情况仍是 **跨机拉取**。

---

## 18. 复习建议（对应原文最后一句）

- **优化专题**：Shuffle、内存、序列化、SQL 执行计划、分区数、AQE —— 反复看 **Spark UI**（Stages、Tasks、Shuffle Read/Write、GC Time）。
- **流式**：在掌握 DStream 的同时，补一套 **Structured Streaming 模型**（Source → 查询 → Sink，checkpoint 与容错）。

---

## 附录：源文件

- 复习原文：`test1`（同目录）

