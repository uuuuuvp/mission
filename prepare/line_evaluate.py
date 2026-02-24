import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc("font",family='YouYuan')

def max_zero_streak_ratio(values):
    """计算最长连续0占总长度的比例"""
    if len(values) == 0:
        return 0
    
    max_streak = 0
    current = 0
    
    for v in values:
        if v == 0:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 0
    
    return max_streak / len(values)

df = pd.read_csv("E:/code/mission/line_matrix_time.csv", index_col=0)

# 批量计算所有目标（比逐行快100倍+）
results = pd.DataFrame({
    # '目标名': df.index,
    '出现次数': df.sum(axis=1),                    # 每行1的总数
    '占比': df.mean(axis=1),                       # 1的占比
    '空窗长度': df.apply(lambda row: max_zero_streak_ratio(row.values), axis=1)
    })

# print(results)
results.to_csv("E:/code/mission/analysis_results.csv", index=False, encoding='utf-8')

# 读取数据（任选一种格式）
df_results = pd.read_csv("E:/code/mission/analysis_results.csv", encoding='utf-8')

# 示例1：散点图 - 出现占比 vs 最大空窗占比
plt.figure(figsize=(10, 6))
plt.scatter(df_results['占比'], df_results['空窗长度'], alpha=0.5)
plt.xlabel('占比')
plt.ylabel('空窗长度')
plt.title('目标对象：出现频率 vs 最大空窗占比')
plt.grid(True, alpha=0.3)
plt.savefig("E:/code/mission/scatter_plot.png", dpi=150, bbox_inches='tight')
plt.show()

# 示例2：直方图 - 出现次数分布
plt.figure(figsize=(10, 6))
plt.hist(df_results['出现次数'], bins=50, edgecolor='black')
plt.xlabel('出现次数')
plt.ylabel('目标数量')
plt.title('出现次数分布')
plt.savefig("E:/code/mission/hist_plot.png", dpi=150, bbox_inches='tight')
plt.show()

# 示例3：找出异常目标（高出现占比但高空窗占比）
df_results['异常度'] = df_results['占比'] * df_results['空窗长度']
top_anomaly = df_results.nlargest(10, '异常度')
print("\n异常目标TOP10: ")
print(top_anomaly[[ '占比', '空窗长度', '异常度']])
