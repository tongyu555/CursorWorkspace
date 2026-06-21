**# Spark Thrift SQL 验证 — 工具使用说明

通过 **PyHive** 连接 POC 集群 Spark Thrift，在提交正式调度前做**只读冒烟**或（经审批后）**POC 写入**验证。

---

## 1. 文件模型（仅两部分）

| 部分 | 默认文件 | 内容 |
|------|----------|------|
| **头文件（header）** | `tool/sql_header.sql` | `USE` 目标库、账期等 `SET hivevar:…`、按需 `ADD JAR` / `CREATE TEMPORARY FUNCTION` |
| **SQL 本体（body）** | 任意路径，`-f` 指定 | `SELECT` / `SHOW` / `INSERT` 等业务语句；**每条语句单独一行**，行末 `;` |

工具执行时按顺序拼接：**头 + 本体** → `merged.sql`，再逐条提交 Thrift。

- 需要多套头时：复制多份 `sql_header_xxx.sql`，用 `--header` 指定。

---

## 2. 安装

```powershell
cd tool
pip install -r requirements.txt
```

依赖：`pyhive`、`thrift`、`thrift-sasl`、`pure-sasl`（见 `requirements.txt`）。

---

## 3. 连接与库名（DITO POC）

| 项 | 值 |
|----|-----|
| 主机 | `172.18.2.127` |
| 端口 | `10016` |
| 用户 | `hdfs` |
| 头文件中 `USE` | **`jwy_dito_dtsw`**（POC 实跑库） |
| 对外说明 / 文档表名 | **`dtsw`**（与生产库名一致；汇报时勿把 `jwy_dito_dtsw` 当生产库） |

修改连接：编辑 `validate_sql_thrift.py` 顶部 `THRIFT_HOST` / `THRIFT_PORT` / `THRIFT_USER`。

**常见错误**：头文件 `USE jwy_dito_dtsw`，本体里写 `dtsw.表名` → `Table not found`。Thrift 脚本内表名应带 **`jwy_dito_dtsw.`** 或依赖当前 `USE` 后的裸表名。

---

## 4. 默认头文件示例

`tool/sql_header.sql`（可按任务改账期、取消注释 UDF 段）：

```sql
USE jwy_dito_dtsw;

set hivevar:p_date=2026-05-01;

-- ADD JAR hdfs:///user/hdfs/udf/your_udf.jar;
-- CREATE TEMPORARY FUNCTION your_udf AS 'com.example.YourUdf'
-- USING JAR 'hdfs:///user/hdfs/udf/your_udf.jar';
```

---

## 5. 常用命令

### 5.1 只读冒烟（默认）

```powershell
cd tool
python validate_sql_thrift.py -f D:\path\to\validate.sql
```

- 未写 `--header` 时自动使用同目录 **`sql_header.sql`**。
- 写操作（`INSERT`/`CREATE`/`ALTER` 等）会被拦截，exit **3**。

### 5.2 指定头文件

```powershell
python validate_sql_thrift.py -f D:\path\to\validate.sql --header D:\path\to\sql_header.sql
```

### 5.3 不拼接头

```powershell
python validate_sql_thrift.py -f validate.sql --no-header
```

### 5.4 POC 写入（须审批）

```powershell
python validate_sql_thrift.py -f write.sql --allow-write
```

`DROP TABLE` 仅对 `cache_*` / `tmp_*` / `temp_*` 在 `--allow-write` 下放行；`DROP DATABASE`、`TRUNCATE`、无 `WHERE` 的 `DELETE` 等始终拦截。

### 5.5 其它参数

| 参数 | 说明 |
|------|------|
| `-e "SQL"` | 单行 SQL，不读文件 |
| `-o path` | 额外写出合并后的 SQL |
| `--combine-only` | 只合并归档，不连 Thrift |
| `--no-archive` | 不写运行归档 |
| `--json` | 控制台输出 JSON（仍会写 `result.json`） |
| `--archive-dir DIR` | 指定归档根目录（默认 `tool/runs/`） |

---

## 6. 运行归档

每次执行（未加 `--no-archive`）在 **`tool/runs/YYYY-MM-DD/<本体名>_时间戳/`** 生成：

| 文件 | 说明 |
|------|------|
| `merged.sql` | 头 + 本体，实际执行内容 |
| `header.sql` / `body.sql` | 快照 |
| `result.txt` | 可读结果（每条语句 OK/FAIL、错误、查询前几行） |
| `result.json` | 结构化结果 |
| `statement_log.md` | 逐条语句日志（推荐排障看这个） |

`runs/` 可整目录删除，仅本地记录。

---

## 7. 退出码

| exit | 含义 |
|------|------|
| 0 | 成功（0 行可能是账期无数据） |
| 1 | 执行失败，看 `runs/.../result.txt` |
| 2 | 参数错误 |
| 3 | 写操作被风控拦截 → 确认应用 `--allow-write` 或改用只读脚本 |

---

## 8. 与 Cursor Skill

将 **`skill/dito-spark-thrift-validate/`** 复制到工程 **`.cursor/skills/`**，在对话中说「Thrift 冒烟」「阶段 4.5 验证」等，AI 会按本说明拼命令、解读 exit 码，并向用户用 **`dtsw`** 库名汇报。

---

## 9. 语句书写注意

1. **一行一条语句**：不要把 `SET` 和 `INSERT` 写在同一行。
2. **分区类型**：`p_date` 等 string 分区用单引号；`p_hour`、`p_provincecode` 等 int 分区不要引号。
3. Thrift 通过 ≠ 正式环境自测通过；通过只表示 POC 上语法与基本逻辑可跑通。
**