# -*- coding: utf-8 -*-
"""SQL 风险拦截（供 validate_sql_thrift 使用，独立于平台 DB risk_rules）。"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import List, Optional


@dataclass
class RiskFinding:
    statement_index: int
    risk_level: str  # BLOCK | WARN
    rule_id: str
    detail: str
    sql_preview: str

    def to_dict(self):
        return asdict(self)


# 默认：验证模式仅允许读/元数据类语句；写操作需 --allow-write
_BLOCK_PATTERNS = [
    ("DROP_DATABASE", r"\bDROP\s+DATABASE\b"),
    ("DROP_TABLE", r"\bDROP\s+TABLE\b"),
    ("DROP_VIEW", r"\bDROP\s+VIEW\b"),
    ("TRUNCATE", r"\bTRUNCATE\s+TABLE\b"),
    ("CREATE_DATABASE", r"\bCREATE\s+DATABASE\b"),
    ("GRANT_REVOKE", r"\b(GRANT|REVOKE)\b"),
    ("ALTER_DROP", r"\bALTER\s+TABLE\b.+\bDROP\b"),
]

_WRITE_PATTERNS = [
    ("INSERT", r"\bINSERT\s+(INTO|OVERWRITE)\b"),
    ("CREATE_TABLE", r"\bCREATE\s+TABLE\b"),
    ("ALTER_TABLE", r"\bALTER\s+TABLE\b"),
    ("LOAD_DATA", r"\bLOAD\s+DATA\b"),
    ("MSCK_REPAIR", r"\bMSCK\s+REPAIR\b"),
    ("DELETE", r"\bDELETE\s+FROM\b"),
    ("UPDATE", r"\bUPDATE\b"),
]

_READ_OK_PREFIX = re.compile(
    r"^\s*(SELECT|WITH|SHOW|DESCRIBE|DESC|EXPLAIN|USE|ANALYZE\s+TABLE|REFRESH\s+TABLE|SET"
    r"|ADD\s+JAR|CREATE\s+TEMPORARY\s+FUNCTION|CREATE\s+FUNCTION)\b",
    re.IGNORECASE | re.DOTALL,
)


def _has_where(sql: str) -> bool:
    return bool(re.search(r"\bWHERE\b", sql, re.IGNORECASE))


def _is_temp_table_drop(sql: str) -> bool:
    """DROP cache_/tmp_/temp_ 临时表（ETL 脚本末尾清理）。"""
    m = re.search(
        r"\bDROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?[`']?(\w+)",
        sql,
        re.IGNORECASE,
    )
    if not m:
        return False
    name = m.group(1).lower()
    return name.startswith(("cache_", "tmp_", "temp_"))


def scan_statement(
    sql: str,
    statement_index: int,
    allow_write: bool,
    allow_rebuild_drop: bool = False,
) -> List[RiskFinding]:
    findings: List[RiskFinding] = []
    upper = sql.upper()
    preview = sql[:160].replace("\n", " ")

    for rule_id, pattern in _BLOCK_PATTERNS:
        if rule_id == "DROP_TABLE" and allow_write and (
            _is_temp_table_drop(sql) or allow_rebuild_drop
        ):
            continue
        if re.search(pattern, upper, re.DOTALL):
            findings.append(
                RiskFinding(
                    statement_index=statement_index,
                    risk_level="BLOCK",
                    rule_id=rule_id,
                    detail="禁止执行高危语句: {}".format(rule_id),
                    sql_preview=preview,
                )
            )

    if re.search(r"\bDELETE\s+FROM\b", upper) and not _has_where(sql):
        findings.append(
            RiskFinding(
                statement_index=statement_index,
                risk_level="BLOCK",
                rule_id="DELETE_NO_WHERE",
                detail="DELETE 必须带 WHERE 条件",
                sql_preview=preview,
            )
        )

    if re.search(r"\bUPDATE\b", upper) and not _has_where(sql):
        findings.append(
            RiskFinding(
                statement_index=statement_index,
                risk_level="BLOCK",
                rule_id="UPDATE_NO_WHERE",
                detail="UPDATE 必须带 WHERE 条件",
                sql_preview=preview,
            )
        )

    if allow_write:
        return findings

    if _READ_OK_PREFIX.match(sql):
        return findings

    for rule_id, pattern in _WRITE_PATTERNS:
        if re.search(pattern, upper, re.DOTALL):
            findings.append(
                RiskFinding(
                    statement_index=statement_index,
                    risk_level="WARN",
                    rule_id=rule_id,
                    detail="写操作需加 --allow-write 才允许通过 Thrift 实跑",
                    sql_preview=preview,
                )
            )
            break

    if not findings and not _READ_OK_PREFIX.match(sql):
        findings.append(
            RiskFinding(
                statement_index=statement_index,
                risk_level="WARN",
                rule_id="UNKNOWN_STMT",
                detail="未识别为只读语句，请加 --allow-write 或改为 SELECT/EXPLAIN 验证",
                sql_preview=preview,
            )
        )

    return findings


def _cache_table_names(statements: List[str]) -> set[str]:
    """同脚本内 CACHE TABLE 创建的表名（如 cell_info），允许末尾 DROP 清理。"""
    names: set[str] = set()
    for stmt in statements:
        for m in re.finditer(r"\bcache\s+table\s+[`']?(\w+)", stmt, re.IGNORECASE):
            names.add(m.group(1).lower())
    return names


def _is_cache_session_table_drop(sql: str, cache_names: set[str]) -> bool:
    m = re.search(
        r"\bDROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?[`']?(\w+)",
        sql,
        re.IGNORECASE,
    )
    return bool(m and m.group(1).lower() in cache_names)


def scan_all(
    statements: List[str],
    allow_write: bool = False,
    allow_rebuild_drop: bool = False,
) -> List[RiskFinding]:
    cache_names = _cache_table_names(statements)
    all_findings: List[RiskFinding] = []
    for i, stmt in enumerate(statements, 1):
        findings = scan_statement(stmt, i, allow_write, allow_rebuild_drop=allow_rebuild_drop)
        if allow_write and cache_names:
            findings = [
                f
                for f in findings
                if not (
                    f.rule_id == "DROP_TABLE"
                    and _is_cache_session_table_drop(stmt, cache_names)
                )
            ]
        all_findings.extend(findings)
    return all_findings


def has_block(findings: List[RiskFinding]) -> bool:
    return any(f.risk_level == "BLOCK" for f in findings)


def has_warn(findings: List[RiskFinding]) -> bool:
    return any(f.risk_level == "WARN" for f in findings)
