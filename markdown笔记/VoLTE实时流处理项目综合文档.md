# Flink VoLTE 实时流处理项目综合文档

> 本档整合了 VoLTE 信令实时处理程序的学习笔记与项目开发指引，全面涵盖了项目架构、数据流向、核心逻辑实现、代码结构以及二次开发指南，适合学习 Flink 流处理技术及进行项目维护。

---

## 一、 项目概述与业务目标

这是一个基于 Apache Flink 的 VoLTE（Voice over LTE）信令实时处理程序。

### 1.1 业务目标
- **输入**：从 Kafka 读取原始的 VoLTE SIP Gx 信令表数据（按省分表，例如 `dw_volte_sip_gx_input_230000`，CSV 格式）。
- **处理**：按 `enodebId + cellId`（或 5G 的标识）关联 4G/5G 的工参维度数据（包含小区级经纬度、省市区、标准化区划等），并对 4G 数据进行硬编码补全。同时区分处理 4G 和 5G 信令。
- **输出**：
  - **Kafka**：关联处理后输出到 `dw_volte_sip_gx_result_<provincecode>`，供下游实时消费。
  - **HDFS / viewfs**：按 `p_provincecode / p_date / p_hour` 分区写入 CSV 文件，供离线及后续分析。

### 1.2 核心框架与技术栈
- **处理框架**：Apache Flink（DataStream API 与 Table API / SQL 混编）。
- **连接器**：Kafka Connector（读写 Kafka）、HDFS FileSink / FileSource（操作 Parquet / CSV / GZ）。
- **状态管理**：RocksDB StateBackend 增量检查点（本地/NFS存储）。
- **序列化**：Parquet / Avro / SimpleStringSchema。

---

## 二、 整体架构与数据流

### 2.1 数据流概览

```text
Kafka (dw_volte_sip_gx_input_<省码>)
    │ CSV 格式，| 分隔，SASL 认证
    ▼
Table API: volte_view (过滤 + 字段变换)
    │ procedure_type in (1,9)、msisdn 非空、TAC/ECI/5GNCI 有效、procedure_status=1
    │ type: 0=4G, 1=5G（由 source_5gnci 是否等于 1099511627775 推导）
    ▼
toDataStream → map(Row → VolteObject)
    ▼
ProcessFunction：按 type 分流
    ├─ type=="0" → 主流（4G）
    └─ type!="0" → 旁路 sideOutput（5G）
    │
    ├──────────────────────────────────────┐
    ▼                                      ▼
主流：4G                                   旁路：5G
ConnectLetMapFunction                      ConnectNrMapFunction
(CmDim + CmCorDim + CuDim 内存 Map)         (NrCmDim + NrCmCorDim 内存 Map)
    ▼                                      ▼
VolteObject.hardcode()                     filter(isConnected)
    ▼                                      │
filter(isConnected)                        │
    ▼                                      │
    └──────────────┬───────────────────────┘
                   ▼
            union(4G, 5G)
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   Kafka Sink            HDFS FileSink
(toString())      (toStringAndConnectCode(), 分区按处理时间)
```

### 2.2 核心设计亮点
1. **Flink SQL 与 DataStream 混编**：接入 Kafka 与初步清洗利用 Table API（DDL 注册表和 View），逻辑简洁直观；复杂的分流和外部维度关联利用 DataStream API（ProcessFunction、MapFunction）实现。
2. **旁路输出（Side Output）区分 4G/5G**：避免了建立两套独立的 Source 流，通过 `ProcessFunction` 和 `OutputTag` 实现主流处理 4G，旁路处理 5G。
3. **工参内存静态 Map 定时加载**：考虑到广播状态可能导致 Checkpoint 过大，对于相对较小且更新不频繁的工参数据，直接在 Map 算子的 `open()` 方法中从 HDFS 读入静态 Map，利用 `ScheduledExecutorService` 定时刷新。
4. **双路 Sink 并行写入**：同一合并后的数据流通过 `disableChaining()` 独立调度，分别写入 Kafka 字符串流和 HDFS 分区文件。

---

## 三、 目录与包结构

