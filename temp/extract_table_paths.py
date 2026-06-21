#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从DDL文件中提取表名和HDFS路径信息
"""

import re
import os

def extract_table_paths(ddl_file, output_file):
    """
    从DDL文件中提取表名和路径信息
    """
    table_paths = []
    
    with open(ddl_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 使用正则表达式匹配CREATE TABLE语句和LOCATION语句
    # 匹配CREATE EXTERNAL TABLE `hsdlake`.`表名`(
    table_pattern = r"CREATE EXTERNAL TABLE `hsdlake`\.`([^`]+)`\("
    # 匹配LOCATION 'hdfs://路径'
    location_pattern = r"LOCATION 'hdfs://([^']+)'"
    
    # 找到所有表名
    table_matches = re.findall(table_pattern, content)
    # 找到所有路径
    location_matches = re.findall(location_pattern, content)
    
    # 确保表名和路径数量匹配
    if len(table_matches) != len(location_matches):
        print(f"警告：表名数量({len(table_matches)})与路径数量({len(location_matches)})不匹配")
    
    # 组合表名和路径
    for i, table_name in enumerate(table_matches):
        if i < len(location_matches):
            full_path = f"hdfs://{location_matches[i]}"
            table_paths.append((table_name, full_path))
        else:
            print(f"警告：表 {table_name} 没有对应的路径")
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("表名\tHDFS路径\n")
        f.write("=" * 80 + "\n")
        
        for table_name, path in table_paths:
            f.write(f"{table_name}\t{path}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"总计：{len(table_paths)} 个表\n")
    
    print(f"成功提取 {len(table_paths)} 个表的信息")
    print(f"结果已保存到：{output_file}")
    
    return table_paths

if __name__ == "__main__":
    ddl_file = "ddl.sql"
    output_file = "table_paths.txt"
    
    if not os.path.exists(ddl_file):
        print(f"错误：找不到文件 {ddl_file}")
        exit(1)
    
    table_paths = extract_table_paths(ddl_file, output_file)
    
    # 打印前几个结果作为预览
    print("\n预览（前5个表）：")
    print("-" * 80)
    for i, (table_name, path) in enumerate(table_paths[:5]):
        print(f"{i+1}. {table_name}")
        print(f"   路径: {path}")
        print()
