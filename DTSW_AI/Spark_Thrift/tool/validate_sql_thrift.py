#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""经 Spark Thrift 校验 SQL（pyhive）。连接参数见下方 THRIFT_*。"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from sql_risk_guard import RiskFinding, has_block, has_warn, scan_all  # noqa: E402

# 集群 Spark Thrift（pocdeploytest-4）
THRIFT_HOST = "172.18.2.127"
THRIFT_PORT = 10016
THRIFT_USER = "hdfs"
THRIFT_DATABASE = "default"
MAX_DISPLAY_ROWS = 50
DEFAULT_HEADER = os.path.join(_SCRIPT_DIR, "sql_header.sql")
TOOL_RUNS_DIR = os.path.join(_SCRIPT_DIR, "runs")
# 兼容旧名
RUNS_DIR = TOOL_RUNS_DIR


def resolve_project_thrift_dir(path: Optional[str]) -> Optional[str]:
    """从 SQL 路径向上查找 …/005_自测SQL/thrift 目录。"""
    if not path:
        return None
    cur = os.path.dirname(os.path.abspath(path))
    while cur and cur != os.path.dirname(cur):
        if (
            os.path.basename(cur).lower() == "thrift"
            and os.path.basename(os.path.dirname(cur)) == "005_自测SQL"
        ):
            return cur
        cur = os.path.dirname(cur)
    return None


def resolve_runs_root(
    body_path: Optional[str],
    header_path: Optional[str],
    archive_dir: Optional[str],
) -> tuple[str, str]:
    """
    解析运行归档根目录。
    返回 (runs_root, archive_source)：archive_source 为 project_thrift | archive_dir | tool_default。
    """
    if archive_dir:
        return os.path.abspath(archive_dir), "archive_dir"
    thrift_dir = resolve_project_thrift_dir(body_path) or resolve_project_thrift_dir(
        header_path
    )
    if thrift_dir:
        return os.path.join(thrift_dir, "runs"), "project_thrift"
    return TOOL_RUNS_DIR, "tool_default"


def format_result_table(columns, rows: list) -> List[str]:
    if not rows:
        return []
    col_names = []
    if columns:
        for c in columns:
            col_names.append(c[0] if isinstance(c, (list, tuple)) else str(c))
    lines: List[str] = []
    if col_names:
        lines.append("\t".join(col_names))
    shown = rows[:MAX_DISPLAY_ROWS]
    for row in shown:
        lines.append("\t".join("" if v is None else str(v) for v in row))
    if len(rows) > MAX_DISPLAY_ROWS:
        lines.append("... ({} more rows)".format(len(rows) - MAX_DISPLAY_ROWS))
    return lines


def split_sql(text: str) -> List[str]:
    parts: List[str] = []
    buf: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buf.append(line)
        if stripped.endswith(";"):
            parts.append("\n".join(buf))
            buf = []
    if buf:
        parts.append("\n".join(buf))
    out: List[str] = []
    for p in parts:
        stmt = p.strip().rstrip(";").strip()
        if stmt:
            out.append(stmt)
    return out


def read_sql_file(path: str) -> str:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def merge_sql(header: str, body: str) -> str:
    h = header.strip()
    b = body.strip()
    if not h:
        return b
    if not b:
        return h
    return h + "\n\n" + b


def resolve_header_path(header_arg: Optional[str], no_header: bool) -> Optional[str]:
    if no_header:
        return None
    if header_arg:
        return header_arg
    if os.path.isfile(DEFAULT_HEADER):
        return DEFAULT_HEADER
    return None


def load_sql(
    file_path: Optional[str],
    execute: Optional[str],
    header_path: Optional[str] = None,
    no_header: bool = False,
) -> tuple[str, Optional[str], Optional[str]]:
    if file_path and execute:
        raise ValueError("use -f or -e, not both")
    if file_path:
        body_path = os.path.abspath(file_path)
        body = read_sql_file(body_path)
        hp = resolve_header_path(header_path, no_header)
        if hp:
            return merge_sql(read_sql_file(hp), body), hp, body_path
        return body, None, body_path
    if execute:
        return execute, None, None
    raise ValueError("use -f/--file or -e/--execute")


def run_time_suffix(now: Optional[datetime] = None) -> str:
    """YYYYMMDD_HHMMSS_mmm（毫秒）。"""
    t = now or datetime.now()
    ms = t.microsecond // 1000
    return t.strftime("%Y%m%d_%H%M%S") + "_{:03d}".format(ms)