```text
src/main/java/com/dtsw/flink/center/volteparse/
├── Volte.java                     # 主入口：参数解析、Env、Source/Sink、4G/5G 链路
├── demo/                          # 本地/测试用（VolteTest、TtlTest 等）
├── function/
│   ├── ConnectLetMapFunction.java # 4G：关联 CmDim、CmCorDim、CuDim
│   └── ConnectNrMapFunction.java  # 5G：关联 NrCmDim、NrCmCorDim
├── object/
│   ├── VolteObject.java           # 主业务 POJO：从 Row 构造、connect()、toString()
│   ├── AbstractDim.java           # 工参基类（cellKey、省市区等字段）
│   ├── CmDim.java, CmCorDim.java, CuDim.java   # 4G 工参实体
│   ├── NrCmDim.java, NrCmCorDim.java           # 5G 工参实体
│   └── CityDim.java, CityConfig.java 等         # 城市与配置维度
├── source/
│   └── HdfsCsvSource.java         # 已废弃的 HDFS CSV Source
└── utils/
    ├── SetHdfsCmCu.java           # 核心：从 HDFS 加载工参到静态 Map（支持 Parquet/CSV/GZ）
    ├── HdfsFileReadUtils.java     # 文件读取工具类
    ├── StringUtil.java            # 字符串处理工具
    ├── UDFDefaultRollingPolicy.java       # 文件 Sink 按大小/时间滚动策略
    └── UDFDefCheckpointRollingPolicy.java # 按 Checkpoint 的滚动策略
```

---

## 四、 核心处理逻辑与关键实现

### 4.1 环境配置和初始化
配置包含开启 Checkpoint、对象重用以及适合大状态的 RocksDB 状态后端：
```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.setRestartStrategy(RestartStrategies.failureRateRestart(5, Time.minutes(3), Time.minutes(1)));
env.enableCheckpointing(30000L, CheckpointingMode.AT_LEAST_ONCE);
// 开启对象重用，降低 GC 压力
env.getConfig().enableObjectReuse();

// 配置RocksDB状态后端并优化机械硬盘高内存使用
EmbeddedRocksDBStateBackend backend = new EmbeddedRocksDBStateBackend(true);
backend.setPredefinedOptions(PredefinedOptions.SPINNING_DISK_OPTIMIZED_HIGH_MEM);
env.setStateBackend(backend);
// Checkpoint存储路径配置：使用本地NFS
env.getCheckpointConfig().setCheckpointStorage("file:///data12/nfs/flink/storage/volte" + provincecode);
```

### 4.2 数据源接入：Kafka + Table API
通过 Flink SQL 接入数据并进行清洗：
```java
// 注册 Kafka DDL 并添加 WATERMARK
tableEnv.executeSql("CREATE TABLE dw_volte_sip_gx_input_" + provincecode + " (...) WITH (...)");

// 业务清洗规则：提取字段，过滤 procedure_type 等
tableEnv.executeSql("create view volte_view AS select ... from dw_volte_sip_gx_input_" + provincecode + " where ...");

// 转换为 DataStream
SingleOutputStreamOperator<VolteObject> volteStream = tableEnv
    .toDataStream(tableEnv.from("volte_view"))
    .map((MapFunction<Row, VolteObject>) VolteObject::new);
```
> **设计特点**：源数据与写入数据共用一个 Kafka 集群，认证方式为 `SASL_PLAINTEXT` / `SCRAM-SHA-256`，减少了跨集群网络开销。

### 4.3 4G/5G 信令分流处理
利用 `ProcessFunction` 和旁路输出区分业务流：
```java
OutputTag<VolteObject> sideOutput = new OutputTag<VolteObject>("sideOutput"){};
SingleOutputStreamOperator<VolteObject> volteStream_main = volteStream.process(
    new ProcessFunction<VolteObject, VolteObject>() {
        @Override
        public void processElement(VolteObject value, Context ctx, Collector<VolteObject> out) {
            if ("0".equals(value.getType())) out.collect(value);   // 4G → 主流
            else ctx.output(sideOutput, value);                    // 5G → 旁路
        }
    });
DataStream<VolteObject> sideStream = volteStream_main.getSideOutput(sideOutput);
```

### 4.4 维度表关联机制：静态 Map 加载与定时刷新
与常规的广播状态（BroadcastState）不同，本项目工参维度关联通过 **定时刷新内存静态 Map** 实现，有效避免了 Checkpoint 状态膨胀。
- **4G 链路 (`ConnectLetMapFunction`)**：在 `open()` 中调用 `SetHdfsCmCu` 加载 HDFS 的 4G 粗工参、纠偏工参和联通工参，建立 `cellKey` 索引。在 `map()` 中进行查找和字段回填，调用 `hardcode()` 硬编码补全，并过滤出成功关联的数据 (`isConnected()`)。
- **5G 链路 (`ConnectNrMapFunction`)**：机制类似，加载 5G 工参和纠偏工参。
- **数据结构 `VolteObject`**：内部包含 `connect(AbstractDim dim)` 方法来回填经纬度与区划，并叠加 `connectCode` 标识数据关联了哪些维度；提供 `toStringAndConnectCode()` 等格式化输出。

