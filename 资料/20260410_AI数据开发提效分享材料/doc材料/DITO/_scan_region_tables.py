# -*- coding: utf-8 -*-
"""One-off scan of 知识库_表资产目录.json for region/geo related tables."""
import json
import re
from pathlib import Path

path = Path(__file__).resolve().parent / "知识库_表资产目录.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
tables = data["tables"]


def table_name_geo_match(tn: str) -> bool:
    t = tn.lower()
    if "rm_area" in t or "cfg_area" in t:
        return True
    parts = t.split("_")
    geo = {"region", "province", "city", "area"}
    for p in parts:
        if p in geo:
            return True
        if p.startswith("region") and len(p) > 6:
            return True
    for pat in [
        r"_region(_|$)",
        r"_province(_|$)",
        r"_city(_|$)",
        r"_area(_|$)",
        r"^province_",
        r"^city_",
        r"^region_",
        r"^area_",
    ]:
        if re.search(pat, t):
            return True
    return False


STRONG_PATTERNS = [
    re.compile(r"^region_id$", re.I),
    re.compile(r"^region_name$", re.I),
    re.compile(r"^region_code$", re.I),
    re.compile(r"^regioncode$", re.I),
    re.compile(r"^regionid$", re.I),
    re.compile(r"^province_id$", re.I),
    re.compile(r"^province_name$", re.I),
    re.compile(r"^province_code$", re.I),
    re.compile(r"^provincecode$", re.I),
    re.compile(r"^city_id$", re.I),
    re.compile(r"^city_name$", re.I),
    re.compile(r"^city_code$", re.I),
    re.compile(r"^citycode$", re.I),
    re.compile(r"^area_id$", re.I),
    re.compile(r"^area_name$", re.I),
    re.compile(r"^areacode$", re.I),
    re.compile(r"^parent_id$", re.I),
    re.compile(r"^rm_area", re.I),
    re.compile(r"^cfg_area", re.I),
    re.compile(r"^home_province$", re.I),
    re.compile(r"^visit_province", re.I),
]

PARTITION_GEO = re.compile(r"^p_(provincecode|region)$", re.I)


def is_strong_col(name: str) -> bool:
    if not name:
        return False
    for p in STRONG_PATTERNS:
        if p.match(name.strip()):
            return True
    return False


def is_medium_col(name: str) -> bool:
    if not name:
        return False
    if PARTITION_GEO.match(name):
        return True
    if name.lower() == "amfregionid":
        return True
    return False


def collect_geo_columns(cols, include_partition: bool):
    strong, medium, other = [], [], []
    for c in cols:
        n = c.get("name") or ""
        if not n:
            continue
        nl = n.lower()
        if "periodicity" in nl or "csiacquisition" in nl:
            continue
        if is_strong_col(n):
            strong.append(n)
            continue
        if include_partition and is_medium_col(n):
            medium.append(n)
            continue
        if any(k in nl for k in ("region", "province", "city")):
            if nl.startswith("p_") and nl not in ("p_provincecode", "p_region"):
                continue
            other.append(n)
        elif "area" in nl:
            if "cover_area" in nl or "coverage" in nl:
                continue
            other.append(n)
    return sorted(set(strong)), sorted(set(medium)), sorted(set(other))


def main():
    tier_cfg_dim = []
    tier_strong = []
    tier_name = []
    tier_partition_only = []

    seen = set()

    def push(bucket, tn, t, reason):
        if tn in seen:
            return
        seen.add(tn)
        s, m, o = collect_geo_columns(t.get("columns") or [], True)
        bucket.append(
            {
                "table_name": tn,
                "table_comment": (t.get("table_comment") or "")[:300],
                "layer": t.get("layer", ""),
                "layer_desc": t.get("layer_desc", ""),
                "strong_cols": s,
                "partition_geo_cols": m,
                "other_geo_cols": o,
                "reason": reason,
            }
        )

    for key, t in tables.items():
        tn = t.get("table_name", key) or key
        layer = t.get("layer", "")
        cols = t.get("columns") or []
        s, m, o = collect_geo_columns(cols, True)

        if layer in ("CFG", "DIM"):
            push(tier_cfg_dim, tn, t, "CFG/DIM层")
            continue

        if s:
            push(tier_strong, tn, t, "含行政/维度类字段(region_id等)")
            continue

        if table_name_geo_match(tn):
            push(tier_name, tn, t, "表名含region/province/city/area等")
            continue

        # 仅分区省域或弱相关列
        if m and not s and not o:
            push(tier_partition_only, tn, t, "主要为p_provincecode/p_region等分区字段")
        elif o and not s:
            push(tier_partition_only, tn, t, "含区域相关列但无强维度字段名")

    out_dir = Path(__file__).resolve().parent
    report = out_dir / "_region_tables_scan_result.json"
    summary = {
        "tier_cfg_dim_count": len(tier_cfg_dim),
        "tier_strong_col_count": len(tier_strong),
        "tier_table_name_count": len(tier_name),
        "tier_partition_or_weak_count": len(tier_partition_only),
        "total_unique_tables": len(seen),
    }
    with open(report, "w", encoding="utf-8") as wf:
        json.dump(
            {
                "summary": summary,
                "tier_1_cfg_dim": tier_cfg_dim,
                "tier_2_strong_dimension_columns": tier_strong,
                "tier_3_table_name_keyword": tier_name,
                "tier_4_partition_or_weak_columns": tier_partition_only,
            },
            wf,
            ensure_ascii=False,
            indent=2,
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("Wrote", report)


if __name__ == "__main__":
    main()
