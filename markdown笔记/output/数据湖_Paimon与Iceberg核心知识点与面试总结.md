# 数据湖核心知识点总结：Apache Iceberg 与 Apache Paimon

本文档旨在全面梳理 Apache Iceberg 和 Apache Paimon 的基础知识、架构原理、优缺点及应用场景，并对两者进行深度对比。最后，针对大数据开发面试，总结了数据湖领域的高频面试题及解答思路。

---

## 一、 Apache Iceberg 基础知识

### 1. 背景

Apache Iceberg 最初由 Netflix 开发并开源，后捐赠给 Apache 基金会成为顶级项目。其诞生的核心背景是为了**解决传统 Hive 格式在处理海量数据时遇到的元数据管理瓶颈**（如 list 目录极慢、无法保证 ACID 事务、Schema 变更困难等）。

### 2. 原理与架构

Iceberg 的核心思想是**“在文件级别管理元数据，而不是在目录级别”**。

- **架构层级（元数据树）**：
  - **Snapshot（快照）**：代表表在某一时刻的状态。每次写入都会生成一个新的 Snapshot。
  - **Manifest List（清单列表）**：记录了当前 Snapshot 包含哪些 Manifest File。
  - **Manifest File（清单文件）**：记录了具体的数据文件（Data Files）路径、分区信息、列级别的统计信息（最大值、最小值、Null 数量等）。
  - **Data Files（数据文件）**：实际存储数据的底层文件（如 Parquet, ORC, Avro）。

```text
iceberg_table/
├── metadata/
│   ├── v1.metadata.json    # 快照文件 : 包含 Schema 和 Snapshot 信息
│   ├── v2.metadata.json
│   ├── snap-1.avro         # Manifest List
│   └── manifest-1.avro     # Manifest File
└── data/                   # 数据文件 (Parquet/ORC)
```

### 3. 特点与解决的问题

- **原数据架构**：彻底摆脱了对 Hive Metastore 目录 List 操作的依赖，采用自描述的三层元数据架构,将元数据存储在分布式系统中(HDFS/S3),极大提升了海量分区表的查询规划速度。
- **原数据查询**：Hive Metastore只存储粗粒度(表、分区路径) ; 元数据存储丰富的统计信息(列最大/最小值,空值数),可精准过滤数据文件。
- **并发及ACID事务**：Hive缺乏事务支持 , 并发写入易冲突且有瓶颈; 采用乐观并发控制和快照隔离，实现行级ACID，支持多任务并发写入，读写互不干扰。(备注说明 : 多个写入任务可以同时进行，各自生成新的数据文件。在最后提交阶段，系统会原子性地检查当前表的快照是否被修改。如果没有，则提交成功，生成一个新的快照；如果检测到冲突，任务会重试或报错。这种方式避免了长时间的表锁，极大地提升了写入吞吐量)
- **隐藏分区（Hidden Partitioning）**：用户只需按照业务字段查询，Iceberg 底层自动进行分区裁剪，避免了 Hive 中因分区字段变更导致的全表重写。
- **Schema 演进（Schema Evolution）**：支持添加、删除、重命名列，且不会产生副作用（如数据错乱），通过内部的 ID 映射机制实现 , 支持分区演进，可随时修改分区规则，新旧分区共存而无需重写数据。
- **时间旅行（Time Travel）**：通过快照机制记录每次操作，支持时间旅行，可随时查询或回滚至任意历史版本。

### 4. 优缺点

- **优点**：生态极其繁荣（完美支持 Spark、Trino、Presto、Flink 等）；批处理和分析查询性能极佳；元数据管理设计优雅，极其稳定。
- **缺点**：
  - 写入与更新性能
    - 高频的数据更新及删除性能一般(默认Copy-on-Write) , 导致写入延迟较高 ; V2引入(Merge-on-Write)牺牲了查询性能
    - 频繁写入带来的小文件问题 , 每次写入会生成新的数据及元数据文件, 大量小文件会拖慢查询及存储性能
    - 流式写入数据可见性的延迟较高(分钟级的checkpoint) , 无法实现毫秒级
  - 运维复杂度
    - 定期优化 : 定期运行 `rewrite_data_files` 等命令合并小文件以解决小文件问题 (该过程会消耗计算资源)
    - 定期清理 : 时间旅行功能带来大量的历史快照 , 导致元数据膨胀 , 需要定期维护
    - 手动治理 : 官方治理工具非自动化 , 需手动编写调度任务完成
  - 其它注意点
    - 小数据集的"性能惩罚" : 小表查询效率反而不占优势 , 为大数据集设计
    - 并发能力有限 : 乐观锁的高并发能力有限 , 易写入冲突导致事务失败及重试
    - 安全与治理功能 , 生态碎片化进度不易 , 需注意适配

