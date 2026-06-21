# DataX 与 SeaTunnel 架构深度解析与对比

在大数据离线与实时同步领域，DataX 和 SeaTunnel（原 Waterdrop）是两款非常优秀且应用广泛的开源数据集成工具。本文将从架构设计、设计理念、优缺点、适用场景以及任务配置方式等多个维度对两者进行深度解析。

---

## 一、 DataX 深度解析

DataX 是由阿里云开源的一个异构数据源离线同步工具，致力于实现包括关系型数据库、HDFS、Hive、ODPS、HBase、FTP 等各种异构数据源之间稳定高效的数据同步功能。

### 1. 架构设计

DataX 采用典型的 **Framework + Plugin（框架 + 插件）** 架构。

- **Framework（底层框架）**：负责连接 Reader 和 Writer，作为两者的数据传输通道。它处理了缓冲、流控、并发、数据转换等核心技术问题。
- **Plugin（插件）**：
  - **Reader（读插件）**：数据采集模块，负责从源端读取数据并将数据发送给 Framework。
  - **Writer（写插件）**：数据写入模块，负责不断向 Framework 取数据并将数据写入到目的端。
- **运行核心概念**：
  - **Job**：单个数据同步作业。Job 会根据配置被切分成多个 Task。
  - **Task**：最小的具体执行单元，由一个 TaskReader、一个 Channel 和一个 TaskWriter 组成。
  - **TaskGroup**：一组 Task 的集合，负责管理和调度这组 Task。
  - **Channel**：连接 Reader 和 Writer 的内存队列，负责数据的传输和限流。

### 2. 设计理念

- **单机多线程**：DataX 定位于单机执行，通过多线程并发来实现高效的数据同步。
- **全内存流转**：数据在 Reader 和 Writer 之间通过内存 Channel 交换，不落盘，极大提高了传输效率。
- **星型拓扑**：将复杂的 `N x M` 个数据源的同步链路，转化为以 DataX 为中心的星型链路（`N + M`），只要开发对应的 Reader 和 Writer 插件即可实现任意数据源互通。

### 3. 特点优势及不足

- **优势**：
  - **稳定成熟**：经过阿里多年双11的考验，单机性能极佳，非常稳定。
  - **插件丰富**：官方及社区提供了大量针对主流数据库的读写插件。
  - **开箱即用**：部署简单，配置清晰，学习成本极低。
  - **精准的流控**：框架层面提供了通道限流和字节/记录数限流能力，保护上下游数据库不被打垮。
- **不足**：
  - **单机瓶颈**：原生开源版不支持分布式集群部署，无法横向扩展（Scale-Out），海量数据同步受限于单机 CPU 和内存。
  - **缺乏实时支持**：主要定位于离线批量同步，不支持 CDC（变更数据捕获）等实时流式同步。
  - **内存溢出风险**：由于是纯内存交换，配置不当或单条数据过大容易引发 OOM。

### 4. 适用场景

- 传统关系型数据库（如 MySQL、Oracle）与大数据平台（如 Hive、HDFS）之间的**离线全量/增量批量同步**。
- 数据量在中小规模（千万级至单表数亿级），对实时性要求不高的 T+1 数据入仓场景。

### 5. 任务配置方式

DataX 采用 **JSON** 格式进行任务配置。主要包含 `job` -> `setting`（全局配置）和 `content`（读写插件配置）。

```json
{
    "job": {
        "setting": {
            "speed": {
                "channel": 3 // 配置并发数
            }
        },
        "content": [
            {
                "reader": {
                    "name": "mysqlreader",
                    "parameter": {
                        "username": "root",
                        "password": "pwd",
                        "column": ["id", "name"],
                        "connection": [{"jdbcUrl": ["jdbc:mysql://localhost:3306/db"], "table": ["user"]}]
                    }
                },
                "writer": {
                    "name": "hdfswriter",
                    "parameter": {
                        "defaultFS": "hdfs://localhost:9000",
                        "fileType": "text",
                        "path": "/user/hive/warehouse/user",
                        "fileName": "user_sync"
                    }
                }
            }
        ]
    }
}
```

### 6. 生产环境高可用集群构建与实践

在实际生产环境中，由于 DataX 原生开源版仅支持单机运行，缺乏可视化的任务管理、依赖调度以及分布式集群执行能力，通常需要结合开源生态工具或大数据集群管理组件来构建高可用架构。