def make_run_dir(
    body_path: Optional[str],
    runs_root: str,
    inline: bool = False,
) -> str:
    now = datetime.now()
    date_part = now.strftime("%Y-%m-%d")
    stamp = run_time_suffix(now)
    if inline or not body_path:
        name = "inline_{}".format(stamp)
    else:
        base = os.path.splitext(os.path.basename(body_path))[0]
        name = "{}_{}".format(base, stamp)
    run_dir = os.path.join(runs_root, date_part, name)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def thrift_meta() -> Dict[str, Any]:
    return {
        "host": THRIFT_HOST,
        "port": THRIFT_PORT,
        "user": THRIFT_USER,
        "database": THRIFT_DATABASE,
    }


def archive_run_start(
    run_dir: str,
    merged: str,
    body_path: Optional[str],
    header_path: Optional[str],
    allow_write: bool,
    runs_root: Optional[str] = None,
    archive_source: Optional[str] = None,
) -> str:
    merged_path = os.path.join(run_dir, "merged.sql")
    with open(merged_path, "w", encoding="utf-8") as f:
        f.write(merged)
    if body_path and os.path.isfile(body_path):
        shutil.copy2(body_path, os.path.join(run_dir, "body.sql"))
    if header_path and os.path.isfile(header_path):
        shutil.copy2(header_path, os.path.join(run_dir, "header.sql"))
    meta = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "run_dir": run_dir,
        "runs_root": runs_root,
        "archive_source": archive_source,
        "body_path": body_path,
        "header_path": header_path,
        "merged_path": merged_path,
        "thrift": thrift_meta(),
        "allow_write": allow_write,
        "exit_code": None,
        "ok": None,
        "statements": None,
    }
    _write_run_json(run_dir, meta)
    return merged_path


