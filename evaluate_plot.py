"""
evaluate_plot.py - 多步预测评估版本
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_multistep(y_true, y_pred, model_name):
    """
    评估多步预测结果
    y_true, y_pred shape: [n_samples, pred_steps, 1]
    """
    # 展平为2D进行评估
    n_samples, n_steps, _ = y_true.shape
    y_true_flat = y_true.reshape(-1, 1)
    y_pred_flat = y_pred.reshape(-1, 1)
    
    # 计算总体指标
    mae = mean_absolute_error(y_true_flat, y_pred_flat)
    rmse = np.sqrt(mean_squared_error(y_true_flat, y_pred_flat))
    mape = np.mean(np.abs((y_true_flat - y_pred_flat) / (y_true_flat + 1e-10))) * 100
    r2 = r2_score(y_true_flat, y_pred_flat)
    
    print(f"\n{model_name} 模型评估结果 (总体):")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAPE: {mape:.2f}%")
    print(f"R²: {r2:.4f}")
    
    # # 计算每个预测步长的指标
    # print(f"\n{model_name} 每个预测步长的MAE:")
    # for step in range(n_steps):
    #     step_mae = mean_absolute_error(y_true[:, step, 0], y_pred[:, step, 0])
    #     print(f"  步长 {step+1}: {step_mae:.4f}")
    
    
    return {'MAE': mae, 'RMSE': rmse, 'MAPE': mape, 'R2': r2}

# 加载数据
lstm_true = np.load("lstm_true_84_12_J_Q.npy")
lstm_pred = np.load("lstm_pred_84_12_J_Q.npy")

print(f"数据形状: 真实值 {lstm_true.shape}, 预测值 {lstm_pred.shape}")

# 评估
results = evaluate_multistep(lstm_true, lstm_pred, "LSTM")# """
# 模型评估与可视化
# 指标：R2 / MAE / RMSE / MAPE
# """

# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# plt.rcParams["font.sans-serif"] = ["SimHei"]
# plt.rcParams["axes.unicode_minus"] = False

# def evaluate(y_true, y_pred, name):
#     mae = mean_absolute_error(y_true, y_pred)
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred))
#     r2 = r2_score(y_true, y_pred)
#     mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

#     print(f"\n===== {name} 评估指标 =====")
#     print(f"R^2  : {r2:.4f}")
#     print(f"MAE  : {mae:.4f}")
#     print(f"RMSE : {rmse:.4f}")
#     print(f"MAPE : {mape:.2f}%")

# # ================== 加载结果 ==================
# lstm_true = np.load("lstm_true.npy")
# lstm_pred = np.load("lstm_pred.npy")

# arima_true = np.load("arima_true.npy")
# arima_pred = np.load("arima_pred.npy")

# # ================== 评估 ==================
# evaluate(lstm_true, lstm_pred, "LSTM")
# evaluate(arima_true, arima_pred, "ARIMA")

# # ================== 可视化 ==================
# plt.figure(figsize=(10, 4))
# plt.plot(lstm_true, label="真实值")
# plt.plot(lstm_pred, label="LSTM预测")

# # plt.plot(arima_true, label="真实值")
# plt.plot(arima_pred, label="ARIMA预测")
# plt.legend()
# plt.title("电力输电线路功率预测对比")
# plt.tight_layout()
# plt.show()