#### (1) 使用 DataX-Web 构建高可用调度管理集群

**DataX-Web** 是开源社区中专门为 DataX 打造的分布式数据同步可视化系统，极大弥补了 DataX 在调度和管理上的短板。

- **分布式架构设计**：采用类似 XXL-JOB 的 `Admin + Executor` 主从架构。
  - **Admin（调度中心）**：负责可视化的任务配置、任务流编排、Cron 定时调度、报警监控以及将任务分发给底层的执行器。Admin 支持集群部署，通过共用数据库保证高可用，防止调度单点故障。
  - **Executor（执行器）**：负责接收 Admin 下发的任务并真正拉起 DataX 进程执行。可以部署多个 Executor 节点，实现大量 DataX 任务的**分布式并发执行**与**负载均衡**。
- **生产实践优势**：
  - **可视化与零代码**：无需手写易错的 JSON 配置，通过 Web 界面勾选即可完成从源库到目标库的映射配置。
  - **故障转移（Failover）**：当某个 Executor 节点宕机或负载过高时，调度中心能够自动将任务路由到其他健康的节点上执行，保障业务连续性。
  - **集中式监控与日志**：所有节点的执行日志、速率、脏数据情况都可在 Web 端集中查看，运维排错成本极低。

#### (2) 让 DataX 任务跑在 YARN 集群中

DataX 作为纯 Java 进程，如果在一个节点并发运行多个大型同步任务，极易将该节点的 CPU 和内存打满甚至引发 OOM。为了充分利用 Hadoop 集群现有的海量计算资源，通常需要将 DataX 提交到 YARN 集群上执行。

- **上 YARN 的核心目的**：利用 YARN 的 Container 机制提供精准的物理资源（CPU、内存）隔离，实现数据同步计算资源的弹性动态分配和用后即焚。
- **常见的实现方式**：
  - **方式一：借助 Apache DolphinScheduler 等现代大数据调度平台（常见推荐）**
  DolphinScheduler 原生内置了 DataX 任务组件。在生产部署时，通常将其 Worker 节点直接部署在 Hadoop 集群内。通过配置工作组和资源队列，Worker 节点会作为一个代理，安全地拉起 DataX 进程，间接实现了集群资源的充分利用。
  - **方式二：使用 DataX-On-Yarn / 自研 YARN Wrapper 方案**
  开发一个专属的 YARN Client 和 ApplicationMaster，将 DataX 包装成一个纯正的 YARN 任务：
    1. 客户端将 DataX 的 JSON 配置文件提交到 YARN 的 ResourceManager。
    2. YARN 为该任务分配并启动一个 **ApplicationMaster (AM)**。
    3. AM 根据该次同步任务的并发度，向 YARN 申请对应的 Container 资源。
    4. 在分配到的独立 Container 中，拉起标准的 DataX 进程执行具体的数据搬运逻辑。
    5. 同步结束后，Container 自动销毁释放资源。
- **生产注意事项——环境依赖分发**：DataX 包含了大量插件，体积高达数百兆。跑在 YARN 上必须解决包依赖问题。通常的做法是提前将 DataX 环境部署到所有 NodeManager 节点的固定本地目录下；或者通过 HDFS 的 Distributed Cache 机制，在 Container 启动时自动将环境包分发到本地，保障任务快速启动。

### 7. HDFS 同步细节与生产性能排障

#### (1) DataX 对 HDFS 多类型及压缩格式的处理

DataX 的 `HdfsReader` 和 `HdfsWriter` 插件提供了对底层 HDFS 文件系统的强力支持：

- **文件类型支持**：原生支持 `TEXT`（普通文本，通常是 CSV/TXT）、`ORC`、`RC`、`SEQ` 以及 `CSV` 等多种大数据常见列式/行式存储文件格式。在配置时通过 `fileType` 参数直接指定。对于复杂的 ORC 和 Parquet 格式，DataX 底层直接调用 Hadoop 和 Hive 的原生 API 进行解析和序列化。
- **压缩格式支持**：
  - **读端（Reader）**：HdfsReader 非常智能。对于文本类型，它支持透明解压 `gzip`、`bzip2`、`zip`、`lzo`、`lzo_deflate`、`snappy` 等格式。只要 HDFS 文件的扩展名符合规范，DataX 底层会根据文件后缀自动选择对应的 Hadoop CompressionCodec 进行动态解压缩读取。
  - **写端（Writer）**：HdfsWriter 支持将数据压缩后写入 HDFS。通过 `compress` 参数指定，如 `gzip`、`bzip2`、`snappy` 等。特别是在写入 ORC 时，常常搭配 `snappy` 压缩，以获得极高的压缩比和读取性能。