### 5. 应用场景

- **海量数据离线数仓**：替代传统 Hive 数仓，作为企业级数据湖的底层存储标准。
- **BI 报表与交互式分析**：结合 Trino/Presto 提供亚秒级到秒级的海量数据查询。
- **数据回溯与合规审计**：利用 Time Travel 特性进行数据审计。

### 6. 未来发展方向

- 增强对流式高频更新的支持。
- 完善 REST Catalog 规范，推动数据湖元数据中心的统一。
- 更智能的自动优化服务（如自动 Compaction、自动清理过期快照）。

---

## 二、 Apache Paimon 基础知识

### 1. 背景

Apache Paimon（原名 Flink Table Store）最初由阿里云和 Flink 社区主导孵化，现为 Apache 顶级项目。其诞生背景是为了**填补数据湖在“实时高频更新”和“流批一体”场景下的短板**，致力于打造真正的流式数据湖（Streaming Lakehouse）。

**定位** : 统一 消息队列(kafka)负责的流处理,数据湖(hive)负责的批处理,分析系统(clickhouse)负责的查询

**设计目标** :

- 支持高吞吐写入 , 降低端到端的延迟
- 原生支持 Update/Delete等实时负载更新
- 提供流读的能力 , 像kafka一样消费增量变更 (依赖于changelog能力)
- 支持批量分析和OLAP查询

### 2. 原理与架构

Paimon 的整体设计可以概括为：**以文件系统为底座，以 Snapshot 管理表版本，以 Bucket + LSM-Tree 组织主键表数据，以 Catalog 统一元数据入口**。它并不是简单地把 Parquet 文件堆在目录里，而是把「存储布局、元数据、写入提交、Compaction」串成一套完整的湖表引擎。

#### 2.1 整体架构

```text
                    ┌─────────────────────────────────────┐
                    │           Catalog 层                 │
                    │  Filesystem / Hive / JDBC / REST    │
                    └─────────────────┬───────────────────┘
                                      │ 管理库表、快照、Schema
                    ┌─────────────────▼───────────────────┐
                    │              Table                   │
                    │  Partition → Bucket → Data File      │
                    └─────────────────┬───────────────────┘
           ┌──────────────────────────┼──────────────────────────┐
           │                          │                          │
    ┌──────▼──────┐            ┌───────▼───────┐           ┌───────▼───────┐
    │  元数据层    │            │   数据存储层   │           │  维护服务层    │
    │ Snapshot    │            │ Bucket-0..N   │           │ Compaction    │
    │ Schema      │            │ LSM Level 文件 │           │ Expire Snap   │
    │ Manifest    │            │ Changelog 文件 │           │ Tag / Branch  │
    └─────────────┘            └───────────────┘           └───────────────┘
```

- **Catalog 层**：对外提供库表管理能力，决定元数据存哪里、如何被发现。
- **Table 层**：一张 Paimon 表 = Schema + 多个 Snapshot + 多个数据文件。
- **数据组织层**：先按**分区（Partition）**切分，再按**分桶（Bucket）**切分；主键表在每个 Bucket 内维护一棵 LSM-Tree。
- **维护层**：Compaction、快照过期、Tag/Branch 等后台或调度任务，保证读写性能和元数据可控。

#### 2.2 存储布局（Storage Layout）

Paimon 表在 HDFS / S3 / OSS 等对象存储上通常呈现如下逻辑结构：

```text
table_path/
├── schema/                 # 历史 Schema 版本
├── snapshot/               # 每次提交生成的快照文件
├── manifest/               # 清单文件，记录数据文件列表及统计信息
├── bucket-0/               # 第 0 号桶的数据
│   ├── level-0/            # LSM 低层，增量文件较多
│   ├── level-1/
│   └── ...
├── bucket-1/
├── changelog/              # 可选，变更日志文件
└── index/                  # 可选，辅助索引
```

**关键概念**：


