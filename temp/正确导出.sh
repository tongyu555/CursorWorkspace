#!/bin/bash
# 正确版本：自动添加命名空间前缀

NAMESPACE="${1:-nifi_cache}"
OUTPUT="hbase_tables_$(date +%Y%m%d_%H%M%S).sql"

echo "正在导出命名空间: ${NAMESPACE}"

# 使用HBase Shell的Ruby脚本（在Ruby里直接拼接完整表名）
cat > /tmp/export_$$.rb <<EOF
namespace = '${NAMESPACE}'
tables = list_namespace_tables(namespace)

puts "# 找到 #{tables.length} 个表"

tables.each do |table_name|
  # 拼接完整表名
  full_table = "#{namespace}:#{table_name}"
  
  begin
    desc = describe(full_table)
    
    cfs = []
    desc.each do |key, cf|
      if cf.is_a?(Hash) && cf['NAME']
        cf_str = "{NAME => '#{cf['NAME']}'"
        cf_str += ", BLOOMFILTER => '#{cf['BLOOMFILTER']}'" if cf['BLOOMFILTER']
        cf_str += ", VERSIONS => '#{cf['VERSIONS']}'" if cf['VERSIONS']
        cf_str += ", IN_MEMORY => '#{cf['IN_MEMORY']}'" if cf['IN_MEMORY']
        cf_str += ", KEEP_DELETED_CELLS => '#{cf['KEEP_DELETED_CELLS']}'" if cf['KEEP_DELETED_CELLS']
        cf_str += ", DATA_BLOCK_ENCODING => '#{cf['DATA_BLOCK_ENCODING']}'" if cf['DATA_BLOCK_ENCODING']
        cf_str += ", TTL => '#{cf['TTL']}'" if cf['TTL']
        cf_str += ", COMPRESSION => '#{cf['COMPRESSION']}'" if cf['COMPRESSION']
        cf_str += ", MIN_VERSIONS => '#{cf['MIN_VERSIONS']}'" if cf['MIN_VERSIONS']
        cf_str += ", BLOCKCACHE => '#{cf['BLOCKCACHE']}'" if cf['BLOCKCACHE']
        cf_str += ", BLOCKSIZE => '#{cf['BLOCKSIZE']}'" if cf['BLOCKSIZE']
        cf_str += ", REPLICATION_SCOPE => '#{cf['REPLICATION_SCOPE']}'" if cf['REPLICATION_SCOPE']
        cf_str += "}"
        cfs << cf_str
      end
    end
    
    puts "create '#{full_table}',#{cfs.join(',')}" unless cfs.empty?
  rescue => e
    puts "# 错误: 表 #{full_table} - #{e.message}"
  end
end

exit
EOF

# 执行Ruby脚本 - 先保存所有输出
echo "执行HBase Shell..."
hbase shell /tmp/export_$$.rb > /tmp/hbase_output_$$.txt 2>&1

# 显示原始输出（用于调试）
echo "======== 原始输出 ========"
cat /tmp/hbase_output_$$.txt
echo "======== 输出结束 ========"
echo ""

# 提取create语句
grep "^create" /tmp/hbase_output_$$.txt > ${OUTPUT} 2>/dev/null

# 清理
rm -f /tmp/export_$$.rb /tmp/hbase_output_$$.txt

# 检查结果
if [ -s ${OUTPUT} ]; then
    TABLE_COUNT=$(wc -l < ${OUTPUT})
    echo ""
    echo "=========================================="
    echo "✓ 导出成功！"
    echo "=========================================="
    echo "文件: ${OUTPUT}"
    echo "表数量: ${TABLE_COUNT}"
    echo ""
    echo "前5行预览:"
    head -5 ${OUTPUT}
    echo ""
    echo "使用方法："
    echo "  hbase shell < ${OUTPUT}"
    echo "=========================================="
else
    echo ""
    echo "✗ 导出失败，请检查HBase连接"
fi

