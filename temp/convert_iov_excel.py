#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
根据Excel导航页将各个Sheet转换为TXT文件
按照导航页的表名进行命名
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime

def convert_excel_by_navigation(excel_file_path, output_dir="input1", encoding='utf-8'):
    """
    根据Excel导航页将各个Sheet转换为TXT文件
    
    Args:
        excel_file_path (str): Excel文件路径
        output_dir (str): 输出目录路径，默认为input1
        encoding (str): 输出文件编码格式，默认utf-8
    """
    try:
        # 检查Excel文件是否存在
        if not os.path.exists(excel_file_path):
            print(f"错误：文件 {excel_file_path} 不存在")
            return False
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        print(f"输出目录: {output_dir}")
        
        print(f"正在读取Excel文件: {excel_file_path}")
        
        # 读取Excel文件的所有工作表
        excel_file = pd.ExcelFile(excel_file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"发现 {len(sheet_names)} 个工作表: {sheet_names}")
        
        # 读取导航页（假设是第一个sheet或名为"导航"的sheet）
        navigation_sheet = None
        if "导航" in sheet_names:
            navigation_sheet = "导航"
        else:
            navigation_sheet = sheet_names[0]
        
        print(f"\n正在读取导航页: {navigation_sheet}")
        
        # 读取导航页，查找表名和sheet页的映射关系
        nav_df = pd.read_excel(excel_file_path, sheet_name=navigation_sheet)
        
        # 打印导航页前几行，帮助理解结构
        print(f"\n导航页前10行内容:")
        print(nav_df.head(10).to_string())
        
        # 尝试找到包含表名的列
        # 通常导航页会有"表名"、"sheet页"、"工作表"等列
        table_name_mapping = {}
        
        # 查找可能的列名
        possible_table_col = ['表名', '表英文名', '目标表', 'table_name', 'TABLE_NAME']
        possible_sheet_col = ['sheet页', 'Sheet页', '工作表', 'sheet', 'Sheet']
        
        table_col = None
        sheet_col = None
        
        # 查找表名列
        for col in nav_df.columns:
            col_str = str(col).strip()
            if any(keyword in col_str for keyword in possible_table_col):
                table_col = col
                print(f"\n找到表名列: {col}")
                break
        
        # 查找sheet页列
        for col in nav_df.columns:
            col_str = str(col).strip()
            if any(keyword in col_str for keyword in possible_sheet_col):
                sheet_col = col
                print(f"找到Sheet页列: {col}")
                break
        
        # 如果找到了映射列，则建立映射关系
        if table_col is not None and sheet_col is not None:
            for idx, row in nav_df.iterrows():
                table_name = str(row[table_col]).strip()
                sheet_name = str(row[sheet_col]).strip()
                
                # 跳过空值和NaN
                if table_name and table_name != 'nan' and sheet_name and sheet_name != 'nan':
                    # sheet_name可能是数字，需要转换
                    if sheet_name.isdigit():
                        sheet_idx = int(sheet_name) - 1  # Excel中的序号从1开始
                        if 0 <= sheet_idx < len(sheet_names):
                            actual_sheet = sheet_names[sheet_idx]
                            table_name_mapping[actual_sheet] = table_name
                            print(f"  映射: Sheet {sheet_name} ({actual_sheet}) -> {table_name}")
                    else:
                        table_name_mapping[sheet_name] = table_name
                        print(f"  映射: {sheet_name} -> {table_name}")
        
        # 如果没有找到明确的映射，尝试直接从列B和列C读取
        if not table_name_mapping:
            print("\n未找到明确的映射列，尝试从前两列读取映射关系...")
            for idx, row in nav_df.iterrows():
                if idx < 5:  # 跳过前几行标题行
                    continue
                # 尝试读取第一列（sheet序号）和第二列（表名）
                if len(nav_df.columns) >= 2:
                    sheet_ref = str(row.iloc[0]).strip()
                    table_name = str(row.iloc[1]).strip()
                    
                    if sheet_ref.isdigit() and table_name and table_name != 'nan':
                        sheet_idx = int(sheet_ref) - 1
                        if 0 <= sheet_idx < len(sheet_names):
                            actual_sheet = sheet_names[sheet_idx]
                            table_name_mapping[actual_sheet] = table_name
                            print(f"  映射: Sheet {sheet_ref} ({actual_sheet}) -> {table_name}")
        
        if not table_name_mapping:
            print("\n警告：无法从导航页提取映射关系，将使用Sheet名称作为文件名")
            # 使用原始sheet名称，除了导航页
            for sheet in sheet_names:
                if sheet != navigation_sheet:
                    table_name_mapping[sheet] = sheet
        
        print(f"\n总共找到 {len(table_name_mapping)} 个映射关系")
        
        # 记录成功转换的文件列表
        converted_files = []
        
        # 处理每个sheet页
        for sheet_name, table_name in table_name_mapping.items():
            if sheet_name not in sheet_names:
                print(f"\n警告：Sheet '{sheet_name}' 不存在，跳过")
                continue
            
            print(f"\n正在处理: {sheet_name} -> {table_name}.txt")
            
            try:
                # 首先读取整个工作表来查找起始行
                temp_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
                
                # 查找包含"详细字段信息"的行
                start_row = None
                target_keywords = ["详细字段信息", "字段信息", "PDM字段"]
                
                # 遍历所有行和列，查找目标关键字
                for row_idx in range(len(temp_df)):
                    for col_idx in range(len(temp_df.columns)):
                        cell_value = str(temp_df.iloc[row_idx, col_idx]).strip()
                        if any(keyword in cell_value for keyword in target_keywords):
                            start_row = row_idx
                            print(f"  找到起始行: 第{start_row + 2}行 (Excel行号)")
                            break
                    if start_row is not None:
                        break
                
                if start_row is None:
                    print(f"  警告：未找到包含关键字的行，将从第1行开始读取")
                    start_row = 0
                
                # 从找到的起始行开始，只读取B、C、D列
                df = pd.read_excel(excel_file_path, sheet_name=sheet_name, 
                                 usecols="B:D", skiprows=start_row)
                
                # 生成输出文件名：使用导航页中的表名
                # 清理文件名中的特殊字符
                safe_table_name = "".join(c for c in table_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                output_filename = f"{safe_table_name}.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                # 创建单独的TXT文件
                with open(output_path, 'w', encoding=encoding) as txt_file:
                    # 写入文件头信息
                    txt_file.write(f"Excel工作表转换结果 (B、C、D列原始数据)\n")
                    txt_file.write(f"原文件: {excel_file_path}\n")
                    txt_file.write(f"工作表: {sheet_name}\n")
                    txt_file.write(f"表名: {table_name}\n")
                    txt_file.write(f"起始行: 第{start_row + 2}行 (Excel行号)\n")
                    txt_file.write(f"搜索关键字: {', '.join(target_keywords)}\n")
                    txt_file.write(f"转换时间: {datetime.now()}\n")
                    txt_file.write("=" * 80 + "\n\n")
                    
                    # 如果数据为空
                    if df.empty:
                        txt_file.write("（此工作表无数据）\n")
                        print(f"  工作表 {sheet_name} 无数据，已生成空文件")
                    else:
                        # 写入数据维度信息
                        txt_file.write(f"数据维度: {df.shape[0]} 行 x {df.shape[1]} 列\n\n")
                        
                        # 写入列名
                        txt_file.write("列名信息:\n")
                        for idx, col in enumerate(df.columns):
                            txt_file.write(f"  {idx+1}. {col}\n")
                        txt_file.write("\n")
                        
                        # 写入处理说明
                        txt_file.write("数据处理说明:\n")
                        txt_file.write("- 智能定位起始行: 自动查找包含'详细字段信息'的行\n")
                        txt_file.write("- 只提取B、C、D三列数据\n")
                        txt_file.write("- 从起始行读取到工作表末尾\n")
                        txt_file.write("- 保持原始数据格式，不进行分割处理\n\n")
                        
                        # 转换数据为字符串格式，处理NaN值
                        df_str = df.fillna('').astype(str)
                        
                        # 写入原始数据
                        txt_file.write("数据内容:\n")
                        
                        # 写入表头
                        header = "\t".join(df_str.columns)
                        txt_file.write(header + "\n")
                        
                        # 写入数据行
                        for _, row in df_str.iterrows():
                            row_data = "\t".join(row.values)
                            txt_file.write(row_data + "\n")
                        
                        print(f"  成功转换 {df.shape[0]} 行数据")
                
                converted_files.append(output_path)
                print(f"  输出文件: {output_path}")
                
            except Exception as e:
                print(f"警告：处理工作表 {sheet_name} 时出错: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n转换完成！共生成 {len(converted_files)} 个文件:")
        for file_path in converted_files:
            print(f"  - {file_path}")
        
        return True
        
    except Exception as e:
        print(f"转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Excel文件路径（使用相对路径）
    import sys
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Excel文件在车联网建模子目录下
    excel_file = os.path.join(script_dir, "车联网建模", "车联网关联方式变更需求模型设计-20250923.xlsx")
    output_dir = os.path.join(script_dir, "车联网建模", "input1")
    
    print(f"Excel文件路径: {excel_file}")
    print(f"输出目录: {output_dir}")
    
    # 执行转换
    success = convert_excel_by_navigation(excel_file, output_dir=output_dir)
    
    if success:
        print("\n转换成功完成！")
    else:
        print("\n转换失败！")