#### (2) 同步时源端与目标端文件是否一一对应？

**答案是：否。通常不会一一对应。**

- **核心原因（多线程切分架构）**：DataX 的设计理念是**并发提速**。当一个 Job 被启动时，DataX 的 `Job` 模块会根据配置的并发度（`channel` 数量）以及源端文件的大小、数量，将其切分为多个 `Task`。
- **读取逻辑**：如果源端有 1 个大文件，且该文件格式支持切分（Split，如普通的 HDFS 文本文件或 ORC 块），DataX 会将其切分为多个 Task 范围并行读取。
- **写入逻辑**：每个 `Task` （本质上是一个线程）独立拥有一个 `Writer` 实例。在向目标端（如 HDFS 或本地文件系统）写入时，**每个并行的 Writer 线程都会在目标目录下生成一个独立的新文件**，文件名的后缀通常带有随机的 UUID 或者线程 TaskID。
- **结论**：源端可能只有 1 个文件，但如果设置了 3 个 Channel 并发同步，目标端通常会生成 3 个独立的文件（即 `1 对多`）。同样，源端有 10 个小文件，由于被分配到了 3 个 Channel 中执行，目标端最终可能只产生 3 个较大的合并文件（即 `多对少`）。因此，**文件的一一对应关系被框架层面的多线程并发模型打破了，DataX 保证的是“数据总内容的一致性”，而不是“物理文件的 1 对 1 映射”。**

#### (3) 生产中常见的 DataX 性能瓶颈与问题场景

DataX 虽然单机性能极佳，但在生产环境中如果不加调优，经常会遇到以下性能瓶颈与故障：

1. **OOM（内存溢出）导致任务崩溃**：
  - **场景**：单条记录过大（如包含超长 TEXT/BLOB、巨大 JSON 串），或者配置了过多的并发 Channel 数，超出了 JVM 堆内存的限制（默认通常较小）。
  - **解决**：调整启动脚本中的 JVM 参数（如调大至 `-Xms4g -Xmx4g`），并在配置中合理评估并发线程数，严控脏数据。
2. **源库/目标库被打死（连接耗尽或 IO 爆满）**：
  - **场景**：DataX 的并发抽取或写入速度过快，如果不加限制，极容易将源端 MySQL/Oracle 的磁盘 IO 或网卡带宽跑满，导致生产线上正在运行的业务库崩溃；或者向目标端高速写入时耗尽连接池资源。
  - **解决**：**生产环境必须配置限流！** 利用 DataX 的 `speed.byte`（字节限速）或 `speed.record`（记录数限速）参数，对通道进行硬性限流。
3. **大表同步极慢（缺失切分键引发单线程慢查）**：
  - **场景**：从 RDBMS（如 MySQL）同步数亿级别的大表，如果没有配置 `splitPk`（切分键），DataX 只能退化为单线程（仅 1 个 Task）去执行一条极其庞大的 `SELECT` * 语句。这不仅耗时极长，还极易导致数据库产生长事务或表锁。
  - **解决**：同步大表必须配置 `splitPk`（通常选择自增主键 ID），使 DataX 能自动将查询拆分为多个类似于 `WHERE id >= 1000 AND id < 2000` 的小任务，从而实现真正的多线程并发查询。
4. **HDFS 小文件灾难**：
  - **场景**：正如前文所述，DataX 的并发机制会导致每个 Writer 线程生成一个新文件。如果离线任务调度非常频繁（例如每 5 分钟同步一次微批次），且每次开启几十个并发，HDFS 目标目录很快会被数以万计的 kb 级别小文件填满。
  - **解决**：定期在 Hive/Spark 中跑脚本进行 `ALTER TABLE ... CONCATENATE` 或通过重写表数据来合并小文件，以缓解 HDFS NameNode 的元数据内存压力。

---

## 二、 SeaTunnel 深度解析

SeaTunnel（曾用名 Waterdrop）是一个非常易用、高性能、支持实时流式和离线批处理的海量数据集成平台。它目前是 Apache 顶级项目。

### 1. 架构设计

