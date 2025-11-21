import cv2
import numpy as np
import psycopg2
import pandas as pd
from scipy.stats import pearsonr,spearmanr
from sqlalchemy import create_engine
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score


# 连接PostgreSQL数据库
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)

# 查询实验结果和实际结果
query = """
    SELECT c.ori_rad_1,c.svi_rad_1,c.svi_rad_2,c.svi_rad_3
    FROM sgcommercial.fan_vs_pan_9 c
"""
df = pd.read_sql(query, conn)

# 关闭数据库连接
conn.close()

# 计算MAE, RMSE, MedAE, 皮尔逊相关系数R和R², 相对误差
def calculate_metrics(experiment, actual):
    mae = mean_absolute_error(actual, experiment)
    rmse = np.sqrt(mean_squared_error(actual, experiment))
    medae = median_absolute_error(actual, experiment)
    R, p_value = pearsonr(actual, experiment)  # 计算皮尔逊相关系数
    R2 = R ** 2  # 计算R²
    rho, rho_p_value = spearmanr(actual, experiment)  # 计算斯皮尔曼相关系数
    return mae, rmse, medae, R, p_value, R2, rho, rho_p_value

metrics = {}
# 分别计算pan_total_rad vs rgb_total_rad
mae, rmse, medae, R, p_value, R2, rho, rho_p_value = calculate_metrics(df['ori_rad_1'], df['svi_rad_1'])
metrics = {
    'MAE': mae,
    'RMSE': rmse,
    'MedAE': medae,
    'R': R,
    'p_value': p_value,
    'R²': R2,
    'Spearman rho': rho,
    'Spearman p_value': rho_p_value
}

# 打印结果
print("band1:")
for metric_name, metric_value in metrics.items():
    print(f"{metric_name}: {metric_value:.2f}")

metrics = {}
# 分别计算pan_total_rad vs rgb_total_rad
mae, rmse, medae, R, p_value, R2, rho, rho_p_value = calculate_metrics(df['ori_rad_1'], df['svi_rad_2'])
metrics = {
    'MAE': mae,
    'RMSE': rmse,
    'MedAE': medae,
    'R': R,
    'p_value': p_value,
    'R²': R2,
    'Spearman rho': rho,
    'Spearman p_value': rho_p_value
}
# 打印结果
print("band2:")
for metric_name, metric_value in metrics.items():
    print(f"{metric_name}: {metric_value:.2f}")

metrics = {}
# 分别计算pan_total_rad vs rgb_total_rad
mae, rmse, medae, R, p_value, R2, rho, rho_p_value = calculate_metrics(df['ori_rad_1'], df['svi_rad_3'])
metrics = {
    'MAE': mae,
    'RMSE': rmse,
    'MedAE': medae,
    'R': R,
    'p_value': p_value,
    'R²': R2,
    'Spearman rho': rho,
    'Spearman p_value': rho_p_value
}
# 打印结果
print("band3:")
for metric_name, metric_value in metrics.items():
    print(f"{metric_name}: {metric_value:.2f}")

# 分别计算pan_total_rad vs rgb_total_rad
mae, rmse, medae, R, p_value, R2, rho, rho_p_value = calculate_metrics(df['ori_rad_1'], df['svi_rad_3']+df['svi_rad_2']+df['svi_rad_1'])
metrics = {
    'MAE': mae,
    'RMSE': rmse,
    'MedAE': medae,
    'R': R,
    'p_value': p_value,
    'R²': R2,
    'Spearman rho': rho,
    'Spearman p_value': rho_p_value
}
# 打印结果
print("band1+2+3:")
for metric_name, metric_value in metrics.items():
    print(f"{metric_name}: {metric_value:.2f}")