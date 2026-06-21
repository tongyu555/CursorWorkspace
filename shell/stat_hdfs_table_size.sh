#!/usr/bin/env bash
# 根据「表名\t路径」列表，统计每个路径的 HDFS 总大小(GB) 与总文件数(个)，输出到指定文件
# 输出格式：表名   路径名   总文件数   总文件大小(GB)
# 用法: $0 <输入文件(表名+路径)> <输出文件>

INPUT_FILE="$1"
OUTPUT_FILE="$2"

if [[ -z "$INPUT_FILE" || -z "$OUTPUT_FILE" ]]; then
    echo "Usage: $0 <input_file> <output_file>" >&2
    echo "  input_file  表名与路径列表，每行格式：表名<Tab>路径" >&2
    echo "  output_file 统计结果输出文件，格式：表名  路径名  总文件数  总文件大小(GB)" >&2
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: 输入文件不存在: $INPUT_FILE" >&2
    exit 1
fi

: > "$OUTPUT_FILE"

while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    table=$(echo "$line" | awk '{print $1}')
    path=$(echo "$line" | awk '{$1=""; sub(/^[[:space:]]+/, ""); print $0}')
    [[ -z "$table" || -z "$path" ]] && continue

    count_out=$(hdfs dfs -count "$path" 2>/dev/null)
    if [[ $? -ne 0 ]]; then
        printf '%s\t%s\t%s\t%s\n' "$table" "$path" "ERROR" "ERROR" >> "$OUTPUT_FILE"
        continue
    fi

    file_count=$(echo "$count_out" | awk '{print $2}')
    size_bytes=$(echo "$count_out" | awk '{print $3}')
    size_gb=$(echo "$size_bytes 1024 1024 1024" | awk '{printf "%.4f", $1/$2/$3/$4}')
    printf '%s\t%s\t%s\t%s\n' "$table" "$path" "$file_count" "$size_gb" >> "$OUTPUT_FILE"
done < "$INPUT_FILE"

echo "已写入 $(wc -l < "$OUTPUT_FILE" 2>/dev/null || echo 0) 行到: $OUTPUT_FILE" >&2
