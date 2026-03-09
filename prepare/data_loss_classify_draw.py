import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

# 读取JSON文件
with open('线路分类.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 计算每个区间的线路数量
intervals = list(data.keys())
counts = [len(data[interval]) for interval in intervals]

# 设置学术风格
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.linewidth'] = 1
plt.rcParams['figure.dpi'] = 300

# 创建断轴图
fig = plt.figure(figsize=(10, 5))

# 创建两个子图，共享x轴
gs = gridspec.GridSpec(2, 1, height_ratios=[1, 3], hspace=0.05)
ax1 = plt.subplot(gs[0])  # 上子图（显示0区间顶部）
ax2 = plt.subplot(gs[1])  # 下子图（显示其他区间）

# 找出0区间的索引
zero_idx = intervals.index('0')
zero_count = counts[zero_idx]
non_zero_max = max([c for i, c in enumerate(counts) if i != zero_idx])

# 绘制下子图（主要部分）- 所有柱子都画在这里
x = np.arange(len(intervals))
bars2 = ax2.bar(x, counts, color='white', edgecolor='black', linewidth=1)

# 设置下子图y轴范围（切掉0柱子的顶部）
ax2.set_ylim(0, non_zero_max * 1.2)

# 绘制上子图（只画0柱子的顶部）
# 注意：只画0区间这一个柱子，位置和宽度与下子图一致
bar_width = 0.8  # 默认bar宽度
ax1.bar(zero_idx, zero_count, width=bar_width, color='lightgray', 
        edgecolor='black', linewidth=1)
ax1.set_ylim(zero_count * 0.95, zero_count * 1.05)
ax1.set_xlim(ax2.get_xlim())  # 与下子图保持相同的x范围
ax1.set_xticks([])  # 不显示x轴刻度

# 隐藏上子图的下边缘和下子图的上边缘
ax1.spines.bottom.set_visible(False)
ax2.spines.top.set_visible(False)
ax1.tick_params(bottom=False, labelbottom=False)
ax2.tick_params(top=False)

# 添加断轴标记
d = 0.015
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=8,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)
ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

# 设置x轴标签
ax2.set_xticks(x)
ax2.set_xticklabels(intervals)

# 添加数值标签
for i, (bar, count) in enumerate(zip(bars2, counts)):
    if i == zero_idx:
        # 0区间的标签放在上子图
        ax1.text(bar.get_x() + bar.get_width()/2., zero_count * 0.97,
                f'{count}', ha='center', va='top', fontsize=10)
        # 在下子图的0柱子顶部添加一个箭头或标记
        ax2.text(bar.get_x() + bar.get_width()/2., non_zero_max * 1.1,
                '↑', ha='center', va='bottom', fontsize=12, fontweight='bold')
    else:
        # 非0区间的标签放在下子图
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + non_zero_max*0.03,
                f'{count}', ha='center', va='bottom', fontsize=9)

# 标签
ax2.set_xlabel('Missing Rate Interval (%)', fontsize=12)
ax2.set_ylabel('Number of Lines', fontsize=12)
ax1.set_ylabel('Zoomed', fontsize=10, labelpad=10)

# 标题
plt.suptitle('Distribution of Transmission Lines by Missing Rate', 
             fontsize=14, y=0.98)

# 调整布局
plt.tight_layout()

# 保存
plt.savefig('missing_rate_distribution.pdf', bbox_inches='tight')
plt.savefig('missing_rate_distribution.png', dpi=300, bbox_inches='tight')

plt.show()

# 打印统计信息
print("\n" + "="*50)
print("Statistics Summary")
print("="*50)
total = sum(counts)
for interval, count in zip(intervals, counts):
    print(f"{interval:>8}: {count:4d} ({count/total*100:5.2f}%)")
print("="*50)
print(f"   Total: {total} lines")




