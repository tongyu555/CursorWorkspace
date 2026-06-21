#!/usr/bin/env bash
# 从 DDL 文件中提取 表名 与 LOCATION 路径，输出格式：表名       路径
# 用法: $0 <输入的DDL文件> <输出的结果文件>

DDL_FILE="$1"
OUTPUT_FILE="$2"

if [[ -z "$DDL_FILE" || -z "$OUTPUT_FILE" ]]; then
    echo "Usage: $0 <ddl_file> <output_file>" >&2
    echo "  ddl_file    输入的 DDL 文件路径" >&2
    echo "  output_file 提取结果输出文件路径" >&2
    exit 1
fi

if [[ ! -f "$DDL_FILE" ]]; then
    echo "Error: 输入文件不存在: $DDL_FILE" >&2
    exit 1
fi

tables=()
paths=()

while IFS= read -r line; do
    if [[ "$line" =~ CREATE\ EXTERNAL\ TABLE\ \`([^\`]+)\` ]]; then
        tables+=("${BASH_REMATCH[1]}")
    fi
    if [[ "$line" =~ LOCATION\ \'([^\']+)\' ]]; then
        paths+=("${BASH_REMATCH[1]}")
    fi
done < "$DDL_FILE"

for i in "${!tables[@]}"; do
    printf '%s\t%s\n' "${tables[$i]}" "${paths[$i]:-}"
done > "$OUTPUT_FILE"

echo "已写入 $(wc -l < "$OUTPUT_FILE" 2>/dev/null || echo 0) 行到: $OUTPUT_FILE" >&2
