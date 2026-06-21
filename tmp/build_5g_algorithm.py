# -*- coding: utf-8 -*-
"""Generate 5g_algorithm/*.sql from sql_file + naming mapping + rules in 需求处理文档."""
import re
import shutil
from pathlib import Path

ROOT = Path(
    "E:/DTSW/\u4e1a\u52a1\u6587\u6863/\u9700\u6c42\u5b9e\u73b0/2025\u5e74\u9700\u6c42/"
    "\u7f51\u7edc\u6570\u636e\u5904\u7406\u7cfb\u7edf/20251103-\u4e2d\u53f0H3\u4efb\u52a1\u8fc1\u79fb"
)
DOC = ROOT / "45G_MR\u6a21\u578b\u6807\u51c6\u5316\u8bbe\u8ba1\u6587\u6863"
SQL_SRC = ROOT / "\u79bb\u7ebf\u4efb\u52a1\u6b63\u5f0f\u8fc1\u79fb" / "sql_file"
OUT_DIR = DOC / "5g_algorithm"
TASK_LIST = DOC / "5g\u4efb\u52a1\u5347\u7ea7\u6e05\u5355.txt"

SQL_KW_AFTER_FROM = frozenset({"select", "lateral", "unnest", "values", "table"})
SKIP_TABLE_PREFIXES = ("tmp_", "temp_", "tmp.", "temp.", "cache_")


def replace_partition_vars(text: str) -> str:
    text = re.sub(r"'[ \t]*\$[a-zA-Z0-9_]+\.p_date\$[ \t]*'", "'${p_date}'", text)
    text = re.sub(r"\$[a-zA-Z0-9_]+\.p_provincecode\$", "${p_provincecode}", text)
    text = re.sub(r"\$[a-zA-Z0-9_]+\.p_date\$", "${p_date}", text)
    text = re.sub(r"\$[a-zA-Z0-9_]+\.p_hour\$", "${p_hour}", text)
    text = re.sub(r"\$[a-zA-Z0-9_]+\.p_quarter\$", "${p_quarter}", text)
    text = re.sub(r"\$[a-zA-Z0-9_]+\.p_year\$", "${p_year}", text)
    text = re.sub(r"\$[a-zA-Z0-9_]+\.p_month\$", "${p_month}", text)
    text = re.sub(r"\$[a-zA-Z0-9_]+\.p_week\$", "${p_week}", text)
    return text


def quote_p_date_only(text: str) -> str:
    """p_date 统一按字符串分区/筛选写法加引号。"""
    text = text.replace("'${p_date}'", "__P_DATE_MARK__")
    text = text.replace("${p_date}", "'${p_date}'")
    text = text.replace("__P_DATE_MARK__", "'${p_date}'")
    return text


def quote_partition_style_eq(text: str) -> str:
    """与算法规则补充一致：insert 静态分区中 p_provincecode/p_hour/p_quarter 使用引号包裹变量。"""
    pairs = [
        ("p_provincecode = ${p_provincecode}", "p_provincecode = '${p_provincecode}'"),
        ("p_hour = ${p_hour}", "p_hour = '${p_hour}'"),
        ("p_quarter = ${p_quarter}", "p_quarter = '${p_quarter}'"),
        ("p_year = ${p_year}", "p_year = '${p_year}'"),
        ("p_month = ${p_month}", "p_month = '${p_month}'"),
        ("p_week = ${p_week}", "p_week = '${p_week}'"),
    ]
    for a, b in pairs:
        text = text.replace(a, b)
    return text


def replace_schema_aliases(text: str) -> str:
    return re.sub(r"(?i)\bzxvmax\.", "dtsw_db.", text)


def replace_dollar_table_placeholders(text: str) -> str:
    def repl(m: re.Match) -> str:
        return "dtsw_db." + m.group(1)

    return re.sub(r"\$([a-zA-Z][a-zA-Z0-9_]*)\$", repl, text)


def should_skip_qualify(name: str) -> bool:
    if not name or name.startswith("dtsw_db"):
        return True
    low = name.lower()
    if low in SQL_KW_AFTER_FROM:
        return True
    for p in SKIP_TABLE_PREFIXES:
        if name.startswith(p):
            return True
    return False