| 概念                  | 说明                                           |
| ------------------- | -------------------------------------------- |
| **Partition（分区）**   | 按时间、地域等业务字段切分数据，便于裁剪和生命周期管理                  |
| **Bucket（分桶）**      | 主键表按 Primary Key 做 Hash 分桶，控制单文件大小并提升并发写入能力  |
| **Data File（数据文件）** | 底层一般为 **Parquet / ORC**，承载实际列式数据             |
| **LSM Level**       | 主键表每个 Bucket 内部按 Level 组织文件，Level 越高文件越大、越有序 |
| **Changelog File**  | 记录 INSERT/UPDATE/DELETE 变更，供下游流式消费           |


**与 Iceberg 的差异**：Iceberg 更强调「Snapshot → Manifest → Data File」的清单式元数据；Paimon 在主键表场景下额外引入 **Bucket + LSM-Tree**，把高频 Upsert 的写入压力分散到多个桶内，通过顺序追加 + 后台合并完成更新。

#### 2.3 元数据管理（Metadata）

Paimon 的元数据同样采用**快照隔离**思想，但结构更贴近流式写入场景：

1. **Schema 文件**
  - 记录字段名、类型、主键、分区键、Bucket 数等表结构信息。
  - 支持 Schema Evolution，历史 Snapshot 仍可按当时 Schema 读取。
2. **Snapshot 文件**
  - 每次成功 Commit 后生成一个新 Snapshot，代表表在某个时间点的完整视图。
  - Snapshot 中记录：当前 Schema 版本、Manifest 列表、Watermark、统计信息等。
  - 支持 **Time Travel**：按 Snapshot ID 或时间戳读取历史版本。
3. **Manifest 文件**
  - 记录某个 Snapshot 下有哪些 Data File / Changelog File。
  - 携带分区值、Bucket、文件大小、行数、列级 Min/Max 等统计信息，供查询引擎做文件裁剪。
4. **Catalog**
  - 常见实现：**Filesystem Catalog**（元数据直接落在表目录）、**Hive Metastore Catalog**、**JDBC Catalog** 等。
  - Catalog 负责定位表路径和维护库表命名空间，真正的 Snapshot/Manifest 仍存储在表目录中。

**元数据读写特点**：

- 写入时采用**原子提交**：先写数据文件，再写 Manifest，最后切换 Snapshot 指针，避免读到半成品。
- 查询时只需读取最新 Snapshot 及其 Manifest，不需要像 Hive 那样 List 全部分区目录。
- 历史 Snapshot 可通过 `expire snapshots` 清理，避免元数据无限膨胀。

#### 2.4 写入与提交流程（Write Pipeline）

以 Flink 写入主键表为例，完整链路如下：

```text
Source 数据
   │
   ▼
按 Primary Key 计算 Bucket
   │
   ▼
写入 Writer 内存缓冲（MemTable / Write Buffer）
   │
   ▼
Checkpoint 或 Buffer 满 → Flush 成 Level-0 数据文件
   │
   ▼
生成 Manifest，提交新 Snapshot（两阶段提交，与 Flink Checkpoint 对齐）
   │
   ▼
后台 Compaction 将多层小文件合并为更大、更有序的文件
   │
   ▼
可选：同时产出 Changelog 文件，供下游流读
```

**写入机制要点**：


| 环节                | 机制                               | 作用                               |
| ----------------- | -------------------------------- | -------------------------------- |
| **分桶路由**          | `hash(primary_key) % bucket_num` | 将同一主键稳定路由到同一 Bucket，保证 Upsert 语义 |
| **LSM 追加写**       | 先写内存，再 Flush 成新文件                | 避免随机写，提高流式 CDC 吞吐                |
| **Merge 语义**      | 同主键多条记录按 Sequence / Timestamp 合并 | 实现 Update、Delete、Partial Update  |
| **Checkpoint 提交** | 与 Flink 两阶段提交绑定                  | 保证 Exactly-Once 写入               |
| **Compaction**    | Universal / Full / Lookup 等策略    | 减少读放大和小文件，提升批查性能                 |
| **Changelog 产出**  | 在 Merge / Compaction 过程中生成       | 让下游像消费 Kafka 一样读增量               |


**Append-Only 表的写入更简单**：不做主键去重，按分区直接追加 Data File，适合日志、埋点等只增不改的数据。

#### 2.5 读取路径（Read Path）

- **批读（Batch Read）**：读取最新 Snapshot → 过滤 Manifest → 读取目标 Data File，适合 Spark / Trino / StarRocks 离线分析。
- **流读（Streaming Read）**：从指定 Snapshot 开始，持续消费新增 Snapshot 或 Changelog File，适合 Flink 实时链路。
- **增量读（Incremental Read）**：只读两个 Snapshot 之间的差异数据，适合增量 ETL。

