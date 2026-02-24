import pandas as pd
from pathlib import Path
import json,os
from extract_acline import attain_parse_args

def count_unique_lines(csv_dir):
    """统计所有不重复的线路名"""
    csv_files = list(Path(csv_dir).glob("*.csv"))
    unique_lines = set()
    
    # 遍历所有CSV文件
    for csv_file in csv_files:
        try:
            # 只读取'name'列，提高效率
            df = pd.read_csv(csv_file, encoding='GB18030', usecols=['name'])
            unique_lines.update(df['name'].dropna().unique())
        except:
            raise ValueError(f"文件 {csv_file} 中缺少 'name' 列或无法读取")
    
    # 保存为JSON（易于阅读）
    result = {
        "total_unique_lines": len(unique_lines),
        "total_files": len(csv_files),
        "lines": sorted(list(unique_lines))
    }
    
    # 保存到JSON文件
    with open("unique_lines-1.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"完成！找到 {len(unique_lines)} 条不重复线路")
    print("结果已保存到 unique_lines.json")
    
    return unique_lines

def condition_judge(I_off, J_off, I_P, I_Q, J_P, J_Q):  # 断开标志
    """判断线路运行状态"""
    if I_off == 1 or J_off == 1:
        return 0  # 断开状态
    elif I_P == 0 and I_Q == 0 and J_P == 0 and J_Q == 0:
        return 0  # 空载状态
    return 1  # 连接状态

def line_matrix(index_json, time_csv_file, mat_csv_file):
    """构建线路画像矩阵"""
    # 1. 从JSON加载所有线路名
    with open(index_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_lines = data.get('lines', [])  # 所有线路名的列表

    # 2. 读取当前时间点数据
    try:
        time_df = pd.read_csv(time_csv_file, encoding='GB18030', skiprows=[1])
    except Exception as e:
        print(f"  读取失败: {Path(time_csv_file).name} - {e}")
        raise ValueError("无法读取线路数据csv文件")

    # 3. 从文件名提取时间戳（列名）
    timestamp = Path(time_csv_file).stem

    # 4. 创建当前时间点的状态Series
    status_series = pd.Series(0, index=all_lines, name=timestamp)

    # 5. 为文件中存在的线路判断状态
    for _, row in time_df.iterrows():  # 遍历CSV的每一行
        line_name = str(row['name']) if 'name' in row else None
        
        if line_name and line_name in status_series.index:
            # 调用你的判断函数
            status = condition_judge(
                float(row.get('I_off', 0)),
                float(row.get('J_off', 0)),
                float(row.get('I_P', 0)),
                float(row.get('I_Q', 0)),
                float(row.get('J_P', 0)),
                float(row.get('J_Q', 0))
            )
            status_series[line_name] = status  # 更新该线路的状态

    # 6. 更新矩阵文件（增量写入）
    if Path(mat_csv_file).exists():
        # 情况A：矩阵文件已存在（不是第一个时间点）
        # 读取现有矩阵
        matrix_df = pd.read_csv(mat_csv_file, index_col=0)
        
        # 添加新列（当前时间点的状态）
        matrix_df[timestamp] = status_series
    else:
        # 情况B：矩阵文件不存在（第一个时间点）
        # 创建新矩阵（只有一列）
        matrix_df = pd.DataFrame(status_series)
    # 保存（覆盖原文件）
    matrix_df.to_csv(mat_csv_file)

    """
    def mat_iterate_append(csv_dir, index_json, mat_csv_file):
    for filename in os.listdir(csv_dir):
        csv_file_path = os.path.join(csv_dir, filename)
        line_matrix(index_json, csv_file_path, mat_csv_file)
    """

def mat_iterate_append(csv_dir, index_json, mat_csv_file):
    """
    批量处理CSV文件(简化版，用于测试)
    """
    csv_files = list(Path(csv_dir).glob("*.csv"))
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    for csv_file in csv_files[:]:
        print(f"\n处理: {csv_file.name}")
        try:
            line_matrix(index_json, csv_file, mat_csv_file)
        except Exception as e:
            raise ValueError(f"处理文件 {csv_file.name} 时出错: {e}")

def mat_iterate_append_time(csv_dir, index_json, mat_csv_file):
    csv_files = list(Path(csv_dir).glob("*.csv"))
    
    # 提取时间戳字符串排序（字典序=时间序，因为格式是%Y%m%d_%H%M）
    def time_key(f):
        # "国调_20230801_0000.csv" -> "20230801_0000"
        return f.stem.split('_', 1)[1]  # 按第一个_分割，取后面部分
    
    csv_files.sort(key=time_key)
    
    print(f"找到 {len(csv_files)} 个CSV文件")
    print(f"时间范围: {csv_files[0].name} -> {csv_files[-1].name}")
    
    for csv_file in csv_files:
        print(f"处理: {csv_file.name}", end='\r')  # 覆盖输出更清爽
        try:
            line_matrix(index_json, csv_file, mat_csv_file)
        except Exception as e:
            raise ValueError(f"处理文件 {csv_file.name} 时出错: {e}")
    print()  # 换行

# 使用
if __name__ == "__main__":
    flag = attain_parse_args()  # default=1
    if flag == 0:
        count_unique_lines("E:\\data\\ACline_CSV_Cleaned")
    elif flag == 1:
        line_matrix("unique_lines.json", "E:\\data\\国调_20230801_0000.csv", "line_matrix.csv")
    elif flag == 2:
        mat_iterate_append("E:\\data\\ACline_CSV_Cleaned", "unique_lines-1.json", "line_matrix.csv")
    elif flag == 3:
        mat_iterate_append_time("E:\\data\\ACline_CSV_Cleaned", "unique_lines-1.json", "line_matrix_time.csv")