def _write_run_json(run_dir: str, meta: Dict[str, Any]) -> None:
    with open(os.path.join(run_dir, "run.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def serialize_result_row(r: dict) -> dict:
    item: Dict[str, Any] = {
        "index": r.get("index"),
        "ok": r.get("ok"),
        "rows": r.get("rows"),
        "sec": r.get("sec"),
        "error": r.get("error"),
        "sql": r.get("sql"),
    }
    if r.get("columns"):
        item["columns"] = [
            c[0] if isinstance(c, (list, tuple)) else str(c) for c in r["columns"]
        ]
    if r.get("data") is not None:
        item["data"] = [["" if v is None else str(v) for v in row] for row in r["data"]]
    return item


def format_results_lines(findings: List[RiskFinding], results: list) -> List[str]:
    lines: List[str] = []
    for f in findings:
        lines.append(
            "[{}] #{} {} — {}".format(f.risk_level, f.statement_index, f.rule_id, f.detail)
        )
    lines.append(
        "hive2://{}:{}/{} user={}".format(
            THRIFT_HOST, THRIFT_PORT, THRIFT_DATABASE, THRIFT_USER
        )
    )
    for r in results:
        if r.get("ok"):
            extra = " rows={}".format(r["rows"]) if "rows" in r else ""
            lines.append(
                "[OK] #{} ({:.3f}s){} {}".format(
                    r["index"], r["sec"], extra, (r.get("sql") or "")[:200]
                )
            )
            if r.get("data"):
                for line in format_result_table(r.get("columns"), r["data"]):
                    lines.append("       {}".format(line))
        else:
            lines.append(
                "[FAIL] #{} ({:.3f}s) {}".format(
                    r["index"], r["sec"], (r.get("sql") or "")[:200]
                )
            )
            if r.get("error"):
                lines.append("       {}".format(r["error"]))
    return lines


def _sql_kind(sql: str) -> str:
    u = sql.lstrip().upper()
    for kw in (
        "SET ",
        "USE ",
        "CREATE ",
        "INSERT ",
        "DROP ",
        "SELECT ",
        "ALTER ",
        "SHOW ",
        "DESCRIBE ",
    ):
        if u.startswith(kw.strip()):
            return kw.strip().rstrip()
    return "OTHER"


def save_statement_log(
    run_dir: str,
    exit_code: int,
    ok: Optional[bool],
    findings: List[RiskFinding],
    results: list,
    blocked: bool = False,
) -> str:
    """逐条语句执行日志（Markdown），与 result.txt 同目录。"""
    path = os.path.join(run_dir, "statement_log.md")
    lines: List[str] = [
        "# Spark Thrift 逐条执行日志",
        "",
        "- exit_code: `{}`".format(exit_code),
        "- ok: `{}`".format(ok),
        "- blocked: `{}`".format(blocked),
        "- endpoint: `hive2://{}:{}/{}` user=`{}`".format(
            THRIFT_HOST, THRIFT_PORT, THRIFT_DATABASE, THRIFT_USER
        ),
        "",
    ]
    if findings:
        lines.append("## 风控扫描")
        lines.append("")
        lines.append("| # | 级别 | 规则 | 说明 |")
        lines.append("|---|------|------|------|")
        for f in findings:
            lines.append(
                "| {} | {} | {} | {} |".format(
                    f.statement_index, f.risk_level, f.rule_id, f.detail.replace("|", "\\|")
                )
            )
        lines.append("")
    lines.append("## 语句执行明细")
    lines.append("")
    for r in results:
        idx = r.get("index")
        status = "OK" if r.get("ok") else "FAIL"
        kind = _sql_kind(r.get("sql") or "")
        sec = r.get("sec", 0)
        lines.append("### #{} [{}] {} ({:.3f}s)".format(idx, status, kind, sec))
        lines.append("")
        if r.get("ok") and "rows" in r:
            lines.append("- 返回行数: `{}`".format(r["rows"]))
        if r.get("error"):
            err = str(r["error"])
            if len(err) > 800:
                err = err[:800] + "…(truncated)"
            lines.append("- 错误: `{}`".format(err.replace("`", "'")))
        lines.append("")
        lines.append("```sql")
        lines.append((r.get("sql") or "").strip())
        lines.append("```")
        lines.append("")
        if r.get("ok") and r.get("data"):
            lines.append("<details><summary>结果预览（最多 {} 行）</summary>".format(MAX_DISPLAY_ROWS))
            lines.append("")
            lines.append("```")
            for line in format_result_table(r.get("columns"), r["data"]):
                lines.append(line)
            lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def save_run_results(
    run_dir: str,
    exit_code: int,
    ok: Optional[bool],
    findings: List[RiskFinding],
    results: Optional[list],
    blocked: bool = False,
) -> Optional[str]:
    payload: Dict[str, Any] = {
        "exit_code": exit_code,
        "ok": ok,
        "blocked": blocked,
        "findings": [f.to_dict() for f in findings],
        "results": [serialize_result_row(r) for r in (results or [])],
    }
    json_path = os.path.join(run_dir, "result.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    txt_path = os.path.join(run_dir, "result.txt")
    header = "exit_code={} ok={} blocked={}\n".format(exit_code, ok, blocked)
    body = "\n".join(format_results_lines(findings, results or []))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(header + body + ("\n" if body else ""))
    log_path: Optional[str] = None
    if results:
        log_path = save_statement_log(
            run_dir, exit_code, ok, findings, results, blocked=blocked
        )
    return log_path


def archive_run_finish(
    run_dir: str,
    exit_code: int,
    ok: Optional[bool],
    results: Optional[list] = None,
    findings: Optional[List[RiskFinding]] = None,
    blocked: bool = False,
) -> None:
    findings = findings or []
    stmt_log_path = save_run_results(
        run_dir, exit_code, ok, findings, results, blocked=blocked
    )
    path = os.path.join(run_dir, "run.json")
    meta: Dict[str, Any] = {}
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    meta["exit_code"] = exit_code
    meta["ok"] = ok
    meta["finished_at"] = datetime.now().isoformat(timespec="milliseconds")
    meta["result_json"] = os.path.join(run_dir, "result.json")
    meta["result_txt"] = os.path.join(run_dir, "result.txt")
    if stmt_log_path:
        meta["statement_log_md"] = stmt_log_path
    if blocked and findings:
        meta["risk_blocked"] = True
        meta["findings"] = [f.to_dict() for f in findings]
    if results is not None:
        meta["statements"] = [
            {
                "index": r.get("index"),
                "ok": r.get("ok"),
                "rows": r.get("rows"),
                "sec": r.get("sec"),
                "error": r.get("error"),
                "sql_preview": (r.get("sql") or "")[:200],
            }
            for r in results
        ]
    _write_run_json(run_dir, meta)


def run_statements(statements: List[str]) -> tuple[bool, list]:
    from pyhive import hive

    results = []
    ok_all = True
    conn = hive.Connection(
        host=THRIFT_HOST,
        port=THRIFT_PORT,
        username=THRIFT_USER,
        database=THRIFT_DATABASE,
    )
    try:
        for i, sql in enumerate(statements, 1):
            t0 = time.time()
            try:
                cur = conn.cursor()
                cur.execute(sql)
                columns = getattr(cur, "description", None)
                try:
                    rows = cur.fetchall()
                    n = len(rows)
                except Exception:
                    rows = []
                    columns = None
                    n = 0
                cur.close()
                elapsed = round(time.time() - t0, 3)
                results.append(
                    {
                        "index": i,
                        "ok": True,
                        "rows": n,
                        "sec": elapsed,
                        "sql": sql,
                        "columns": columns,
                        "data": rows,
                    }
                )
            except Exception as exc:
                ok_all = False
                elapsed = round(time.time() - t0, 3)
                results.append(
                    {"index": i, "ok": False, "error": str(exc), "sec": elapsed, "sql": sql}
                )
    finally:
        conn.close()
    return ok_all and bool(results), results


def print_results(findings: List[RiskFinding], results: list) -> None:
    for line in format_results_lines(findings, results):
        print(line)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Validate SQL via Spark Thrift")
    p.add_argument("-f", "--file", help="SQL body file")
    p.add_argument("-e", "--execute", help="SQL string (no header merge)")
    p.add_argument(
        "--header",
        metavar="PATH",
        help="SQL header file (default: sql_header.sql next to this script)",
    )
    p.add_argument("--no-header", action="store_true", help="do not prepend header")
    p.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        help="write merged header+body to file (still runs unless --combine-only)",
    )
    p.add_argument(
        "--combine-only",
        action="store_true",
        help="only merge header+body to -o, do not connect Thrift",
    )
    p.add_argument("--allow-write", action="store_true", help="allow INSERT/CREATE/ALTER on cluster")
    p.add_argument(
        "--allow-rebuild-drop",
        action="store_true",
        help="with --allow-write: allow DROP TABLE (POC 表结构重建，慎用)",
    )
    p.add_argument("--no-archive", action="store_true", help="do not save under runs/")
    p.add_argument(
        "--archive-dir",
        metavar="PATH",
        help="override runs root (default: {需求}/005_自测SQL/thrift/runs if SQL under thrift/, else tool runs/)",
    )
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    run_dir: Optional[str] = None
    body_path: Optional[str] = None

    try:
        text, header_used, body_path = load_sql(
            args.file, args.execute, args.header, args.no_header
        )
    except (ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not args.no_archive:
        runs_root, archive_source = resolve_runs_root(
            body_path, header_used, args.archive_dir
        )
        run_dir = make_run_dir(
            body_path,
            runs_root,
            inline=bool(args.execute and not args.file),
        )
        archive_run_start(
            run_dir,
            text,
            body_path,
            header_used,
            args.allow_write,
            runs_root=runs_root,
            archive_source=archive_source,
        )
        if not args.json:
            print("runs_root: {} ({})".format(runs_root, archive_source))
            print("run: {}".format(run_dir))

    if header_used and not args.json:
        print("header: {}".format(header_used))
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        if not args.json:
            print("merged: {}".format(args.output))
    if args.combine_only:
        if run_dir:
            archive_run_finish(
                run_dir,
                0,
                True,
                results=[{"index": 0, "ok": True, "sec": 0.0, "sql": "(combine-only, not executed)"}],
            )
        return 0

    statements = split_sql(text)
    if not statements:
        print("no SQL statements", file=sys.stderr)
        if run_dir:
            archive_run_finish(run_dir, 2, False)
        return 2

    findings = scan_all(
        statements,
        allow_write=args.allow_write,
        allow_rebuild_drop=args.allow_rebuild_drop,
    )
    if findings and (has_block(findings) or (has_warn(findings) and not args.allow_write)):
        if args.json:
            print(
                json.dumps(
                    {"ok": False, "blocked": True, "findings": [f.to_dict() for f in findings]},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            print_results(findings, [])
        if run_dir:
            archive_run_finish(
                run_dir, 3, False, results=[], findings=findings, blocked=True
            )
        return 3

    try:
        ok, results = run_statements(statements)
    except ImportError as exc:
        print(
            "Missing pyhive: {}. pip install -r requirements.txt".format(exc),
            file=sys.stderr,
        )
        if run_dir:
            archive_run_finish(run_dir, 2, False)
        return 2
    except Exception as exc:
        print("connection failed: {}".format(exc), file=sys.stderr)
        if run_dir:
            archive_run_finish(
                run_dir,
                1,
                False,
                results=[{"index": 0, "ok": False, "error": str(exc), "sql": "(connection)"}],
            )
        return 1

    exit_code = 0 if ok else 1
    if run_dir:
        archive_run_finish(run_dir, exit_code, ok, results=results, findings=findings)

    if args.json:
        out = []
        for r in results:
            item = dict(r)
            if item.get("columns"):
                item["columns"] = [
                    c[0] if isinstance(c, (list, tuple)) else str(c) for c in item["columns"]
                ]
            if item.get("data"):
                item["data"] = [["" if v is None else str(v) for v in row] for row in item["data"]]
            out.append(item)
        payload: Dict[str, Any] = {
            "ok": ok,
            "run_dir": run_dir,
            "findings": [f.to_dict() for f in findings],
            "results": out,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_results(findings, results)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
