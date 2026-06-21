#!/bin/bash

# 脚本功能: 获取HBase中指定命名空间下所有表的建表语句(优化版本)
# 使用方法: ./get_hbase_ddl_v2.sh [namespace] [output_file]
# 示例: ./get_hbase_ddl_v2.sh nifi_cache hbase_ddl.rb

# 默认参数
NAMESPACE=${1:-"nifi_cache"}
OUTPUT_FILE=${2:-"hbase_ddl_$(date +%Y%m%d_%H%M%S).rb"}

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}HBase建表语句导出工具${NC}"
echo -e "${GREEN}命名空间: ${NAMESPACE}${NC}"
echo -e "${GREEN}输出文件: ${OUTPUT_FILE}${NC}"
echo -e "${GREEN}========================================${NC}"

# 创建HBase Shell脚本
cat > /tmp/get_tables_$$.rb << 'EOF'
list_namespace_tables ARGV[0]
EOF

cat > /tmp/describe_table_$$.rb << 'EOF'
desc ARGV[0]
EOF

# 获取表列表
echo -e "${YELLOW}正在获取表列表...${NC}"
TABLES=$(echo "list_namespace_tables '${NAMESPACE}'" | hbase shell -n 2>/dev/null | \
    grep -E "^${NAMESPACE}:" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

if [ -z "${TABLES}" ]; then
    echo -e "${RED}错误: 未找到任何表${NC}"
    exit 1
fi

TABLE_COUNT=$(echo "${TABLES}" | wc -l)
echo -e "${GREEN}找到 ${TABLE_COUNT} 个表${NC}"

# 清空输出文件
> ${OUTPUT_FILE}

# 遍历每个表
INDEX=0
for TABLE_FULL_NAME in ${TABLES}
do
    INDEX=$((INDEX + 1))
    echo -e "${YELLOW}[${INDEX}/${TABLE_COUNT}] 处理: ${TABLE_FULL_NAME}${NC}"
    
    # 使用Python脚本解析HBase describe输出
    DESCRIBE_OUTPUT=$(echo "describe '${TABLE_FULL_NAME}'" | hbase shell -n 2>/dev/null)
    
    # 提取列族配置
    CREATE_STMT=$(echo "${DESCRIBE_OUTPUT}" | python3 -c "
import sys
import re

content = sys.stdin.read()

# 查找所有列族配置
pattern = r\"NAME => '([^']+)'.*?BLOOMFILTER => '([^']+)'.*?VERSIONS => '([^']+)'.*?IN_MEMORY => '([^']+)'.*?KEEP_DELETED_CELLS => '([^']+)'.*?DATA_BLOCK_ENCODING => '([^']+)'.*?TTL => '([^']+)'.*?COMPRESSION => '([^']+)'.*?MIN_VERSIONS => '([^']+)'.*?BLOCKCACHE => '([^']+)'.*?BLOCKSIZE => '([^']+)'.*?REPLICATION_SCOPE => '([^']+)'\"

matches = re.findall(pattern, content, re.DOTALL)

if matches:
    cf_configs = []
    for match in matches:
        cf_name, bloomfilter, versions, in_memory, keep_deleted, data_encoding, ttl, compression, min_versions, blockcache, blocksize, replication = match
        config = (f\"{{NAME => '{cf_name}', BLOOMFILTER => '{bloomfilter}', \"
                 f\"VERSIONS => '{versions}', IN_MEMORY => '{in_memory}', \"
                 f\"KEEP_DELETED_CELLS => '{keep_deleted}', DATA_BLOCK_ENCODING => '{data_encoding}', \"
                 f\"TTL => '{ttl}', COMPRESSION => '{compression}', \"
                 f\"MIN_VERSIONS => '{min_versions}', BLOCKCACHE => '{blockcache}', \"
                 f\"BLOCKSIZE => '{blocksize}', REPLICATION_SCOPE => '{replication}'}}\")
        cf_configs.append(config)
    
    print(f\"create '${TABLE_FULL_NAME}',\" + ','.join(cf_configs))
" 2>/dev/null)
    
    if [ ! -z "${CREATE_STMT}" ]; then
        echo "${CREATE_STMT}" >> ${OUTPUT_FILE}
    else
        echo -e "${RED}警告: 无法解析表 ${TABLE_FULL_NAME}${NC}"
    fi
done

# 清理临时文件
rm -f /tmp/get_tables_$$.rb /tmp/describe_table_$$.rb

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}完成! 共处理 ${TABLE_COUNT} 个表${NC}"
echo -e "${GREEN}输出文件: ${OUTPUT_FILE}${NC}"
echo -e "${GREEN}========================================${NC}"

# 显示统计信息
if [ -f ${OUTPUT_FILE} ]; then
    GENERATED_COUNT=$(cat ${OUTPUT_FILE} | grep -c "^create")
    echo -e "${GREEN}成功生成 ${GENERATED_COUNT} 条建表语句${NC}"
    echo -e "${YELLOW}前3条预览:${NC}"
    head -3 ${OUTPUT_FILE}
fi


