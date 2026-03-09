import pandas as pd
import json

# 读取CSV文件
df = pd.read_csv("E:\code\mission\data_loss_matrix - 副本.csv")

# 获取线路名（第一列）和missing_rate（最后一列）
line_names = df.iloc[:, 0]  # 第一列
missing_rates = df.iloc[:, -1]  # 最后一列

# 定义区间
intervals = {
    '0': [],
    '0-5': [],
    '5-10': [],
    '10-20': [],
    '20-40': [],
    '40-60': [],
    '60-80': [],
    '80-100': []
}

# 分类
for name, rate in zip(line_names, missing_rates):
    # 转换rate为数值
    if isinstance(rate, str):
        rate = float(rate.replace('%', '').strip())
    else:
        rate = float(rate)
    
    # 分类逻辑
    if rate == 0:
        intervals['0'].append(name)
    elif rate <= 5:
        intervals['0-5'].append(name)
    elif rate <= 10:
        intervals['5-10'].append(name)
    elif rate <= 20:
        intervals['10-20'].append(name)
    elif rate <= 40:
        intervals['20-40'].append(name)
    elif rate <= 60:
        intervals['40-60'].append(name)
    elif rate <= 80:
        intervals['60-80'].append(name)
    elif rate <= 100:
        intervals['80-100'].append(name)

# 写入JSON文件
with open('线路分类.json', 'w', encoding='utf-8') as f:
    json.dump(intervals, f, ensure_ascii=False, indent=2)
