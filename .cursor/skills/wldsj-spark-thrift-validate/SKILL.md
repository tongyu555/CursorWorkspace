---
name: wldsj-spark-thrift-validate
description: >-
  Runs WLDSJ Spark SQL smoke tests via PyHive (validate_sql_thrift.py) on POC
  database wldsj_jt_zxvmax. Two files only: sql_header.sql (USE, vars, UDF) + body
  SQL via -f. When reporting to the user, use zxvmax naming (not wldsj_jt_zxvmax).
---

# WLDSJ Spark Thrift SQL 验证

## 触发

- Thrift 冒烟 / 阶段 4.5 / POC 测 SQL
- `sql-review` 之后、正式自测之前

## 两文件模型

| 文件 | 作用 |
|------|------|
| **`sql_header.sql`** | `USE wldsj_jt_zxvmax`、账期 `set hivevar:…`、可选 `ADD JAR` / `CREATE TEMPORARY FUNCTION` |
| **本体 `.sql`** | `-f` 指定；只放业务语句，每条一行、行末 `;` |

默认头：与 `validate_sql_thrift.py` 同目录的 `sql_header.sql`（可用 `--header` 覆盖）。

## 库名

| 场景 | 库名 |
|------|------|
| Thrift 实跑（头文件 `USE`、脚本内表名） | `wldsj_jt_zxvmax` |
| 向用户汇报 | **`zxvmax`**（说明：POC 实跑 wldsj_jt_zxvmax，对应生产 zxvmax |

## 命令

```powershell
cd <tool目录>
python validate_sql_thrift.py -f <本体.sql>
python validate_sql_thrift.py -f <本体.sql> --header <sql_header.sql> --json
python validate_sql_thrift.py -f <write.sql> --allow-write   # 须用户审批
```

## exit 码

| exit | 处理 |
|------|------|
| 0 | 成功 |
| 1 | 看 `runs/.../result.txt` 或 `statement_log.md` |
| 3 | 写操作被拦 → `--allow-write` 或改只读脚本 |

## 归档

默认 `tool/runs/YYYY-MM-DD/<脚本名>_时间戳/`。向用户汇报时引用 `zxvmax` 表名。

## 连接

- `172.18.2.127:10016`，user `hdfs`
- 工具目录：`DTSW_AI/Spark_Thrift/tool/`

## 常见问题

| 现象 | 处理 |
|------|------|
| `Table not found: zxvmax.xxx` | 头文件应为 `USE wldsj_jt_zxvmax`，表名勿写生产库前缀 |
| INSERT 未执行 exit=0 | `SET` 与 `INSERT` 同一行 → 拆成两行 |
| 对用户说了 wldsj_jt_zxvmax | 改述为 zxvmax + POC 映射说明 |
