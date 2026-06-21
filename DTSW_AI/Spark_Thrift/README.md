# Spark Thrift 工具分享包

本目录可**整包压缩**分发，用于演示「SQL 写完后在 POC 集群上快速冒烟」。

| 路径 | 说明 |
|------|------|
| **`Spark_Thrift工具使用说明.md`** | 安装、两文件模型、命令、库名、退出码（**先看这个**） |
| **`tool/`** | `validate_sql_thrift.py` 及依赖，默认头 `sql_header.sql` |
| **`skill/dito-spark-thrift-validate/`** | 拷到个人工程 `.cursor/skills/` 后，AI 可按说明代跑 Thrift |

## 快速开始

```powershell
cd tool
pip install -r requirements.txt
# 编辑 sql_header.sql 中的账期等变量后：
python validate_sql_thrift.py -f 你的脚本.sql
```

未指定 `--header` 时自动拼接同目录下的 **`sql_header.sql`**（含 `USE`、变量、可选 UDF）。

## 与工作区完整工程的关系

- 日常开发仍以工作区 `tools/spark/spark-thrift-validate/` 为准（与本包 `tool/` 同源，可定期同步）。
- 本包**不含**业务 SQL 与 demo 样例，仅工具 + Skill + 使用说明。
