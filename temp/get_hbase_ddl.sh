#!/bin/bash

# 脚本功能: 获取HBase中nifi_cache命名空间下所有表的建表语句
# 作者: Auto Generated
# 日期: $(date +%Y-%m-%d)

# 设置变量
NAMESPACE="nifi_cache"
OUTPUT_FILE="hbase_ddl_$(date +%Y%m%d_%H%M%S).rb"
TEMP_FILE="/tmp/hbase_tables_$$.txt"
TEMP_DESC="/tmp/hbase_desc_$$.txt"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}获取HBase建表语句脚本${NC}"
echo -e "${GREEN}命名空间: ${NAMESPACE}${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查HBase是否可用
echo -e "${YELLOW}检查HBase连接...${NC}"
if ! command -v hbase &> /dev/null; then
    echo -e "${RED}错误: 未找到hbase命令,请检查HBase是否已安装并配置环境变量${NC}"
    exit 1
fi

# 获取命名空间下的所有表
echo -e "${YELLOW}正在获取${NAMESPACE}命名空间下的所有表...${NC}"
echo "list_namespace_tables '${NAMESPACE}'" | hbase shell -n 2>/dev/null | grep -v "HBase Shell" | grep -v "Use" | grep -v "Version" | grep -v "row(s)" | grep -v "^$" | grep -v "TABLE" | sed 's/ //g' > ${TEMP_FILE}

# 检查是否获取到表
TABLE_COUNT=$(cat ${TEMP_FILE} | wc -l)
if [ ${TABLE_COUNT} -eq 0 ]; then
    echo -e "${RED}错误: 未找到任何表或命名空间不存在${NC}"
    rm -f ${TEMP_FILE}
    exit 1
fi

echo -e "${GREEN}找到 ${TABLE_COUNT} 个表${NC}"

# 清空或创建输出文件
> ${OUTPUT_FILE}

# 遍历每个表,获取建表语句
TABLE_INDEX=0
while IFS= read -r table
do
    TABLE_INDEX=$((TABLE_INDEX + 1))
    echo -e "${YELLOW}[${TABLE_INDEX}/${TABLE_COUNT}] 正在处理表: ${table}${NC}"
    
    # 获取表的描述信息
    echo "describe '${NAMESPACE}:${table}'" | hbase shell -n 2>/dev/null > ${TEMP_DESC}
    
    # 解析建表语句
    # 提取列族信息
    COLUMN_FAMILIES=$(grep "NAME =>" ${TEMP_DESC} | grep -v "Table ${NAMESPACE}:${table}")
    
    if [ -z "${COLUMN_FAMILIES}" ]; then
        echo -e "${RED}警告: 无法获取表 ${table} 的列族信息${NC}"
        continue
    fi
    
    # 构建create语句
    CREATE_STMT="create '${NAMESPACE}:${table}'"
    
    # 处理列族配置
    while IFS= read -r cf_line
    do
        # 提取列族配置,去除多余空格
        cf_config=$(echo "${cf_line}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        if [ ! -z "${cf_config}" ]; then
            CREATE_STMT="${CREATE_STMT},{${cf_config}}"
        fi
    done <<< "${COLUMN_FAMILIES}"
    
    # 写入输出文件
    echo "${CREATE_STMT}" >> ${OUTPUT_FILE}
    
done < ${TEMP_FILE}

# 清理临时文件
rm -f ${TEMP_FILE} ${TEMP_DESC}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}完成! 建表语句已保存到: ${OUTPUT_FILE}${NC}"
echo -e "${GREEN}总共处理了 ${TABLE_COUNT} 个表${NC}"
echo -e "${GREEN}========================================${NC}"

# 显示文件内容预览
echo -e "${YELLOW}文件内容预览(前5行):${NC}"
head -5 ${OUTPUT_FILE}

exit 0