> 表类型差异、各引擎支持能力见下文第三、四章专门说明。

### 3. 表类型详解

Paimon 不是只有一种表，**表类型决定写入语义、是否支持 Upsert、能否产出 Changelog**。选型时首先要明确表类型。

#### 3.1 主键表（Primary Key Table）

- **定义**：声明 `PRIMARY KEY`，同一主键只保留最新版本记录。
- **底层结构**：`Partition → Bucket → LSM-Tree`。
- **支持操作**：INSERT、UPDATE、DELETE、Upsert。
- **典型场景**：CDC 入湖、维度表缓慢变化、需要按主键修正的数据集。
- **关键配置**：`bucket` 数量、`merge-engine`（deduplicate / partial-update / aggregation）、`changelog-producer`。
- **特点**：写入性能强，但依赖 Compaction 保证查询效率；Bucket 数与并发度、文件大小密切相关。

#### 3.2 Append-Only 表（Log Table）

- **定义**：无主键，只追加、不去重。
- **底层结构**：按分区直接追加 Parquet/ORC 文件，无 LSM 合并逻辑。
- **支持操作**：仅 Append。
- **典型场景**：日志、埋点、原始事件流、无需更新的明细数据。
- **特点**：写入最简单、吞吐高；不支持按主键更新，但批查和流读开销通常低于主键表。

#### 3.3 Partial Update 表（局部更新）

- **定义**：主键表的一种 `merge-engine`，不同字段可由不同上游流分别写入。
- **语义**：同一主键的多条记录按字段级别合并，后到的非空字段覆盖先前值。
- **典型场景**：实时宽表拼接，如用户基础信息、订单信息、标签信息来自不同 Topic/CDC 流。
- **价值**：避免传统做法中先落 Kafka 再 Join 的复杂链路，直接在湖表完成打宽。

#### 3.4 Aggregation 表（聚合表）

- **定义**：主键表的一种 `merge-engine`，同一主键的多条记录在写入时自动聚合。
- **语义**：支持 SUM、MAX、MIN、LISTAGG 等聚合函数，适合实时汇总。
- **典型场景**：实时 DWS 层指标汇总，如按用户/商品维度累计 PV、GMV。
- **特点**：将「流计算聚合 + 落湖」合二为一，减少中间 Kafka 状态存储。

#### 3.5 Changelog 表语义（变更日志）

- **说明**：Changelog 不是独立表类型，而是主键表可开启的一种**产出模式**。
- **配置**：通过 `changelog-producer` 控制，如 `input`、`lookup`、`full-compaction` 等。
- **产出内容**：下游可读到 `+I / -U / +U / -D` 等变更类型，类似 Flink CDC 格式。
- **典型场景**：一条 Flink 作业写 Paimon，下游多条 Flink 作业流式消费变更继续加工。
- **价值**：Paimon 可部分替代「Kafka 做中间层」的架构，降低链路复杂度与存储成本。

#### 3.6 表类型选型小结


| 表类型            | 是否主键 | 是否 Upsert | 是否产出 Changelog | 典型场景      |
| -------------- | ---- | --------- | -------------- | --------- |
| Primary Key    | 是    | 是         | 可选             | CDC 入湖、维表 |
| Append-Only    | 否    | 否         | 否              | 日志、埋点     |
| Partial Update | 是    | 是（按列）     | 可选             | 多流打宽表     |
| Aggregation    | 是    | 是（聚合）     | 可选             | 实时汇总指标    |


### 4. 引擎生态概览

Paimon 支持多引擎访问，但**读写能力并不对等**：Flink 能力最完整，其余引擎以批读或查询为主。


| 引擎            | 主要特点                                              | 典型用途                     |
| ------------- | ------------------------------------------------- | ------------------------ |
| **Flink**     | 流写/流读、CDC 入湖、Upsert/Delete、Changelog、Exactly-Once | 实时数仓主链路（ODS → DWD → DWS） |
| **Spark**     | 批读/批写，流式能力有限                                      | 离线补数、历史回灌、T+1 ETL        |
| **StarRocks** | 通过 External Catalog 读 Paimon，查询性能强                | BI 报表、即席 OLAP 分析         |
| **Trino**     | 批读为主，联邦查询                                         | 交互式分析、跨源查询               |


**选型口诀**：实时写入与流读走 **Flink**，离线批处理走 **Spark**，分析查询走 **StarRocks / Trino**。

### 5. 特点与解决的问题

