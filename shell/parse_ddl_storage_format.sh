#!/usr/bin/env bash
# 从 Hive DDL 中解析表名与 HDFS 侧文件存储格式，输出：表名<TAB>格式名
# 识别格式：TEXT、PARQUET、ORC、AVRO（依据 INPUTFORMAT 类名或 STORED AS 关键字）
# 用法: $0 <输入的DDL文件> <输出的结果文件>

set -euo pipefail

DDL_FILE="${1:-}"
OUTPUT_FILE="${2:-}"

if [[ -z "$DDL_FILE" || -z "$OUTPUT_FILE" ]]; then
    echo "Usage: $0 <ddl_file> <output_file>" >&2
    echo "  ddl_file    输入的 DDL 文件路径" >&2
    echo "  output_file 解析结果输出文件路径（两列：表名、格式名）" >&2
    exit 1
fi

if [[ ! -f "$DDL_FILE" ]]; then
    echo "Error: 输入文件不存在: $DDL_FILE" >&2
    exit 1
fi

# 根据 INPUTFORMAT 的 Java 类名推断存储格式
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

current_table=""

: >"$OUTPUT_FILE"

while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ CREATE[[:space:]]+(EXTERNAL[[:space:]]+)?TABLE[[:space:]]+\`([^\`]+)\` ]]; then
        current_table="${BASH_REMATCH[2]}"
    fi

    [[ -z "$current_table" ]] && continue

    if [[ "$line" =~ INPUTFORMAT[[:space:]]+\'([^\']+)\' ]]; then
        fmt="$(map_inputformat_class "${BASH_REMATCH[1]}")"
        printf '%s\t%s\n' "$current_table" "$fmt" >>"$OUTPUT_FILE"
        current_table=""
        continue
    fi

    if [[ "$line" =~ ^[[:space:]]*STORED[[:space:]]+AS[[:space:]]+(PARQUET|ORC|AVRO|TEXTFILE)[[:space:]]*$ ]]; then
        kw="${BASH_REMATCH[1]}"
        case "$kw" in
            TEXTFILE) fmt="TEXT" ;;
            PARQUET) fmt="PARQUET" ;;
            ORC) fmt="ORC" ;;
            AVRO) fmt="AVRO" ;;
            *) fmt="UNKNOWN" ;;
        esac
        printf '%s\t%s\n' "$current_table" "$fmt" >>"$OUTPUT_FILE"
        current_table=""
    fi
done <"$DDL_FILE"

echo "已写入 $(wc -l <"$OUTPUT_FILE" 2>/dev/null || echo 0) 行到: $OUTPUT_FILE" >&2
