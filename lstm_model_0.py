"""
LSTM 电力输电线路功率预测（多步预测版本）
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
seq_len = 84  # 输入序列长度
pred_len = 12  # 预测序列长度
epochs = 50
batch_size = 32
lr = 0.001
hidden_size = 64  # LSTM隐藏层大小

filename = "E:\\data\\output_lines\\华东.林静5197线.csv"
column_name = "J_Q"

# ================== 读取数据 ==================
df = pd.read_csv(filename)
power = pd.to_numeric(df[column_name], errors="coerce").values[:time_steps]

# ================== 3σ异常值处理 ==================
mean, std = power.mean(), power.std()
upper, lower = mean + 3 * std, mean - 3 * std
power = np.where((power > upper) | (power < lower), mean, power)

# ================== 归一化 ==================
scaler = MinMaxScaler()
power_scaled = scaler.fit_transform(power.reshape(-1, 1)).flatten()

# ================== 构造多步预测序列 ==================
def create_multistep_dataset(data, seq_len, pred_len):
    X, y = [], []
    for i in range(len(data) - seq_len - pred_len + 1):
        X.append(data[i:i + seq_len])
        y.append(data[i + seq_len:i + seq_len + pred_len])
    return np.array(X), np.array(y)

X, y = create_multistep_dataset(power_scaled, seq_len, pred_len)

# 8:2 划分（保留时间顺序，不打乱）
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

print(f"训练集形状: X_train {X_train.shape}, y_train {y_train.shape}")
print(f"测试集形状: X_test {X_test.shape}, y_test {y_test.shape}")

# 转换为tensor
X_train = torch.tensor(X_train, dtype=torch.float32).unsqueeze(-1)  # [样本, seq_len, 1]
y_train = torch.tensor(y_train, dtype=torch.float32).unsqueeze(-1)  # [样本, pred_len, 1]
X_test = torch.tensor(X_test, dtype=torch.float32).unsqueeze(-1)
y_test = torch.tensor(y_test, dtype=torch.float32).unsqueeze(-1)

# 注意：不使用shuffle，保持时间顺序
train_dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)

# ================== 多步预测LSTM模型 ==================
class MultistepLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, pred_len=24):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.pred_len = pred_len
        
        # 自定义输入变换
        self.input_proj = nn.Linear(input_size, hidden_size)
        
        # LSTM层
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers, batch_first=True)
        
        # 自定义输出变换
        self.output_proj = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        # x shape: [batch, seq_len, 1]
        
        # 输入变换
        x = self.input_proj(x)  # [batch, seq_len, hidden_size]
        
        # LSTM处理，返回所有时间步的输出
        out, _ = self.lstm(x)  # [batch, seq_len, hidden_size]
        
        # 输出变换到预测维度
        out = self.output_proj(out)  # [batch, seq_len, 1]
        
        # 只取最后pred_len个预测
        return out[:, -self.pred_len:, :]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MultistepLSTM(input_size=1, hidden_size=hidden_size, 
                      num_layers=2, pred_len=pred_len).to(device)

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lr)

# ================== 训练（带验证） ==================
best_loss = float('inf')
for epoch in range(epochs):
    model.train()
    train_loss = 0
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        y_pred = model(xb)
        loss = criterion(y_pred, yb)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    
    # 验证
    model.eval()
    with torch.no_grad():
        val_pred = model(X_test.to(device))
        val_loss = criterion(val_pred, y_test.to(device)).item()
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{epochs}, Train Loss={train_loss/len(train_loader):.6f}, Val Loss={val_loss:.6f}")
    
    # 保存最佳模型
    if val_loss < best_loss:
        best_loss = val_loss
        torch.save(model.state_dict(), 'best_model.pth')
        print(f'  -> Best model saved (loss: {val_loss:.6f})')

# ================== 加载最佳模型进行预测 ==================
model.load_state_dict(torch.load('best_model.pth'))
model.eval()
with torch.no_grad():
    y_pred = model(X_test.to(device)).cpu().numpy()  # [n_test, pred_len, 1]

# ================== 反归一化（修复版本） ==================
print(f"预测结果形状: {y_pred.shape}")

# 方法1：重塑数据再反归一化
n_samples = y_pred.shape[0]
n_steps = y_pred.shape[1]

# 将预测结果重塑为2D数组进行反归一化
y_pred_2d = y_pred.reshape(-1, 1)  # [n_samples * pred_len, 1]
y_pred_inv_2d = scaler.inverse_transform(y_pred_2d)  # 反归一化

# 重塑回原来的3D形状
y_pred_inv = y_pred_inv_2d.reshape(n_samples, n_steps, 1)

# 同样处理真实值
y_test_np = y_test.cpu().numpy()  # [n_test, pred_len, 1]
y_test_2d = y_test_np.reshape(-1, 1)
y_test_inv_2d = scaler.inverse_transform(y_test_2d)
y_test_inv = y_test_inv_2d.reshape(n_samples, n_steps, 1)

print(f"反归一化后形状: 预测 {y_pred_inv.shape}, 真实 {y_test_inv.shape}")

# ================== 保存结果 ==================
np.save(f"lstm_true_{seq_len}_{pred_len}_{column_name}.npy", y_test_inv)
np.save(f"lstm_pred_{seq_len}_{pred_len}_{column_name}.npy", y_pred_inv)

print("LSTM 多步预测完成，结果已保存")
print(f"预测形状: {y_pred_inv.shape} (样本数, 预测步数, 1)")

# ================== 可选：可视化第一个样本的预测结果 ==================
import matplotlib.pyplot as plt

# 绘制第一个测试样本的预测结果
plt.figure(figsize=(12, 6))
plt.plot(y_test_inv[0, :, 0], label='True', marker='o')
plt.plot(y_pred_inv[0, :, 0], label='Predicted', marker='s')
plt.xlabel('Time Step')
plt.ylabel('Power')
plt.title('LSTM Multi-step Prediction (First Test Sample)')
plt.legend()
plt.grid(True)
plt.show()