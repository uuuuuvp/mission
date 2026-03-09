"""
ARIMA 电力输电线路功率预测（基线模型）
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

# ================== 参数 ==================
time_steps = 1660
filename = r"E:\data\output_lines\华东.林远5133线.csv"
column_name = "J_Q"

# ================== 读取数据 ==================
df = pd.read_csv(filename)
power = pd.to_numeric(df[column_name], errors="coerce").values[:time_steps]

# ================== 3σ异常值处理 ==================
mean, std = power.mean(), power.std()
upper, lower = mean + 3 * std, mean - 3 * std
power = np.where((power > upper) | (power < lower), mean, power)

# ================== 划分数据 ==================
train_size = int(len(power) * 0.8)
train, test = power[:train_size], power[train_size:]

# ================== ARIMA建模 ==================
model = ARIMA(train, order=(5, 1, 2))
model_fit = model.fit()

# ================== 预测 ==================
forecast = model_fit.forecast(steps=len(test))

# ================== 保存结果 ==================
np.save("arima_true.npy", test)
np.save("arima_pred.npy", forecast)

print("ARIMA 预测完成，结果已保存")