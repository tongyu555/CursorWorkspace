#!/usr/bin/env bash
# 解析 Hive 建表 DDL：输出 表名、存储格式(TEXT/PARQUET/ORC/AVRO)、字段分隔符、压缩类型、存储路径(LOCATION)
# 存储格式依据 INPUTFORMAT 类名或 STORED AS 关键字；TEXT 的字段分隔符取 field.delim，非 TEXT 填 /
# 压缩类型取 TBLPROPERTIES/SERDEPROPERTIES 中常见项，未指定为 /
# LOCATION 未出现时第 5 列为空
# 用法: $0 <输入.sql> <输出文件>

set -euo pipefail

DDL_FILE="${1:-}"
OUTPUT_FILE="${2:-}"

if [[ -z "$DDL_FILE" || -z "$OUTPUT_FILE" ]]; then
    echo "Usage: $0 <ddl_sql_file> <output_file>" >&2
    exit 1
fi

if [[ ! -f "$DDL_FILE" ]]; then
    echo "Error: 输入文件不存在: $DDL_FILE" >&2
    exit 1
fi

map_inputformat_class() {
    local cls="$1"
    case "$cls" in
        *TextInputFormat*|*CombineTextInputFormat*)
            echo "TEXT"
            ;;
        *parquet*|*Parquet*)
            echo "PARQUET"
            ;;
        *OrcInputFormat*|*OrcNewSplit*|*OrcNewInputFormat*)
            echo "ORC"
            ;;
        *AvroContainerInputFormat*|*.avro.*InputFormat*)
            echo "AVRO"
            ;;
        *)
            echo "UNKNOWN"
            ;;
    esac
}

flush_block() {
    local t="$1"
    local fmt="$2"
    local fd="$3"
    local comp="$4"
    local loc="$5"

    [[ -z "$fmt" ]] && fmt="UNKNOWN"

    local delim_out="/"
    if [[ "$fmt" == "TEXT" ]]; then
        if [[ -n "$fd" ]]; then
            delim_out="$fd"
        else
            delim_out="/"
        fi
    fi

    [[ -z "$comp" ]] && comp="/"

    printf '%s\t%s\t%s\t%s\t%s\n' "$t" "$fmt" "$delim_out" "$comp" "$loc"
}

pending_table=""
store_fmt=""
field_delim=""
compression=""
location_path=""

: >"$OUTPUT_FILE"

while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ CREATE[[:space:]]+(EXTERNAL[[:space:]]+)?TABLE[[:space:]]+\`([^\`]+)\` ]]; then
        if [[ -n "$pending_table" ]]; then
            flush_block "$pending_table" "$store_fmt" "$field_delim" "$compression" "$location_path" >>"$OUTPUT_FILE"
        fi
        pending_table="${BASH_REMATCH[2]}"
        store_fmt=""
        field_delim=""
        compression=""
        location_path=""
    fi

    [[ -z "$pending_table" ]] && continue

    if [[ "$line" =~ INPUTFORMAT[[:space:]]+\'([^\']+)\' ]]; then
        new_fmt="$(map_inputformat_class "${BASH_REMATCH[1]}")"
        if [[ "$new_fmt" != "UNKNOWN" ]]; then
            store_fmt="$new_fmt"
        elif [[ -z "$store_fmt" ]]; then
            store_fmt="UNKNOWN"
        fi
    fi

    if [[ "$line" =~ ^[[:space:]]*STORED[[:space:]]+AS[[:space:]]+(PARQUET|ORC|AVRO|TEXTFILE)[[:space:]]*$ ]]; then
        case "${BASH_REMATCH[1]}" in
            TEXTFILE) store_fmt="TEXT" ;;
            PARQUET) store_fmt="PARQUET" ;;
            ORC) store_fmt="ORC" ;;
            AVRO) store_fmt="AVRO" ;;
        esac
    fi

    if [[ "$line" =~ \'field\.delim\'[[:space:]]*=[[:space:]]*\'([^\']*)\' ]]; then
        field_delim="${BASH_REMATCH[1]}"
    fi

    if [[ "$line" =~ \'parquet\.compression\'[[:space:]]*=[[:space:]]*\'([^\']*)\' ]]; then
        compression="${BASH_REMATCH[1]}"
    fi

    if [[ "$line" =~ \'orc\.compress\'[[:space:]]*=[[:space:]]*\'([^\']*)\' ]]; then
        compression="${BASH_REMATCH[1]}"
    fi

    if [[ "$line" =~ \'orc\.compression\'[[:space:]]*=[[:space:]]*\'([^\']*)\' ]]; then
        compression="${BASH_REMATCH[1]}"
    fi

    if [[ "$line" =~ \'avro\.output\.codec\'[[:space:]]*=[[:space:]]*\'([^\']*)\' ]]; then
        compression="${BASH_REMATCH[1]}"
    fi

    if [[ "$line" =~ \'avro\.codec\'[[:space:]]*=[[:space:]]*\'([^\']*)\' ]]; then
        compression="${BASH_REMATCH[1]}"
    fi

    if [[ "$line" =~ ^[[:space:]]*LOCATION[[:space:]]+\'([^\']+)\' ]]; then
        location_path="${BASH_REMATCH[1]}"
    fi
done <"$DDL_FILE"

if [[ -n "$pending_table" ]]; then
    flush_block "$pending_table" "$store_fmt" "$field_delim" "$compression" "$location_path" >>"$OUTPUT_FILE"
fi

echo "已写入 $(wc -l <"$OUTPUT_FILE" 2>/dev/null || echo 0) 行到: $OUTPUT_FILE" >&2
