# 离线调度工具对比总结：Airflow、Kettle、DolphinScheduler

本文档从背景架构、设计特点、优缺点、使用方式、适用场景等维度，梳理 Apache Airflow、Pentaho Kettle（PDI）、Apache DolphinScheduler 三款常见离线调度/ETL 工具，并给出对比与面试高频考点。

---

## 一、 Apache Airflow

### 1. 背景

Apache Airflow 最初由 Airbnb 于 2014 年开发并开源，2019 年成为 Apache 顶级项目。其诞生背景是：**大数据与数据仓库任务日益复杂，传统 Cron + Shell 脚本难以管理依赖、重试、监控和可观测性**。

Airflow 的定位不是 ETL 引擎本身，而是**工作流编排与调度平台（Workflow Orchestrator）**：负责“什么时候跑、按什么顺序跑、失败怎么办”，具体数据处理通常交给 Spark SQL、Hive、Python 脚本、Shell 等外部系统执行。

### 2. 架构

```text
┌─────────────────────────────────────────────────────────┐
│                    Web UI / REST API                     │
├─────────────────────────────────────────────────────────┤
│  Scheduler          │  DAG Processor  │  Triggerer      │
│  (调度解析、下发)     │  (DAG 文件解析)  │  (Deferrable)   │
├─────────────────────────────────────────────────────────┤
│  Metadata DB (PostgreSQL/MySQL)  ←  DAG Run / Task 状态  │
├─────────────────────────────────────────────────────────┤
│  Executor 层                                              │
│  Sequential / Local / Celery / Kubernetes / ...          │
├─────────────────────────────────────────────────────────┤
│  Worker 节点执行具体 Task（调用 Spark/Hive/Shell 等）      │
└─────────────────────────────────────────────────────────┘
```

**核心组件**：

| 组件 | 作用 |
| :--- | :--- |
| **DAG** | 有向无环图，描述任务及其依赖关系 |
| **Operator** | 任务类型抽象，如 `BashOperator`、`SparkSubmitOperator` |
| **Scheduler** | 按 Cron/Interval 触发 DAG Run，调度 Task 实例 |
| **Executor** | 决定 Task 在哪个 Worker 上执行 |
| **Metadata DB** | 存储 DAG、Run、Task 实例、日志索引等元数据 |
| **Web UI** | 可视化监控、手动触发、补数、日志查看 |

**执行模型**：Airflow 2.x 采用 **Scheduler + Worker 分离**；Task 本身通常只是“提交作业”或“执行脚本”，真正的计算在外部集群（YARN/K8s/Spark）完成。

### 3. 设计特点

- **Code-as-Workflow**：DAG 用 Python 代码定义，版本可控、可测试、可复用。
- **Operator 生态丰富**：内置大量 Operator，社区提供 Spark、Hive、K8s、云厂商等扩展。
- **依赖表达灵活**：`>>` / `set_upstream()` 定义上下游；支持 Branch、Trigger Rule、Sensor 等复杂编排。
- **调度语义清晰**：`schedule`（Cron/Interval）、`start_date`、`catchup` 控制补历史数据行为。
- **可观测性强**：Task 级状态、重试、日志、SLA、告警（Email/Slack 等）完善。
- **与计算引擎解耦**：Airflow 管编排，Spark/Flink/Hive 管计算，职责边界清楚。

### 4. 优缺点

**优点**：

- 编排能力强，适合复杂 DAG、跨系统依赖调度。
- Python 生态 + Git 管理，工程化程度高。
- 社区活跃，插件丰富，云原生（K8s Executor）支持成熟。
- 监控、补数、回溯、权限等企业级能力较完善。

**缺点**：

- **学习曲线陡**：Python、Executor、Connection、XCom 等概念较多。
- **自身不做 ETL 转换**：数据清洗逻辑需写在外部 SQL/Spark 中，平台内无可视化转换。
- **Scheduler 单点瓶颈**：超大规模 DAG/Task 时需调优 DB 和 Scheduler。
- **动态 DAG 能力有限**：传统模式依赖 Python 文件解析，不如专用平台直观。
- **资源占用**：Metadata DB 和 Scheduler 需稳定运维。

### 5. 使用方式

1. **定义 DAG 文件**（Python）：

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="daily_etl",
    start_date=datetime(2024, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
) as dag:
    ods = BashOperator(task_id="load_ods", bash_command="spark-submit ods.py")
    dwd = BashOperator(task_id="load_dwd", bash_command="spark-submit dwd.py")
    ods >> dwd