- **极高吞吐的流式更新**：得益于 LSM-Tree 架构，Paimon 能够轻松应对海量 CDC（Change Data Capture）数据的实时 Upsert/Delete 操作。
- **局部更新与聚合（Partial Update & Aggregation）**：支持多个流向同一张表写入不同列（打宽表），或者在写入时自动进行聚合计算。
- **流读流写**：不仅支持批查询，还能像 Kafka 一样被 Flink 持续流式读取（Streaming Read），实现真正的流批一体数仓。
- **解决的痛点**：解决了传统数据湖（如 Iceberg/Hudi）在面对超高频 CDC 写入时产生大量小文件、合并代价过高、无法高效生成下游 Changelog 的问题。

### 6. 优缺点

- **优点**：实时性极强，CDC 摄入和流式更新性能业界领先；与 Flink 生态深度绑定，流批一体体验最佳；自带 Changelog 生产能力。
- **缺点**：相对年轻，生态广度（如对 Spark、Trino 的深度优化）还在追赶 Iceberg；LSM-Tree 在纯批处理查询时的读放大问题需要通过 Compaction 来缓解。

### 7. 应用场景

- **实时数仓（Real-time Lakehouse）**：替代部分 Kafka + 传统数仓的架构，实现 ODS 到 DWD/DWS 的全链路分钟级/秒级延迟。
- **数据库 CDC 实时入湖**：将 MySQL/Oracle 的 Binlog 实时同步到数据湖。
- **多流拼接（实时打宽表）**：利用 Partial Update 引擎特性，在湖层实时拼接大宽表。

### 8. 未来发展方向

- 脱离 Flink 强绑定，增强对 Spark 引擎的写入和更新支持。
- 引入向量化读取和更高级的索引技术，提升 OLAP 批查询性能。
- 与 AI 基础设施集成，支持非结构化数据和向量数据的湖仓管理。

---

## 三、 Apache Iceberg 与 Apache Paimon 深度对比


| 维度           | Apache Iceberg                            | Apache Paimon                                   |
| ------------ | ----------------------------------------- | ----------------------------------------------- |
| **设计初衷**     | 解决海量批处理元数据管理瓶颈，面向**分析型数据湖**               | 解决高频流式更新与流批一体，面向**流式数据湖**                       |
| **底层核心架构**   | 纯元数据驱动（Snapshot -> Manifest -> Data File） | LSM-Tree 结构（MemTable -> SST Files + Compaction） |
| **更新机制**     | Copy-on-Write (CoW) / Merge-on-Read (MoR) | LSM-Tree 增量写入 + 异步 Compaction                   |
| **流式写入/CDC** | 支持，但高频更新易产生小文件，合并开销大                      | 极佳，原生为高频 Upsert/Delete 设计                       |
| **下游流式消费**   | 较弱，Changelog 生成依赖复杂的合并逻辑                  | 极佳，原生支持 Changelog 生产，可作为消息队列替代品                 |
| **生态中心**     | Spark, Trino, Presto, Snowflake           | Flink (绝对核心), Spark, StarRocks                  |
| **批查询性能**    | 极佳（列级统计信息过滤、向量化支持完善）                      | 良好（依赖 Compaction 程度，存在一定读放大）                    |
| **适用主场景**    | 离线数仓升级、海量数据 BI 分析、批处理 ETL                 | 实时数仓、CDC 实时入湖、流批一体链路                            |


---

## 四、 数据湖高频面试题及理解思路

### Q1：为什么我们需要数据湖格式（Iceberg/Paimon/Hudi），而不是直接用 Hive？

**理解思路**：

- **痛点**：Hive 强依赖 HDFS 目录结构和 MySQL Metastore。查询时需要 List 整个目录，耗时极长；不支持 ACID，读写并发会读到脏数据；分区变更需要重写数据；不支持细粒度的 Update/Delete。
- **解决**：数据湖格式将元数据下推到文件层管理（如 Iceberg 的 Manifest），实现了 O(1) 级别的元数据定位；通过快照（Snapshot）实现了 ACID 和时间旅行；通过 MoR 或 LSM-Tree 实现了高效的 Upsert/Delete。

### Q2：请简述 Apache Iceberg 的元数据管理机制？

**理解思路**：

- 一定要答出**三层结构**：`Snapshot` -> `Manifest List` -> `Manifest File`。
- **查询流程**：用户提交查询 -> 找到最新 Snapshot -> 读取 Manifest List 获取相关的 Manifest Files（根据分区范围初步过滤） -> 读取 Manifest File 获取具体的数据文件路径（根据列级别 Min/Max 统计信息精准过滤） -> 读取真实数据文件。
- **优势**：避免了 NameNode 的 List 压力，将过滤工作交给了计算引擎分布式执行。

