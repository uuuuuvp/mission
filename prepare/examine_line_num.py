import os
from pathlib import Path
import re

def count_acline_lines(qs_file_path):
    """统计单个QS文件中ACline块的行数"""
    count = 0
    in_acline = False
    
    try:
        with open(qs_file_path, 'r', encoding='GB18030') as f:
            for line in f:
                line = line.strip()
                
                # 进入ACline块
                if line.startswith('<ACline::'):
                    in_acline = True
                    continue
                
                # 退出ACline块
                if line.startswith('</ACline::'):
                    break
                
                # 在ACline块内且是数据行
                if in_acline and line.startswith('#'):
                    count += 1
                    
        return count
    except Exception as e:
        print(f"处理文件 {qs_file_path} 时出错: {e}")
        return -1  # 错误标记

def validate_acline_counts(directory_path):
    """验证目录下所有QS文件的ACline行数"""
    directory = Path(directory_path)
    qs_files = list(directory.glob('*.qs'))
    
    print(f"找到 {len(qs_files)} 个QS文件")
    print("="*60)
    
    counts = {}
    for qs_file in qs_files:
        count = count_acline_lines(qs_file)
        counts[qs_file.name] = count
        
        if count > 0:
            print(f"{qs_file.name:40} → {count:6} 行")
        else:
            print(f"{qs_file.name:40} → 错误或未找到ACline数据")
    
    # 分析结果
    print("\n" + "="*60)
    print("统计结果:")
    print("-"*60)
    
    if counts:
        valid_counts = [c for c in counts.values() if c > 0]
        
        if valid_counts:
            print(f"有效文件数量: {len(valid_counts)}")
            print(f"最小行数: {min(valid_counts)}")
            print(f"最大行数: {max(valid_counts)}")
            print(f"平均行数: {sum(valid_counts)/len(valid_counts):.2f}")
            
            # 检查一致性
            if min(valid_counts) == max(valid_counts):
                print("✅ 所有文件ACline行数完全一致！")
                print(f"每次都是 {valid_counts[0]} 条线路")
            else:
                print("⚠️  文件间行数不一致！")
                print(f"差异范围: {max(valid_counts)-min(valid_counts)} 行")
                
                # 找出不一致的文件
                unique_counts = set(valid_counts)
                if len(unique_counts) < 10:  # 如果只有少数几种行数
                    print("\n行数分布:")
                    for count_val in sorted(unique_counts):
                        num_files = sum(1 for c in valid_counts if c == count_val)
                        print(f"  {count_val:6} 行: {num_files:3} 个文件")
        else:
            print("❌ 未找到任何有效的ACline数据")
    else:
        print("❌ 没有找到任何QS文件")
    
    return counts

# 使用示例
if __name__ == "__main__":
    directory = "E:\data\QS文件"  # 你的QS文件目录
    counts = validate_acline_counts(directory)