```

2. **部署 DAG 到** `dags_folder`，Scheduler 自动加载。
3. **配置 Connection / Variable** 管理数据库、集群连接与参数。
4. **通过 Web UI** 启停、补跑、查看日志与依赖图。
5. **生产环境** 常用 CeleryExecutor 或 KubernetesExecutor 做分布式 Worker。

### 6. 适用场景

- 大数据离线数仓 T+1 / 小时级调度（Spark、Hive、Presto 任务链）。
- 多系统、多依赖的复杂工作流（ODS → DWD → DWS → 导出）。
- 需要 Code Review、Git 版本管理的工程化数据团队。
- 云原生环境，任务容器化运行在 K8s 上。
- **不适合**：业务人员主导的纯可视化 ETL、轻量级单机定时脚本（过重）。

---

## 二、 Kettle（Pentaho Data Integration，PDI）

### 1. 背景

Kettle 是 Pentaho 开源的数据集成（ETL）工具，后被 Hitachi Vantara 收购。其诞生背景是：**企业数据分散在数据库、文件、ERP 等异构系统中，需要低代码/可视化方式完成抽取、转换、加载**。

Kettle 的核心定位是 **ETL 工具**，调度能力相对较弱，通常需配合 **Carte**、**Pentaho BA Server** 或外部 Cron/Airflow 做定时触发。

### 2. 架构

```text
┌─────────────────────────────────────────────────────────┐
│              Spoon（桌面设计器，可视化开发）                │
├─────────────────────────────────────────────────────────┤
│  转换（Transformation）    │    作业（Job）              │
│  多 Step 并行/串行数据流    │    串行控制流 + 调度逻辑     │
├─────────────────────────────────────────────────────────┤
│  运行时引擎：Kitchen（Job）/ Pan（Transformation）       │
├─────────────────────────────────────────────────────────┤
│  Carte（可选）：轻量 Web 服务，远程执行与简单调度          │
├─────────────────────────────────────────────────────────┤
│  数据源：RDBMS / 文件 / HDFS / Kafka / API 等           │
└─────────────────────────────────────────────────────────┘
```

**核心概念**：

| 概念 | 说明 |
| :--- | :--- |
| **Transformation（转换）** | 数据处理主单元，Step 之间通过 Hop 连接，数据行流动 |
| **Job（作业）** | 编排多个 Transformation/Job，含条件、邮件、FTP 等控制 Step |
| **Step** | 最小处理单元，如表输入、过滤、Join、表输出 |
| **Hop** | Step 之间的连线，决定数据流向 |
| **Spoon** | GUI 设计器，拖拽式开发 |
| **Kitchen / Pan** | 命令行执行 Job / Transformation |
| **Carte** | 远程执行服务，支持简单定时 |

**执行模型**：以 **JVM 进程内 Row Set 流式处理** 为主，数据在 Step 间逐行或批量传递；大数据量场景常成为瓶颈。

### 3. 设计特点

- **可视化低代码**：业务/实施人员可通过拖拽完成 ETL，上手快。
- **Transformation 与 Job 分离**：转换管“怎么处理数据”，作业管“怎么串流程、怎么调度”。
- **异构数据源支持广**：传统数据库、Excel、XML、各类 API 覆盖好。
- **内置丰富转换 Step**：清洗、映射、SCD、JavaScript、正则等。
- **参数化与变量**：支持 `${变量}`、参数传递、配置文件。
- **调度非核心能力**：原生更偏“执行引擎”，企业级调度常外接 Pentaho Server 或其它调度平台。

### 4. 优缺点

**优点**：

- 可视化开发，**实施门槛低**，适合传统 BI/数仓项目。
- 异构源集成能力强，中小数据量 ETL 开发效率高。
- 单机部署简单，无需复杂分布式组件。
- 转换逻辑直观，便于与业务人员沟通。

**缺点**：

- **大数据扩展性差**：基于 JVM 单机/小集群，难以替代 Spark/Flink 处理 PB 级数据。
- **版本管理与协作弱**：XML 格式的 `.ktr/.kjb` 不如 Python/SQL 适合 Git Diff 和 Code Review。
- **企业级调度、监控、权限** 依赖 Pentaho Server 或第三方，原生能力有限。
- **性能与稳定性**：大表 Join、高并发下易出现内存、锁、慢 Step 问题。
- **社区与迭代**：在大数据领域热度下降，云原生支持弱于 Airflow / DolphinScheduler。

### 5. 使用方式

1. **Spoon 中设计 Transformation**：表输入 → 清洗/映射 → 表输出。
2. **设计 Job**：串联多个 Transformation，配置成功/失败分支、邮件通知。
3. **命令行执行**：

```bash
# 执行转换
pan.sh -file=/path/to/load.ktr -param:DATE=20240601