### Q3：什么是 Copy-on-Write (CoW) 和 Merge-on-Read (MoR)？

**理解思路**：

- **CoW（写时复制）**：在更新数据时，将包含被更新数据的整个文件读取出来，修改后写成一个全新的文件。
  - *优点*：查询极快（没有合并开销）。*缺点*：写入极慢（写放大严重），不适合高频更新。
- **MoR（读时合并）**：更新数据时，将变更记录（Delete/Update）追加写入到一个小的增量文件（Delta File）中。查询时，将基础文件和增量文件在内存中进行 Merge。
  - *优点*：写入极快（追加写）。*缺点*：查询较慢（读放大，需要合并计算），需要后台定期执行 Compaction。

### Q4：Apache Paimon 是如何实现高吞吐的流式更新的？

**理解思路**：

- **存储层**：主键表按 `Partition → Bucket → LSM-Tree` 组织，同一主键 Hash 到固定 Bucket，写入以顺序追加为主。
- **写入层**：数据先进入 MemTable / Write Buffer，Checkpoint 或 Buffer 满后 Flush 为 Level-0 文件，再原子提交 Snapshot。
- **合并层**：同主键记录按 Sequence / Timestamp 做 Merge，实现 Upsert/Delete；后台 Compaction 合并多层小文件，控制读放大。
- **变更层**：可选产出 Changelog，下游 Flink 可持续流读，无需额外 Kafka 中转。
- **对比 Iceberg**：Iceberg 更偏 Manifest 清单 + CoW/MoR；Paimon 把 LSM-Tree 引入湖表，专为高频 CDC 和流批一体优化。

### Q5：在生产环境中，如何选择 Iceberg 和 Paimon？

**理解思路**：

- **看业务延迟要求**：如果是 T+1 或小时级的离线批处理数仓，主要引擎是 Spark/Trino，果断选择 **Iceberg**，生态完善且批查性能极致。
- **看更新频率与流处理要求**：如果是秒级/分钟级的实时数仓，需要接入大量 MySQL CDC 数据，且强依赖 Flink 进行流式计算和多流拼接，果断选择 **Paimon**，它在实时 Upsert 和 Changelog 分发上具有压倒性优势。

### Q6：数据湖中的“小文件问题”是如何产生的？如何解决？

**理解思路**：

- **产生原因**：流式写入（如 Flink 每分钟 Checkpoint 一次）会频繁生成小文件；高频的 Update/Delete（MoR 模式）会产生大量小的 Delta 文件。
- **解决思路**：
  1. **自动/异步 Compaction**：利用数据湖框架自带的合并服务，在后台将小文件合并为大文件（如 Paimon 的 LSM 合并，Iceberg 的 RewriteDataFiles action）。
  2. **调整 Checkpoint 间隔**：适当调大 Flink 的 Checkpoint 时间，减少 Flush 频率。
  3. **写入前 Shuffle**：在写入前按分区键或主键进行 Hash Shuffle，避免单个 Task 写入过多分区产生碎片文件。

### Q7：Paimon 的主键表和 Append-Only 表有什么区别？如何选型？

**理解思路**：

- **主键表**：有 PRIMARY KEY，底层 `Partition → Bucket → LSM-Tree`，支持 Upsert/Delete，适合 CDC、维表、需要修正的数据。
- **Append-Only 表**：无主键，按分区直接追加文件，只支持 Insert，适合日志、埋点等只增不改的数据。
- **选型原则**：需要更新/delete → 主键表；纯追加 → Append-Only；多流打宽 → Partial Update；实时汇总 → Aggregation。

### Q8：Paimon 的 Snapshot、Manifest、Bucket 分别是什么作用？

**理解思路**：

- **Snapshot**：表在某个时刻的一致性视图，每次 Commit 生成，支持 Time Travel 和流读起点。
- **Manifest**：记录 Snapshot 下有哪些 Data/Changelog 文件及统计信息，供查询做文件裁剪。
- **Bucket**：主键表按 PK Hash 分桶，每个桶内独立 LSM-Tree，分散写入压力并保证同主键路由一致。
- **串联关系**：写入产生 Data File → 写入 Manifest → 提交 Snapshot；读取则反向解析 Snapshot → Manifest → Data File。

