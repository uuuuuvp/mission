import pandas as pd
from pathlib import Path
import json,os
from extract_acline import attain_parse_args

def data_loss_mat(csv_dir, index_json, output_csv):
    """构建线路在时间戳文件缺失矩阵
    csv_dir: 时间戳文件目录
    json_file: JSON文件包含所有线路名
    """
    # 1. 从JSON加载所有线路名
    with open(index_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_lines = data.get('lines', [])  # 所有线路名的列表

    # 2. 获取所有CSV文件
    csv_files = list(Path(csv_dir).glob("*.csv"))
    def time_key(f):
        # "国调_20230801_0000.csv" -> "20230801_0000"
        return f.stem.split('_', 1)[1]  # 按第一个_分割，取后面部分
    
    csv_files.sort(key=time_key)
    
    # 3. 初始化缺失矩阵（DataFrame）
    # 行索引：线路名，列名：时间戳
    timestamps = [time_key(f) for f in csv_files]
    loss_df = pd.DataFrame(0, index=all_lines, columns=timestamps)
    
    # 4. 遍历每个时间戳文件，利用index快速标记存在的线路
    for i, csv_file in enumerate(csv_files, 1):
        timestamp = time_key(csv_file)
        print(f"处理时间点 [{i}/{len(csv_files)}]: {timestamp}", end='\r')
        
        try:
            # 读取当前时间点的数据
            df = pd.read_csv(
                csv_file, 
                encoding='GB18030', 
                skiprows=[1],  # 跳过前两行（id和序号行）
                usecols=['name'],  # 只读取name列，提高效率
                dtype={'name': str}  # 确保name列为字符串类型
            )
            # 假设df的index已经是处理后的线路名
            # 获取df中存在的线路名（即index的值）
            existing_lines = df['name'].tolist()
            
            # 找出同时存在于loss_df index中的线路并标记为1
            common_lines = [line for line in existing_lines if line in loss_df.index]
            if common_lines:
                loss_df.loc[common_lines, timestamp] = 1
                
        except Exception as e:
            print(f"\n警告: 读取文件 {csv_file.name} 时出错: {e}")
            continue
    
    print("\n缺失矩阵构建完成")
    
    # 5. 添加统计信息
    print("正在添加统计信息...")
    loss_df['total_records'] = loss_df.sum(axis=1)
    loss_df['missing_count'] = len(timestamps) - loss_df['total_records']
    loss_df['missing_rate'] = (loss_df['missing_count'] / len(timestamps) * 100).round(2)
    
    # 6. 保存到CSV文件
    loss_df.to_csv(output_csv, encoding='utf-8-sig')
    print(f"缺失矩阵已保存到: {output_csv}")
    



# 使用示例
if __name__ == "__main__":
    # 添加到flag判断中
    # flag = attain_parse_args()
    # if flag == "0":
        csv_dir = "E:\\data\\ACline_CSV_Cleaned"  # 替换为实际路径
        index_json = "./unique_lines-1.json"  # 替换为实际路径
        output_csv = "./data_loss_matrix.csv"  # 输出文件名
        data_loss_mat(csv_dir, index_json, output_csv)