# 执行业务作业
kitchen.sh -file=/path/to/daily_job.kjb -param:DATE=20240601
```

4. **定时**：Linux Cron、Windows 计划任务，或 Carte / Pentaho Server 调度。
5. **生产部署**：可将 Kitchen/Pan 作为 Airflow 的一个 Task 被编排。

### 6. 适用场景

- 传统关系型数据库之间的 ETL、数据迁移、报表层加工。
- 实施/运维人员主导、数据量中小（百万~千万级）的项目。
- 需要快速对接 Excel、XML、各类 JDBC 源的场景。
- 作为 **局部 ETL 工具**，被 Airflow 等调度平台调用。
- **不适合**：海量离线数仓主链路、实时流处理、云原生大规模任务编排。

---

## 三、 Apache DolphinScheduler

### 1. 背景

Apache DolphinScheduler（海豚调度）最初由易观（Analysys）2017 年开源，2019 年进入 Apache 孵化器，2023 年成为 Apache 顶级项目。其背景是：**国内大数据场景需要一款既支持可视化编排、又具备分布式调度能力、且贴合 Hadoop/Spark 生态的国产调度平台**。

定位介于 Airflow 与 Kettle 之间：**既是工作流调度平台，也内置任务类型与资源中心，更强调“平台化 + 国产化 + 大数据友好”**。

### 2. 架构

```text
┌─────────────────────────────────────────────────────────┐
│  API Server  │  Master Server  │  Worker Server         │
│  (REST/UI)   │  (调度分发)      │  (任务执行)             │
├─────────────────────────────────────────────────────────┤
│  Alert Server  │  Logger Server  │  Registry (ZK)        │
├─────────────────────────────────────────────────────────┤
│  Metadata DB (MySQL/PostgreSQL)                          │
├─────────────────────────────────────────────────────────┤
│  任务类型：Shell / SQL / Spark / Flink / HTTP / 子流程等   │
├─────────────────────────────────────────────────────────┤
│  资源中心：脚本、Jar、配置文件统一管理                      │
└─────────────────────────────────────────────────────────┘
```

**核心组件**：

| 组件 | 作用 |
| :--- | :--- |
| **Master** | 解析 DAG、分片调度、故障转移、任务下发 |
| **Worker** | 执行 Shell、SQL、Spark、Flink 等具体任务 |
| **API** | 提供 REST 接口与 Web UI 后端 |
| **Registry（ZK）** | Master/Worker 注册与选主，保证高可用 |
| **Alert** | 邮件、钉钉、飞书、短信等告警 |
| **资源中心** | 统一管理 UDF、脚本、Jar，避免散落各节点 |

**执行模型**：**去中心化多 Master + 多 Worker**，任务通过 Netty 通信下发；计算型任务（Spark/Flink）由 Worker 提交到 YARN/K8s，平台本身负责编排与状态管理。

### 3. 设计特点

- **可视化 + 低代码**：Web UI 拖拽 DAG，也支持 SQL/Shell 脚本任务。
- **任务类型丰富**：原生支持 Spark、Flink、Hive、SQL、SubProcess、依赖节点等，贴合国内大数据栈。
- **国产友好**：中文文档、钉钉/飞书告警、国内社区活跃，政企项目采用多。
- **资源中心**：脚本/Jar 统一上传与版本管理，运维方便。
- **多租户与权限**：项目、租户、资源组隔离，适合平台化建设。
- **补数与依赖**：支持按日期补跑、跨工作流依赖、优先级与容错策略。
- **高可用设计**：Master 选主、Worker 水平扩展，适合大规模任务调度。

### 4. 优缺点

**优点**：

- **可视化 + 分布式调度** 兼顾，实施与开发都能接受。
- 原生支持 Spark/Flink/Hive，国内大数据场景落地快。
- 运维监控、告警、资源管理、多租户等平台能力较完整。
- 相比 Airflow，**对非 Python 团队更友好**（UI 配置为主）。
- 国产开源，信创、政企项目适配较多。

**缺点**：

- **代码即配置能力弱于 Airflow**：复杂逻辑在 UI 中维护，Git 协作与单元测试不如 Python DAG。
- **国际化与海外生态** 弱于 Airflow。
- **与计算引擎仍耦合在 Worker**：Worker 需配置 Hadoop/Spark 客户端环境。
- **版本升级**：大版本升级需注意 DB 迁移与 API 兼容。
- **超复杂编排**（大量 Sensor、动态分支）表达力略逊于 Airflow。

### 5. 使用方式

1. **Web UI 创建项目** → 工作流（Workflow）→ 拖拽任务节点并连线。
2. **配置任务**：Shell 脚本、Spark SQL 文件、Spark Submit 参数、数据源等。
3. **上传资源**到资源中心（`.sh`、`.sql`、`.jar`）。
4. **设置调度**：Cron 表达式、起止时间、失败策略、告警组。
5. **上线运行**：手动触发、定时调度、补数（按业务日期回溯）。
6. **API 集成**：通过 Open API 与外部系统对接（启停、状态查询）。

典型任务链示例：

```text
Shell(检查分区) → SQL(Hive ODS) → Spark(DWD) → Spark(DWS) → 依赖检查 → 告警
```

### 6. 适用场景

- 国内 Hadoop/Spark/Flink 离线数仓 T+1、小时级调度。
- 需要**可视化平台 + 分布式调度 + 多租户**的企业级数据平台。
- 实施/运维/开发混合团队，不希望全员写 Python DAG。
- 政企、金融等对国产开源、权限审计有要求的项目。
- **不适合**：强依赖 Python 生态的复杂编程式编排；纯轻量 ETL 且无需分布式调度（Kettle 更简单）。

---

## 四、 三者对比

| 维度 | Airflow | Kettle (PDI) | DolphinScheduler |
| :--- | :--- | :--- | :--- |
| **核心定位** | 工作流编排平台 | ETL 数据集成工具 | 可视化分布式调度平台 |
| **开发方式** | Python 代码定义 DAG | GUI 拖拽（Spoon） | Web UI 拖拽 + 脚本 |
| **是否自带 ETL** | 否（调用外部引擎） | 是（核心能力） | 否（以 Shell/SQL/Spark 为主） |
| **架构** | Scheduler + Executor + Worker | Spoon + Kitchen/Pan + Carte | Master + Worker + ZK |
| **分布式能力** | 强（Celery/K8s） | 弱（偏单机/小集群） | 强（原生多 Master/Worker） |
| **大数据适配** | 强（Spark/Hive 生态） | 弱（JVM 内存瓶颈） | 强（原生 Spark/Flink 任务） |
| **可视化** | Web 监控为主，DAG 靠代码 | 强（设计器为核心） | 强（设计+运维一体） |
| **版本管理** | Git + Python，工程化好 | XML 文件，协作一般 | UI/DB 为主，代码化弱 |
| **学习成本** | 高 | 低~中 | 中 |
| **社区/生态** | 国际主流，最活跃 | 传统 BI 领域，热度下降 | 国内大数据领域活跃 |
| **典型用户** | 数据平台/工程团队 | 实施/BI/传统 ETL | 国内数仓/数据中台团队 |

### 选型建议（一句话）

```text
复杂编排 + Python 工程化 + 云原生          → Airflow
异构源中小数据量可视化 ETL                  → Kettle
国内大数据离线调度 + 可视化平台 + 多租户    → DolphinScheduler
```

### 组合使用（生产常见）

- **Airflow / DolphinScheduler 调度 + Kettle 做局部 ETL**：平台管编排，Kettle 管特定异构源转换。
- **Airflow / DolphinScheduler 调度 + Spark SQL 文件**：大数据数仓主流做法，Kettle 逐步退出主链路。

---

## 五、 面试高频知识点

### Q1：Airflow 中 DAG、Task、Operator、Executor 分别是什么？

**理解思路**：

- **DAG**：工作流定义，描述 Task 及依赖，无环。
- **Task**：DAG 中的一个节点实例化后的执行单元（Task Instance）。
- **Operator**：Task 的模板/类型，定义“做什么”（Bash、Spark、Python 等）。
- **Executor**：调度策略，决定 Task 在哪个 Worker 进程/容器执行（Local/Celery/K8s）。

### Q2：Airflow 的 `execution_date` 和实际运行时间有什么区别？

**理解思路**：

- `execution_date`（Airflow 2.2+ 也称 logical date）表示**数据所属的业务周期**，不是 Task 真正开始跑的时间。
- 例如 `schedule="0 2 * * *"` 的日任务，`execution_date = 2024-06-01` 的任务通常在 **6 月 2 日凌晨 2 点** 触发，处理的是 6 月 1 日的数据。
- 补数（backfill）时按 `execution_date` 逐日生成 DAG Run，这是面试常考点。

### Q3：Kettle 中 Transformation 和 Job 的区别？

**理解思路**：

- **Transformation**：数据驱动，Step 间传递数据行（Row），负责 ETL 转换逻辑。
- **Job**：控制驱动，按成功/失败路径串行执行 Transformation 或其它 Job，负责流程编排、邮件、FTP 等。
- 类比：Transformation ≈ 数据处理函数；Job ≈ 工作流控制器。

### Q4：为什么 Kettle 不适合做大数据离线数仓主链路？

**理解思路**：

- 基于 JVM 单机内存流式处理，缺乏 Spark 级别的分布式计算与 Shuffle 优化。
- 大表 Join、聚合易 OOM，吞吐远低于 Spark/Hive。
- 企业级调度、资源隔离、任务优先级不如专用调度平台。
- 现代数仓普遍“调度平台 + Spark SQL”，Kettle 更适合中小规模异构集成。

### Q5：DolphinScheduler 的 Master 和 Worker 如何协作？

**理解思路**：

- **Master**：负责工作流解析、定时触发、任务分片、下发到 Worker、状态汇总与容错。
- **Worker**：接收任务，执行 Shell/SQL/Spark 等，上报状态与日志。
- **ZK**：Master 选主、节点注册，避免双 Master 同时调度。
- Master 不执行具体计算，Worker 可水平扩展，计算任务再提交 YARN/K8s。

### Q6：Airflow 与 DolphinScheduler 如何选型？

**理解思路**：

| 选 Airflow | 选 DolphinScheduler |
| :--- | :--- |
| 团队 Python 能力强 | 团队更习惯 UI 配置 |
| 复杂 Sensor、动态 DAG | 国内 Spark/Hive 标准调度 |
| 云原生 K8s 部署 | 需要多租户、资源中心、国产支持 |
| 国际化、插件生态 | 政企平台化、钉钉告警 |

### Q7：调度平台如何保证任务不重跑/不丢跑？

**理解思路**：

- **不重跑（幂等）**：任务设计幂等（分区覆盖写入）；平台层用 `max_active_runs`、任务实例唯一键避免重复提交。
- **不丢跑**：Metadata DB 持久化 DAG Run 状态；失败重试 + 告警；Worker 心跳与 Master 故障转移。
- **Exactly-Once 语义**：调度平台通常保证“至少一次”，业务层需自己保证幂等（如 `INSERT OVERWRITE PARTITION`）。

### Q8：什么是任务依赖中的 Sensor？Airflow 里怎么用？

**理解思路**：

- **Sensor** 是一种特殊 Operator，持续等待某个条件满足（如 Hive 分区就绪、上游文件到达、外部 DAG 成功）。
- 满足后才触发下游，解决“时间到了但数据未就绪”的问题。
- 缺点：占用 Worker 槽位轮询，Airflow 2.2+ 引入 Deferrable Operator 异步等待以节省资源。

### Q9：Cron 表达式 `0 2 * * *` 在调度里表示什么？

**理解思路**：

- 标准 5 位：`分 时 日 月 周` → 每天凌晨 2:00 触发。
- 需结合平台的**时区**（Airflow 默认 UTC，国内常设 `Asia/Shanghai`）。
- DolphinScheduler / Airflow 均支持 Cron，但 `execution_date` 与触发时间的对应关系在 Airflow 中需额外说明。

### Q10：生产环境调度平台需要关注哪些运维点？

**理解思路**：

1. **高可用**：Scheduler/Master 多实例、DB 主从、ZK 集群。
2. **性能**：Metadata DB 索引、历史数据清理、Worker 数量与队列。
3. **告警**：失败重试次数、超时 Kill、钉钉/邮件/on-call。
4. **补数**：按业务日期批量回溯，控制并发避免打满集群。
5. **权限与审计**：谁可以上线 DAG、谁可以 Kill 任务。
6. **资源隔离**：队列/YARN 队列/K8s Namespace，避免任务互相抢资源。

---

## 六、 总结

| 工具 | 一句话概括 |
| :--- | :--- |
| **Airflow** | 以 Python 为核心的国际化工作流编排标准，适合工程化大数据调度。 |
| **Kettle** | 可视化 ETL 工具，擅长异构源中小数据集成，调度需外接。 |
| **DolphinScheduler** | 国产可视化分布式调度平台，贴合 Spark/Hive 与国内平台化需求。 |

在实际数仓项目中，**调度平台（Airflow / DolphinScheduler）+ 计算引擎（Spark/Hive）** 已是主流；Kettle 更多出现在传统 BI、数据迁移或局部 ETL 场景。面试中除工具本身，还应结合**依赖设计、补数、幂等、失败重试、高可用**等通用调度知识一并作答。
