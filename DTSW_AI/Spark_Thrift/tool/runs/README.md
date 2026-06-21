# runs — 执行归档

由 `validate_sql_thrift.py` 自动写入（`--no-archive` 时不生成）。**可整目录删除**。

```text
runs/YYYY-MM-DD/<本体名>_YYYYMMDD_HHMMSS_mmm/
  merged.sql   body.sql   header.sql
  result.txt   result.json   statement_log.md   run.json
```

`-e` 单行 SQL 时目录名为 `inline_YYYYMMDD_HHMMSS_mmm`。