SeaTunnel 的架构经历了重构，目前的核心架构为 **SeaTunnel Engine（Zeta） + Connectors + 兼容多计算引擎**。

- **计算引擎抽象层**：早期 SeaTunnel 强依赖 Spark 和 Flink。新版本引入了自研的专属数据同步引擎 **SeaTunnel Zeta**，同时也继续兼容 Flink 和 Spark 引擎。这使得 SeaTunnel 可以脱离庞大的 Hadoop 生态独立运行。
- **Connectors（连接器）**：
  - **Source**：负责接入各种数据源（支持批处理和流处理）。
  - **Transform**：数据转换层，支持 SQL 过滤、字段映射、拆分合并等轻量级 ETL 操作。
  - **Sink**：负责将处理后的数据输出到目标存储。
- **API 解耦**：通过统一的 Source/Sink API，插件开发者不需要关心底层运行的是 Zeta、Spark 还是 Flink。

### 2. 设计理念

- **批流一体**：原生支持离线批量同步和实时流式同步（如 CDC），一套代码和配置解决两种场景。
- **分布式与高性能**：天生为海量数据设计，通过分布式计算引擎实现高吞吐量和横向扩展。
- **引擎解耦**：自研 Zeta 引擎专为数据同步优化（例如无锁队列、动态线程共享），不仅轻量而且减少了对 Spark/Flink 庞大集群的依赖。

### 3. 特点优势及不足

- **优势**：
  - **海量数据处理与高可扩展**：基于分布式引擎，轻松应对百亿、千亿级数据的同步。
  - **实时同步与 CDC**：支持多源 CDC（如 MySQL Binlog、Postgres、SQL Server 等），完美契合实时数仓建设。
  - **引擎多样性**：可无缝运行在自研 Zeta 引擎、Spark 或是 Flink 集群上，灵活适配企业现有基础设施。
  - **Exact-Once 语义**：在流式同步中能够保证数据精确一次送达，避免数据丢失或重复。
- **不足**：
  - **学习与运维成本相对较高**：相比于单机的 DataX，SeaTunnel 若依赖 Flink/Spark 或部署 Zeta 集群，其排错和运维复杂度直线上升。
  - **组件仍在高速迭代**：作为相对较新的 Apache 顶级项目，部分非核心 Connector 的稳定性可能还需进一步打磨。

### 4. 适用场景

- 海量数据的离线初始化与定期同步。
- **实时数仓（Real-time Data Warehouse）入仓**：实时捕获业务库 CDC 日志并写入 Kafka、Doris、ClickHouse 等。
- 需要进行轻量级 ETL（如字段脱敏、拆分）的复杂同步链路。

### 5. 任务配置方式

SeaTunnel 采用类似 Nginx 的 **HOCON（Human-Optimized Config Object Notation）** 格式编写配置文件，结构极其清晰，分为 `env`（引擎环境）、`source`、`transform`（可选）和 `sink` 四个部分。

```hocon
env {
  execution.parallelism = 2
  job.mode = "BATCH" // 可选 BATCH 或 STREAMING
}

source {
  Jdbc {
    url = "jdbc:mysql://localhost:3306/db"
    driver = "com.mysql.cj.jdbc.Driver"
    connection_check_timeout_sec = 100
    user = "root"
    password = "pwd"
    query = "select id, name from user"
  }
}

transform {
  # 可选的转换操作，例如将全大写转小写，或者 SQL 过滤
  Sql {
    source_table_name = "fake_table"
    result_table_name = "fake_table_2"
    query = "select id, lower(name) as name from fake_table"
  }
}

sink {
  Clickhouse {
    host = "localhost:8123"
    database = "default"
    table = "user_sync"
    username = "default"
    password = ""
  }
}
```

### 6. 数据同步原理与引擎依赖机制

#### (1) SeaTunnel 的数据同步原理与 API 解耦

SeaTunnel 的核心同步原理是基于统一的 Source、Transform、Sink 抽象。为了实现“一次编写，多引擎运行”的设计目标，SeaTunnel 实现了名为 **SeaTunnel API (V2)** 的统一数据处理接口体系。

- **Translation 转换层（翻译层）**：当 SeaTunnel 任务提交到具体的底层执行引擎（如 Flink、Spark 或原生 Zeta）时，SeaTunnel 内部的 Translation 层会将 SeaTunnel API 编写的 Source、Transform 和 Sink 动作**动态翻译（转换为）**该底层引擎能够识别的原生算子。
  - 例如，如果在 Flink 引擎上运行，SeaTunnel Source 会被翻译成 Flink 的 `SourceFunction` 或 `InputFormat`，Sink 会被翻译成 Flink 的 `SinkFunction`。
