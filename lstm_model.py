"""
LSTM 电力输电线路功率预测
流程：3σ → 归一化 → LSTM → 预测 → 保存结果
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import DataLoader, TensorDataset
import warnings
warnings.filterwarnings("ignore")

# ================== 参数 ==================
time_steps = 1660
seq_len = 24
epochs = 50
batch_size = 32
lr = 0.001

filename = "E:\\data\\output_lines\\华东.林静5197线.csv"
column_name = "I_Q"

# ================== 读取数据 ==================
df = pd.read_csv(filename)
power = pd.to_numeric(df[column_name], errors="coerce").values[:time_steps]

# ================== 3σ异常值处理 ==================
mean, std = power.mean(), power.std()
upper, lower = mean + 3 * std, mean - 3 * std
power = np.where((power > upper) | (power < lower), mean, power)

# ================== 归一化 ==================
scaler = MinMaxScaler()
power_scaled = scaler.fit_transform(power.reshape(-1, 1))

# ================== 构造序列 ==================
def create_dataset(data, seq_len):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i + seq_len])
        y.append(data[i + seq_len])
    return np.array(X), np.array(y)

X, y = create_dataset(power_scaled, seq_len)

train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)

train_loader = DataLoader(
    TensorDataset(X_train, y_train),
    batch_size=batch_size,
    shuffle=False
)

# ================== LSTM模型 ==================
class LSTMModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(1, 64, 2, batch_first=True)
        self.fc = nn.Linear(64, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LSTMModel().to(device)

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

# ================== 训练 ==================
for epoch in range(epochs):
    model.train()
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        loss = criterion(model(xb), yb)
        loss.backward()
        optimizer.step()
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{epochs}, Loss={loss.item():.6f}")

# ================== 预测 ==================
model.eval()
with torch.no_grad():
    y_pred = model(X_test.to(device)).cpu().numpy()

# 反归一化
y_test_inv = scaler.inverse_transform(y[train_size:])
y_pred_inv = scaler.inverse_transform(y_pred)

# ================== 保存结果 ==================
np.save("lstm_true.npy", y_test_inv)
np.save("lstm_pred.npy", y_pred_inv)

print("LSTM 预测完成，结果已保存")