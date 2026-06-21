#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从DDL文件中提取表名和存储路径信息
"""

import re
import sys
from datetime import datetime

def extract_table_info(file_path):
    """从DDL文件中提取表名和存储路径"""
    
    table_info = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式匹配CREATE TABLE语句
        # 匹配模式：CREATE TABLE `database`.`table_name` ... LOCATION 'path'
        pattern = r'CREATE TABLE\s+`([^`]+)`\.`([^`]+)`.*?LOCATION\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            database = match[0]
            table_name = match[1]
            location = match[2]
            
            table_info.append({
                'database': database,
                'table_name': table_name,
                'full_table_name': f"{database}.{table_name}",
                'location': location
            })
    
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
        return []
    
    return table_info

def generate_report(table_info, output_file=None):
    """生成报告"""
    
    if not table_info:
        print("未找到任何表信息")
        return
    
    # 生成输出内容
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("5G DPI DDL建表语句分析报告")
    output_lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("=" * 80)
    output_lines.append(f"总表数量：{len(table_info)}")
    output_lines.append("")
    
    # 表名和路径清单
    output_lines.append("表名和存储路径清单：")
    output_lines.append("-" * 80)
    
    for i, info in enumerate(table_info, 1):
        output_lines.append(f"{i:2d}. 表名：{info['full_table_name']}")
        output_lines.append(f"    路径：{info['location']}")
        output_lines.append("")
    
    # 按数据库分组统计
    db_stats = {}
    for info in table_info:
        db = info['database']
        if db not in db_stats:
            db_stats[db] = []
        db_stats[db].append(info['table_name'])
    
    output_lines.append("按数据库分组统计：")
    output_lines.append("-" * 40)
    for db, tables in db_stats.items():
        output_lines.append(f"数据库：{db} ({len(tables)}个表)")
        for table in tables:
            output_lines.append(f"  - {table}")
        output_lines.append("")
    
    # 路径分析
    output_lines.append("存储路径分析：")
    output_lines.append("-" * 40)
    path_patterns = set()
    for info in table_info:
        # 提取路径的基础目录结构
        path = info['location']
        if path.startswith('hdfs://'):
            path_parts = path.split('/')
            if len(path_parts) >= 6:
                base_path = '/'.join(path_parts[:6])  # hdfs://ns1/zxvmax/telecom/5g/ods
                path_patterns.add(base_path)
    
    for pattern in sorted(path_patterns):
        count = sum(1 for info in table_info if info['location'].startswith(pattern))
        output_lines.append(f"路径模式：{pattern} ({count}个表)")
    
    output_lines.append("")
    output_lines.append("=" * 80)
    
    # 输出到控制台
    report_text = '\n'.join(output_lines)
    print(report_text)
    
    # 保存到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"\n报告已保存到：{output_file}")

def main():
    """主函数"""
    input_file = "ddl.sql"
    output_file = f"table_location_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print("正在分析DDL文件...")
    
    # 提取表信息
    table_info = extract_table_info(input_file)
    
    if not table_info:
        print("未找到任何表信息，请检查DDL文件格式")
        return
    
    # 生成报告
    generate_report(table_info, output_file)
    
    # 生成CSV格式（方便Excel打开）
    csv_file = f"table_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(csv_file, 'w', encoding='utf-8-sig') as f:  # utf-8-sig for Excel compatibility
            f.write("序号,数据库,表名,完整表名,存储路径\n")
            for i, info in enumerate(table_info, 1):
                f.write(f"{i},{info['database']},{info['table_name']},{info['full_table_name']},{info['location']}\n")
        print(f"CSV格式文件已保存到：{csv_file}")
    except Exception as e:
        print(f"保存CSV文件时出错：{str(e)}")

if __name__ == "__main__":
    main()