### 4.5 数据输出双 Sink：Kafka + HDFS
关联完成后的 4G 与 5G 流通过 `union` 合并，同时输出至两端：
- **Kafka Sink**：序列化为字符串输出，启用压缩并配置较大的缓冲及容错机制。
- **HDFS FileSink**：以 CSV 形式写入 HDFS，按 `p_provincecode / p_date / p_hour` 基于 **处理时间** 分区，并采用自定义滚动策略（如：5分钟无写入滚动、最大100MB滚动）。

---

## 五、 部署、运行与监控

### 5.1 启动参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `provincecode` | 必填。省份代码，决定 Topic 名、工参路径和 Checkpoint 目录。 | `230000` |
| `parallelism`  | 必填。作业并行度。 | `5` |
| `interval`     | 选填。工参定时刷新间隔（毫秒）。 | `21600000`（6小时） |
| `OpenExpiredTime`| 选填。是否开启工参的过期时间过滤判断。 | `false` |

### 5.2 运行命令示例 (`runVolte.sh`)
生产采用 YARN Application 模式（保障资源隔离）：
```bash
/usr/local/flink/bin/flink run-application -t yarn-application \
-Dtaskmanager.numberOfTaskSlots=1 \
-Djobmanager.memory.process.size=4096m \
-Dtaskmanager.memory.process.size=6144m \
-Dyarn.application.name="Flink-Volte-4G-${provincecode}-"$(date "+%Y-%m-%d_%H_%M_%S") \
-c com.dtsw.flink.center.volteparse.Main \
/home/dtsw/zyt/volte_streaming/dtswfink-center-volteparse-3.4.jar provincecode=${provincecode} parallelism=${parallelism}
```

### 5.3 监控与性能优化
1. **监控指标**：通过 Flink Web UI 重点关注 Checkpoint 的持续时间与状态大小，以及上游 Kafka Source 的消费延迟和反压。
2. **并行度与内存**：工参内存 Map 在 TaskManager 级别是单例。若 TaskManager 内运行多个 Subtask 会复用一份内存，大量节省资源；启用 `enableObjectReuse` 以降低大吞吐下的 GC 开销。
3. **容错与状态**：合理配置超时 (`300000L`) 和最大连续失败次数 (`2`) 应对瞬时网络抖动导致的 Checkpoint 失败。

---

## 六、 二次开发与扩展指引

1. **修改或增加清洗过滤条件**：
   直接修改 `Volte.java` 中 `regisTables()` 方法里的 SQL View（`volte_view`）的 `WHERE` 或 `SELECT` 子句即可；若涉及新字段，需同步调整 `VolteObject` 实体类的构造与格式化方法。
2. **新增一种工参维度**：
   - 继承 `AbstractDim` 创建实体类。
   - 在 `SetHdfsCmCu.java` 中增加解析读取逻辑并维护新的静态 ConcurrentHashMap。
   - 在对应的 `MapFunction` 的 `open()` 中注册定时刷新任务，在 `map()` 中实现查找逻辑并调用 `connect()` 回填。
3. **更换工参数据源 (如换为 API 或 DB)**：
   只需重写 `SetHdfsCmCu` 中“拉取 → 填充静态 Map”的逻辑。底层基于定时任务驱动刷新机制，整体流处理架构不受影响。
4. **修改数据 Sink**：
   在最后 `.union()` 操作后，可自由扩展 `.sinkTo(...)` 或 `.addSink(...)`。对于 HDFS 路径更改，可调整 `BucketAssigner` 分配逻辑。

---

## 七、 学习要点总结

通过本项目可以深入掌握以下 Flink 核心知识：
- **Flink DataStream 与 Table API 的丝滑互转混编**，利用 SQL 的易用性与 DataStream 的高自定义控制能力。
- **状态管理策略选型**：学习在面对庞大且准静态的维表数据时，如何通过 `ConcurrentHashMap` 加定时线程替代 BroadcastState，从而大幅优化 Checkpoint 的耗时与体积。
- **容错与一致性保障**：了解 Kafka 结合 RocksDB Checkpoint 及 FileSink 如何实现端到端的 At Least Once 甚至 Exactly Once 数据处理。
- **复杂流分流与合流**：灵活应用 `ProcessFunction`（Side Output 旁路输出）与 `union()` 对不同业务数据的差异化分流处理与合并统一输出。
