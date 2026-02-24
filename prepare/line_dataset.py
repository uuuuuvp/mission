import json
import csv
import os
import pandas as pd
from pathlib import Path
import glob
from extract_acline import attain_parse_args

def create_line_csv_files(json_file, output_dir):
    # 1. 读取JSON文件，获取线路列表
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        lines = data["lines"]  # 假设JSON文件中有一个键 "lines" 包含线路列表
    # 2. 确保输出目录存在
    if not os.path.exists(output_dir):
        print("输出文件夹不存在，正在创建...")
        os.makedirs(output_dir)
    
    # 3. 为每条线路创建一个CSV文件，并写入表头
    for line in lines:
        if line == "安徽.康桥光伏/220kV.康正2N88线":
            line = line.replace("/", "_")
        line_csv_path = os.path.join(output_dir, line) + '.csv'
        with open(line_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'I_P', 'I_Q', 'J_P', 'J_Q'])

def batch_read_from_timestamp_csv_files(timestamp_dir, line_csv_dir):
    for line in os.listdir(line_csv_dir):
        line_name = line.replace('.csv', '')
        if line_name == "安徽.康桥光伏_220kV.康正2N88线":
            line_name = line_name.replace("_", "/")
        
        line_csv_path = os.path.join(line_csv_dir, line)
        read_from_timestamp_csv_files(timestamp_dir, line_csv_path, line_name)


def experiment_for_timestamp(timestamp_dir, line_csv_path):
    timestamp_files = sorted(glob.glob(os.path.join(timestamp_dir, '*.csv')))
    
    for timestamp_file in timestamp_files:
        timestamp = os.path.splitext(os.path.basename(timestamp_file))[0]
        with open(line_csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, '', '', '', ''])  # 这里可以根据需要填充其他

def read_from_timestamp_csv_files(timestamp_dir, line_csv_path, line_name):
    timestamp_files = sorted(glob.glob(os.path.join(timestamp_dir, '*.csv')))
    
    with open(line_csv_path, 'a', newline='', encoding='utf-8') as out_f:
        writer = csv.writer(out_f)
        
        for timestamp_file in timestamp_files:
            timestamp = os.path.splitext(os.path.basename(timestamp_file))[0]
            # 默认值设为空字符串（表示缺失）
            I_P = I_Q = J_P = J_Q = ''
            # 读取时间戳文件，查找指定线路
            with open(timestamp_file, 'r', encoding='GB18030') as in_f:
                reader = csv.reader(in_f)
                next(reader)  # 跳过表头
                next(reader)  # 跳过说明行
                
                for row in reader:
                    if row and len(row) >= 6 and row[1] == line_name:
                        # 将字符串转换为浮点数
                        try:
                            I_P = float(row[2])
                            I_Q = float(row[3])
                            J_P = float(row[4])
                            J_Q = float(row[5])
                        except ValueError:
                            # 如果转换失败，保持原字符串或设为None
                            print(f"警告：文件 {timestamp_file} 中线路 {line_name} 的数据不是有效数值")
                        break
            
            # 写入这一行的数据
            writer.writerow([timestamp, I_P, I_Q, J_P, J_Q])

def main():
    flag = attain_parse_args()
    # 设置路径
    timestamp_directory = "E:\data\ACline_CSV_Cleaned"  # 时间戳CSV文件目录
    json_file = "./unique_lines.json"            # 包含线路名的JSON文件
    output_directory = "E:\data\output_lines"    # 输出目录，初始创建及后续追加
    line_csv_path = "E:\\data\\output_lines\\安徽.霸香2D45线.csv"
    
    if flag == 0:   # 单条线路
        read_from_timestamp_csv_files(timestamp_directory, line_csv_path, "安徽.霸香2D45线")
    elif flag == 1: # 检测时间序列排序问题
        time_stamp = "./time_stamp.csv"          # 时间戳CSV文件路径
        experiment_for_timestamp(timestamp_dir=timestamp_directory, line_csv_path=time_stamp)
    elif flag == 2: # 从json获取文件名创建每条线路的CSV文件
        create_line_csv_files(json_file, output_directory)
    elif flag == 3: # 批量处理每条线路的CSV文件
        test_out = "E:\\data\\test_out"
        # batch_read_from_timestamp_csv_files(timestamp_directory, test_out)
        batch_read_from_timestamp_csv_files(timestamp_directory, output_directory)

if __name__ == "__main__":
    main()