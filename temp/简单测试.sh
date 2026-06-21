#!/bin/bash
# 最简单的测试 - 只处理一个表

NAMESPACE="nifi_cache"

echo "测试获取第一个表的建表语句..."

hbase shell <<'EOF'
# 获取第一个表
tables = list_namespace_tables('nifi_cache')
if tables.empty?
  puts "错误: 命名空间下没有表"
  exit
end

first_table = tables[0]
full_name = "nifi_cache:#{first_table}"

puts "处理表: #{full_name}"

begin
  desc = describe(full_name)
  
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
  
  puts ""
  puts "========== 建表语句 =========="
  puts "create '#{full_name}',#{cfs.join(',')}"
  puts "=============================="
  
rescue => e
  puts "错误: #{e.message}"
  puts e.backtrace
end

exit
EOF