def qualify_bare_tables(text: str) -> str:
    def sub_io(m: re.Match) -> str:
        if should_skip_qualify(m.group(2)):
            return m.group(0)
        return m.group(1) + "dtsw_db." + m.group(2)

    text = re.sub(
        r"(?is)\b(insert\s+overwrite\s+table\s+)(?!dtsw_db\.)([a-zA-Z][a-zA-Z0-9_]*)",
        sub_io,
        text,
    )
    text = re.sub(
        r"(?is)\b(insert\s+into\s+table\s+)(?!dtsw_db\.)([a-zA-Z][a-zA-Z0-9_]*)",
        sub_io,
        text,
    )
    text = re.sub(
        r"(?is)\b(alter\s+table\s+)(?!dtsw_db\.)([a-zA-Z][a-zA-Z0-9_]*)",
        sub_io,
        text,
    )

    def fj(m: re.Match) -> str:
        if should_skip_qualify(m.group(2)):
            return m.group(0)
        return m.group(1) + " dtsw_db." + m.group(2)

    text = re.sub(
        r"(?is)\b(from|join)\s+(?!dtsw_db\.)([a-zA-Z][a-zA-Z0-9_]*)",
        fj,
        text,
    )
    return text


def adapt_one(content: str) -> str:
    content = replace_partition_vars(content)
    content = quote_p_date_only(content)
    content = quote_partition_style_eq(content)
    content = replace_schema_aliases(content)
    content = replace_dollar_table_placeholders(content)
    content = qualify_bare_tables(content)
    return content


def apply_physical_renames(text: str) -> str:
    repls = [
        ("dtsw_db.aggr_nr_coverage_base_usr_refactor_q", "dtsw_db.aggr_nr_coverage_usrcelgrd_q"),
        ("dtsw_db.aggr_nr_coverage_reduce_usrcelgrd_q", "dtsw_db.aggr_nr_coverage_index_reduce_usrcelgrd_q"),
        ("dtsw_db.aggr_nr_coverage_reduce_usrcelgrd_h", "dtsw_db.aggr_nr_coverage_index_reduce_usrcelgrd_h"),
    ]
    for a, b in repls:
        text = text.replace(a, b)
    return text


def rename_entity(text: str, old: str, new: str) -> str:
    return text.replace(old, new)


def build_from_alias(src_stem: str, dest_table: str) -> str:
    raw = (SQL_SRC / f"{src_stem}.sql").read_text(encoding="utf-8", errors="ignore")
    raw = rename_entity(raw, src_stem, dest_table)
    raw = adapt_one(raw)
    raw = apply_physical_renames(raw)
    return raw


def hdr(algorithm_cn: str, extra: str = "") -> str:
    lines = [
        "-- create_time：2026-04-14",
        "-- author:zhangyutong",
        f"-- algorithm: {algorithm_cn}",
        "-- comment : 5G MR模型标准化迁移：sql_file适配+dtsw_db+分区变量，输出至5g_algorithm",
    ]
    if extra:
        lines.append(extra)
    lines.append("-- Generated By AI Start (Cursor)")
    return "\n".join(lines) + "\n"


def ftr() -> str:
    return "\n-- Generated By AI End (Cursor)\n"


def sql_fact_nr_mro_index_reduce_q() -> str:
    body = """set spark.sql.adaptive.enabled = true;
set spark.sql.adaptive.minNumPostShufflePartitions = 1;
set spark.sql.adaptive.maxNumPostShufflePartitions = 1000;
set spark.sql.adaptive.shuffle.targetPostShuffleInputSize = 512435456;
set spark.sql.adaptive.shuffle.targetPostShuffleRowCount = 100000000;

insert overwrite table dtsw_db.fact_nr_mro_index_reduce_q partition
(
    p_provincecode = '${p_provincecode}'
    ,p_date = '${p_date}'
    ,p_hour = '${p_hour}'
    ,p_quarter = '${p_quarter}'
)
select
     A1.datetime
    ,A1.imsi
    ,A1.msisdn
    ,A1.imei
    ,A1.gnbid
    ,A1.cellid
    ,A1.p_provincecode as provincecode
    ,A1.mrlon
    ,A1.mrlat
    ,A1.locationtype
    ,A1.p_provincecode
    ,A1.p_date
    ,A1.p_hour
    ,A1.p_quarter
from
    dtsw_db.ods_nr_mro_northctcc_q A1
where
    A1.p_provincecode = '${p_provincecode}'
    and A1.p_date = '${p_date}'
    and A1.p_hour = '${p_hour}'
    and A1.p_quarter = '${p_quarter}'
;
"""
    return hdr("5G电联MRO详单字段裁剪表") + body + ftr()


def ph(table: str, note: str) -> str:
    return (
        hdr(table, "-- update comment : " + note)
        + f"-- 待补齐：{note}\nselect 1 as _placeholder where 1 = 0;\n"
        + ftr()
    )