- **API 解耦的优势**：Connector 开发者只需要基于 SeaTunnel API 编写一套读取和写入逻辑，框架就会自动负责将其适配到底层的 Spark RDD/DataFrame、Flink DataStream 或 Zeta 引擎上，打破了过去必须为 Flink 和 Spark 各写一套插件的窘境。

#### (2) 依赖 Flink/Spark 的执行过程

虽然 SeaTunnel 推出了原生的 Zeta 引擎，但在很多企业中依然广泛使用其依赖 Flink 或 Spark 的模式，以复用现有的 Hadoop/YARN 计算资源。

- **解析与提交流程**：当用户通过 `start-seatunnel-flink.sh` 或 `start-seatunnel-spark.sh` 提交任务时，SeaTunnel 客户端实际上是把用户的 HOCON 配置文件解析，并封装成了一个标准的 Flink 或 Spark Application。
- **任务编排 (DAG)**：SeaTunnel 根据配置文件生成一个逻辑有向无环图（DAG），其中包含了读取（Source）、转换（Transform）和写入（Sink）节点。
- **底层引擎全面接管**：该 DAG 经过 Translation 翻译后，被完整移交给 Flink 的 JobManager 或 Spark 的 Driver。接下来所有的**分布式资源调度、Task 分片、跨节点内存/网络数据交换、容错管理（如 Checkpoint）**，全部由底层的 Flink 或 Spark 引擎原生负责，SeaTunnel 仅仅作为算子的逻辑提供方，不再干预核心的物理计算流转。

#### (3) 流同步与批同步任务的执行过程剖析

SeaTunnel 真正的“批流一体”能力正是通过底层计算引擎的特性来实现的。配置参数 `job.mode = "BATCH"` 或 `STREAMING` 将直接决定底层引擎的执行模式。

- **批同步（BATCH）任务执行过程**：
  1. **数据有界性**：Source 端（如读取 HDFS 文件或 RDBMS 表）明确知晓数据的边界和总大小。
  2. **并发分片读取**：类似于 DataX，SeaTunnel Source 会根据配置的并行度对全量数据进行分片（Split）切分，多个 Task 实例在 Spark/Flink 的不同节点上并行读取数据块。
  3. **计算与写入（无状态）**：数据流转到 Sink 端执行批量写入。所有数据处理完毕后，触发最终的 Commit 操作（例如移动临时文件、提交数据库事务）。
  4. **任务结束并释放资源**：全量数据跑批完成后，底层的 Flink/Spark 任务自动进入 `FINISHED` 状态，释放 YARN/K8s 集群资源。
- **流同步（STREAMING）任务执行过程**：
  1. **数据无界性与 CDC 捕获**：主要用于实时同步场景（如 MySQL Binlog、Kafka 消费）。Source 端处于长连接监听状态，源源不断地实时捕获变更数据流。
  2. **持续运行**：流任务一旦提交，只要不发生致命错误或被人工停止，该 Application 将永远处于 `RUNNING` 状态，占用固定的集群资源。
  3. **Checkpoint 状态保存**：流同步过程中，强依赖底层引擎（如 Flink 的 Checkpoint 机制）定期打全局快照。SeaTunnel 会将 Kafka 的 Offset 或者 MySQL 的 Binlog Position 连同内存中的数据状态一起持久化到状态后端（如 HDFS）。
  4. **两阶段提交与 Exactly-Once 保障**：为了保证目标端数据“不重不丢”（Exact-Once 语义），Sink 端（如写入 ClickHouse 或 Kafka）通常配合 Checkpoint 触发分布式两阶段提交（2PC）。只有当一个 Checkpoint 周期内的所有数据都被所有并发节点成功处理后，才会向目标端发起最终的 Commit；若中途某个节点宕机，则依靠最近一次成功的 Checkpoint 全局回滚并重新消费。

### 7. 多计算引擎（Spark / Flink / Zeta）特性对比与选型建议

SeaTunnel 最强大的特性之一就是可以在 Spark、Flink 和自研的 Zeta 引擎之间无缝切换。这三种引擎在处理数据同步任务时有着各自鲜明的架构特性和最佳适用场景。

