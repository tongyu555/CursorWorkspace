#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Excel转TXT文本格式转换器
支持多工作表Excel文件转换为可读的文本格式
"""

import pandas as pd
import sys
import os
from pathlib import Path

def excel_to_txt(excel_file_path, output_dir=None, encoding='utf-8'):
    """
    将Excel文件的每个工作表转换为单独的TXT文本文件
    智能定位起始行，从包含'详细字段信息'的行开始读取B、C、D三列原始数据
    
    Args:
        excel_file_path (str): Excel文件路径
        output_dir (str): 输出目录路径，如果为None则使用当前目录
        encoding (str): 输出文件编码格式，默认utf-8
    """
    try:
        # 检查Excel文件是否存在
        if not os.path.exists(excel_file_path):
            print(f"错误：文件 {excel_file_path} 不存在")
            return False
        
        # 获取Excel文件的基础名称（不含扩展名）
        base_name = Path(excel_file_path).stem
        
        # 如果没有指定输出目录，使用当前目录
        if output_dir is None:
            output_dir = "."
        else:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
        
        print(f"正在读取Excel文件: {excel_file_path}")
        
        # 读取Excel文件的所有工作表
        excel_file = pd.ExcelFile(excel_file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"发现 {len(sheet_names)} 个工作表: {sheet_names}")
        
        # 记录成功转换的文件列表
        converted_files = []
        
        # 逐个处理每个工作表
        for i, sheet_name in enumerate(sheet_names):
            print(f"正在处理工作表 {i+1}/{len(sheet_names)}: {sheet_name}")
            
            try:
                # 首先读取整个工作表来查找起始行
                temp_df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
                
                # 查找包含"详细字段信息"的行
                start_row = None
                target_keywords = ["详细字段信息"]
                
                print(f"  正在查找起始行，搜索关键字: {target_keywords}")
                
                # 遍历所有行和列，查找目标关键字
                for row_idx in range(len(temp_df)):
                    for col_idx in range(len(temp_df.columns)):
                        cell_value = str(temp_df.iloc[row_idx, col_idx]).strip()
                        if any(keyword in cell_value for keyword in target_keywords):
                            start_row = row_idx
                            print(f"  找到起始行: 第{start_row + 2}行 (Excel行号), 匹配内容: '{cell_value}'")
                            break
                    if start_row is not None:
                        break
                
                if start_row is None:
                    print(f"  警告：未找到包含关键字的行，将从第1行开始读取")
                    start_row = 0
                
                # 从找到的起始行开始，只读取B、C、D列
                df = pd.read_excel(excel_file_path, sheet_name=sheet_name, 
                                 usecols="B:D", skiprows=start_row)
                
                print(f"  从第{start_row + 2}行开始读取B、C、D列数据")
                
                # 生成输出文件名：Excel文件名_Sheet页名.txt
                # 清理文件名中的特殊字符
                safe_sheet_name = "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_filename = f"{base_name}_{safe_sheet_name}.txt"
                output_path = os.path.join(output_dir, output_filename)
                
                # 创建单独的TXT文件
                with open(output_path, 'w', encoding=encoding) as txt_file:
                    # 写入文件头信息
                    txt_file.write(f"Excel工作表转换结果 (B、C、D列原始数据)\n")
                    txt_file.write(f"原文件: {excel_file_path}\n")
                    txt_file.write(f"工作表: {sheet_name}\n")
                    txt_file.write(f"起始行: 第{start_row + 2}行 (Excel行号)\n")
                    txt_file.write(f"搜索关键字: {', '.join(target_keywords)}\n")
                    txt_file.write(f"转换时间: {pd.Timestamp.now()}\n")
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
                continue
        
        print(f"\n转换完成！共生成 {len(converted_files)} 个文件:")
        for file_path in converted_files:
            print(f"  - {file_path}")
        
        return True
        
    except Exception as e:
        print(f"转换失败: {str(e)}")
        return False

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python excel_to_txt.py <Excel文件路径> [输出目录路径]")
        print("\n示例:")
        print("  python excel_to_txt.py data.xlsx")
        print("  python excel_to_txt.py data.xlsx ./output/")
        print("\n功能说明:")
        print("  - 智能定位：自动查找包含'详细字段信息'的行作为起始行")
        print("  - 只提取B、C、D三列数据，从起始行读取到末尾")
        print("  - 每个Sheet页会生成一个单独的TXT文件")
        print("  - 文件命名格式：Excel文件名_Sheet页名.txt")
        print("  - 保持原始数据格式，不进行任何分割处理")
        return
    
    excel_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 执行转换
    success = excel_to_txt(excel_file, output_dir)
    
    if success:
        print("\n转换成功完成！")
    else:
        print("\n转换失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