ALIAS_MAP: dict[str, str] = {
    "aggr_nr_coveragr_problem_sncell_h": "aggr_nr_sncell_problem_h",
    "aggr_nr_coveragr_problem_sncell_d": "aggr_nr_sncell_problem_d",
    "aggr_nr_coverage_usrcelgrd_q": "aggr_nr_coverage_base_usr_refactor_q",
    "aggr_nr_coverage_index_reduce_usrcelgrd_q": "aggr_nr_coverage_reduce_usrcelgrd_q",
    "aggr_nr_coverage_index_reduce_usrcelgrd_h": "aggr_nr_coverage_reduce_usrcelgrd_h",
    "aggr_nr_coverage_usrareagrd_d": "aggr_nr_usrareagrd_d",
    "aggr_nr_coverage_celgrd_h": "aggr_nr_coverage_celgrd_refactor_h",
    "aggr_nr_coverage_usrcel_h": "aggr_nr_coverage_usrcel_refactor_h",
    "aggr_nr_coverage_cel_h": "aggr_nr_coverage_cel_refactor_h",
    "aggr_nr_coverage_index_reduce_cel_h": "aggr_nr_coverage_reduce_cel_h",
    "aggr_nr_coverage_grd_h": "aggr_nr_coverage_grd_refactor_h",
    "aggr_nr_coverage_celgrd_d": "aggr_nr_coverage_celgrd_refactor_d",
    "aggr_nr_coverage_cel_d": "aggr_nr_coverage_cel_refactor_d",
    "aggr_nr_coverage_grd_d": "aggr_nr_coverage_grd_refactor_d",
    "aggr_nr_coverage_usrcel_d": "aggr_nr_coverage_usrcel_refactor_d",
    "aggr_nr_coverage_usr_d": "aggr_nr_coverage_usr_refactor_d",
    "aggr_nr_coverage_usrgrd_d": "aggr_nr_coverage_usrgrd_refactor_d",
}


PLACEHOLDER_TASKS = {
    "aggr_nr_coverage_base_h": "小时表需由aggr_nr_coverage_base_q按模型汇总，sql_file无同名脚本",
    "aggr_nr_coverage_index_reduce_cel_d": "裁剪天表需由aggr_nr_coverage_cel_d按模型汇总，sql_file无同名脚本",
    "aggr_nr_coverage_index_reduce_usrcel_h": "需由aggr_nr_coverage_usrcel_h裁剪汇总，sql_file无同名脚本",
    "aggr_nr_coverage_index_reduce_celgrd_q": "删减15分钟表需由aggr_nr_coverage_usrcelgrd_q按模型加工，sql_file无同名脚本",
    "aggr_nr_usr_perception_usrcelarea_d": "多源关联与窗口逻辑，见文档_toon/17_*.toon",
    "aggr_nr_usr_perception_coverage_usrcelarea_d": "源为usr_perception_usrcelarea_d，见文档_toon/17.1_*.toon",
    "aggr_nr_highrail_coverage_usrcelgrd_h": "高铁多源关联，见文档_toon/38_*.toon",
    "aggr_nr_highrail_coverage_celgrd_d": "高铁多源关联，见文档_toon/39_*.toon",
    "dq_aggr_nr_coverage_rsrp_celgrd_d": "模型标注附件SQL，需按稽核平台表结构补充",
    "dq_fact_nr_mro_index_reduce_q": "模型标注附件SQL，需按稽核平台表结构补充",
}


def main() -> None:
    tasks = [ln.strip() for ln in TASK_LIST.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for t in tasks:
        out = OUT_DIR / f"{t}.sql"
        if t == "fact_nr_mro_index_reduce_q":
            out.write_text(sql_fact_nr_mro_index_reduce_q(), encoding="utf-8")
            continue
        if t in ALIAS_MAP:
            stem = ALIAS_MAP[t]
            if not (SQL_SRC / f"{stem}.sql").exists():
                out.write_text(ph(t, f"映射源不存在: {stem}.sql"), encoding="utf-8")
                continue
            out.write_text(hdr(t) + build_from_alias(stem, t) + ftr(), encoding="utf-8")
            continue
        if t in PLACEHOLDER_TASKS:
            out.write_text(ph(t, PLACEHOLDER_TASKS[t]), encoding="utf-8")
            continue
        src = SQL_SRC / f"{t}.sql"
        if src.exists():
            txt = adapt_one(src.read_text(encoding="utf-8", errors="ignore"))
            txt = apply_physical_renames(txt)
            out.write_text(hdr(t) + txt + ftr(), encoding="utf-8")
        else:
            out.write_text(ph(t, "sql_file中无同名脚本且无映射"), encoding="utf-8")

    n = len(list(OUT_DIR.glob("*.sql")))
    print("OK", n, "files ->", OUT_DIR)


if __name__ == "__main__":
    main()