#### (1) 基于 Spark 引擎的同步任务

- **引擎特性**：Spark 是基于内存的分布式微批处理（Micro-batch）计算框架。在 SeaTunnel 中，批处理模式会被翻译为 Spark RDD/DataFrame 算子；流处理模式则会被翻译为 Spark Structured Streaming 任务。
- **同步表现**：
  - 吞吐量极高，非常适合海量数据的离线批量搬运。
  - 在流同步（CDC）场景下，由于其底层本质依然是“微批”，数据延迟通常在秒级甚至分钟级，无法做到真正的亚秒级实时。
- **推荐场景**：**海量离线批处理首选**。如果企业内部已经有了非常庞大成熟的 Hadoop/YARN 平台和 Spark 体系，且同步任务主要以 T+1 或小时级大批量全量/增量同步为主，对毫秒级实时性没有苛刻要求。

#### (2) 基于 Flink 引擎的同步任务

- **引擎特性**：Flink 是天生的分布式纯流式计算框架（将批处理视为有界流）。在 SeaTunnel 中，任务会被动态翻译为 Flink 的 DataStream API 算子。
- **同步表现**：
  - 真正的实时流处理，延迟可达毫秒级。
  - 容错机制极其强大，利用 Flink 原生的 Checkpoint 和分布式状态快照，完美支持海量 CDC 数据流的 Exactly-Once（精确一次）语义保障。
  - 资源占用相对 Spark 较小，但在处理几十 TB 级别的超大纯离线批任务时，极限吞吐量可能略逊于 Spark。
- **推荐场景**：**实时流同步与 CDC 入仓首选**。当业务要求秒级/亚秒级将 MySQL Binlog 实时同步到 ClickHouse、Doris 等实时数仓，且对数据丢失零容忍时，Flink 是绝对的最佳选择。同样非常适合企业已经维护了 Flink 集群的场景。

#### (3) 基于 SeaTunnel Engine (Zeta) 的同步任务

- **引擎特性**：Zeta 是 SeaTunnel 在 2.x 版本后期重磅推出的**专门为数据同步而生**的自研原生引擎。它没有沉重的 Hadoop 历史包袱。
- **核心优势与独有表现**：
  - **极其轻量**：不需要依赖庞大的 YARN、Spark 或 Flink 集群，几台机器直接拉起即可组成高可用集群。
  - **动态线程共享机制**：在同步大量小表的 CDC 任务时，Flink/Spark 会为每一个表分配固定的计算槽（Slot），导致资源严重浪费；而 Zeta 引擎实现了多表同步任务在一个 JVM 进程内共享线程和连接，极大节省了连接池和 CPU 资源（比如一键整库同步 100 张小表，Zeta 的资源占用仅为 Flink 的几十分之一）。
  - **无锁队列**：专门针对数据传输优化的底层的无锁队列（Disruptor），数据在 Source 和 Sink 之间传递的损耗降到最低。
  - **自带容错**：Zeta 内置了轻量级的分布式 Checkpoint 快照和两阶段提交机制，同样支持 Exactly-Once 语义。
- **推荐场景**：**独立数据集成平台与多表 CDC 同步首选**。如果企业没有运维 Hadoop/Flink/Spark 集群的经验和精力，或者核心诉求是“整库实时同步（如几千张表同时做 CDC）”，Zeta 引擎是最佳选择。部署最简单，专为同步优化，资源利用率最高。

---

## 三、 总结与选型建议


| 维度         | DataX                            | SeaTunnel                                |
| ---------- | -------------------------------- | ---------------------------------------- |
| **计算架构**   | 单机多线程                            | 分布式集群（Zeta / Flink / Spark）              |
| **处理模式**   | 仅离线批处理                           | 批流一体（支持全量批处理 + CDC 实时流）                  |
| **数据规模**   | 中小规模（TB级别以下）                     | 海量数据（PB级别无压力）                            |
| **部署与运维**  | 极简，单机执行脚本即可                      | 相对复杂，需维护分布式引擎或集群                         |
| **ETL 能力** | 极弱，纯搬运                           | 较强，支持 SQL Transform 和丰富的数据处理逻辑           |
| **选型建议**   | 传统定时跑批、小数据量搬运、不具备分布式引擎运维能力的团队首选。 | 实时数仓建设、海量数据同步、需要 CDC 能力、有分布式集群运维经验的团队首选。 |


