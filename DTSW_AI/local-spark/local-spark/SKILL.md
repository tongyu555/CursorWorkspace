# Local Spark 快速测试与执行 (Local Spark Execution)

此 Skill 用于指导如何在 Windows 本地环境中使用内置的 Spark 快速进行建库、建表、数据插入与查询的测试全流程。当需要验证 SQL 逻辑、测试 PySpark 脚本或诊断 Spark 本地环境问题时使用。

## 环境依赖与准备

### 1. Java 环境
**必须安装 Java 8（或 Java 11）**。Spark 2.3.4 推荐使用 Java 8。
- 请确保已安装 JDK 1.8。
- 需要在系统环境变量中配置 `JAVA_HOME`，并将其 `bin` 目录添加到 `Path` 中。
- 验证方式：在终端执行 `java -version`，应能正常输出 Java 1.8.x 的版本信息。

### 2. Python 环境
**必须安装 Python**，并在系统变量中配置好，以支持 `pyspark` 执行。
- 验证方式：在终端执行 `python --version`。

### 3. Hadoop 插件 (Winutils)
由于 Spark 底层依赖 Hadoop 库，在 Windows 上本地执行 Spark 时，如果缺少 Windows 的 Hadoop 支持包，会报错（如 `Failed to locate the winutils binary` 且无法修改文件权限）。
- **文件位置**：将 `winutils.exe` 和 `hadoop.dll` 放置在 Spark 的 `bin` 目录下。
  具体到本项目中，目录路径为：
  `local-spark/local-spark/spark-2.3.4-bin-hadoop2.7/bin/`
- 如果您直接在 `local-spark/local-spark` 根目录下看到了这两个文件，请将它们**复制或移动**到上述的 `bin` 目录中。

## 本地测试流程

本项目在 `local-spark/local-spark` 中提供了一个开箱即用的测试脚本 `test_local_spark.py` 以及测试 SQL 文件 `test_local.sql`。整个流程分为 4 个步骤：建库 → 建表 → 插入数据 → 查询验证。

### 方式一：使用 PySpark 脚本自动化执行

该方式将自动初始化一个带有 Hive 支持的本地 Spark Session，并在当前目录下创建 `spark-warehouse` 以存储数据，随后执行全套 SQL 测试。

1. **进入目录**
   打开终端并进入 `local-spark/local-spark` 目录：
   ```powershell
   cd e:\CursorWorkspace\DTSW_AI\local-spark\local-spark
   ```

2. **设置环境变量并执行**
   在 PowerShell 中运行以下命令，设置好 `SPARK_HOME` 和 `HADOOP_HOME` 后通过 `spark-submit.cmd` 执行：
   ```powershell
   $env:SPARK_HOME="e:\CursorWorkspace\DTSW_AI\local-spark\local-spark\spark-2.3.4-bin-hadoop2.7"
   $env:HADOOP_HOME=$env:SPARK_HOME
   $env:PYTHONIOENCODING="utf-8"
   & "$env:SPARK_HOME\bin\spark-submit.cmd" test_local_spark.py
   ```

### 方式二：使用 Spark-SQL 命令行执行纯 SQL

如果您只想验证纯 SQL 文件，可以直接使用内置的 `spark-sql.cmd`。

1. **准备 SQL 文件**（例如 `test_local.sql`）：
   ```sql
   CREATE DATABASE IF NOT EXISTS local_test_db;
   USE local_test_db;
   
   DROP TABLE IF EXISTS local_test_table;
   CREATE TABLE local_test_table (
       id INT,
       name STRING,
       age INT
   ) USING parquet;
   
   INSERT INTO local_test_table VALUES
   (1, 'Alice', 25),
   (2, 'Bob', 30),
   (3, 'Charlie', 35),
   (4, 'David', 40);
   
   SELECT * FROM local_test_table WHERE age >= 30 ORDER BY id;
   ```

2. **执行 SQL 文件**：
   ```powershell
   $env:SPARK_HOME="e:\CursorWorkspace\DTSW_AI\local-spark\spark-2.3.4-bin-hadoop2.7"
   $env:HADOOP_HOME=$env:SPARK_HOME
   & "$env:SPARK_HOME\bin\spark-sql.cmd" -S -f test_local.sql
   ```
   *注意：使用 `spark-sql` 首次执行时会在执行目录下创建 `metastore_db` 和 `spark-warehouse`。*

## 常见问题
- **报错 `java.io.IOException: (null) entry in command string: null chmod 0733 D:\tmp\hive`**
  **原因**：缺失 `winutils.exe` 或存放位置不对。
  **解决**：确保 `winutils.exe` 和 `hadoop.dll` 已放置在 `spark-2.3.4-bin-hadoop2.7\bin` 目录中，并且配置了 `HADOOP_HOME` 指向 Spark 根目录。
