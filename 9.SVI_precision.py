import cv2
import numpy as np
import psycopg2
import pandas as pd
from scipy.stats import pearsonr,spearmanr
from sqlalchemy import create_engine
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score

# # 读取图片
# image = cv2.imread('dewarp-output-re2.png')  # 替换为你的图片路径

# # 获取图片的尺寸
# height, width, channels = image.shape

# # 计算每个扇形的宽度
# sector_width = width / 18

# # 提取R、G、B分量
# B, G, R = cv2.split(image)

# # 初始化存储所有区域R、G、B像素值之和的列表
# sector_sums = []

# # 遍历每个扇形区域
# for sector_index in range(0, 18):  # 从0到17
#     # 计算当前扇形的左右边界
#     left_boundary = 0.5 * width - sector_width * 0.5 + sector_index * sector_width
#     right_boundary = left_boundary + sector_width

#     # 边界控制，如果超出宽度则循环回到起始位置
#     if left_boundary >= width:
#         left_boundary -= width
#     if right_boundary >= width:
#         right_boundary -= width

#     # 初始化R、G、B像素值之和
#     sum_R, sum_G, sum_B = 0, 0, 0
#     # print((left_boundary,right_boundary,sector_index))
#     if(sector_index!=9):
#         # 计算R、G、B像素值之和
#         for y in range(height):
#             for x in range(int(left_boundary),int(min(right_boundary, width))):
#                 sum_R += int(R[y, x])
#                 sum_G += int(G[y, x])
#                 sum_B += int(B[y, x])
#     else:
#         for y in range(height):
#             for x in range(int(left_boundary),int(width)):
#                 sum_R += int(R[y, x])
#                 sum_G += int(G[y, x])
#                 sum_B += int(B[y, x])
#         for y in range(height):
#             for x in range(0,int(right_boundary)):
#                 sum_R += int(R[y, x])
#                 sum_G += int(G[y, x])
#                 sum_B += int(B[y, x])
#     # 将当前区域的R、G、B像素值之和添加到列表中
#     sector_sums.append([sum_R, sum_G, sum_B])
# print(sector_sums)
# 连接PostgreSQL数据库
# conn = psycopg2.connect(
#     dbname="postgres",
#     user="postgres",
#     password="",
#     host="localhost",
#     port="5432"
# )

# cur = conn.cursor()
# # 更新fan表
# for i, sums in enumerate(sector_sums):
#     cur.execute("""
#         UPDATE sgcommercial.fan
#         SET svi_rad_1 = %s, svi_rad_2 = %s, svi_rad_3 = %s
#         WHERE id = %s;
#     """, (int(sums[0]), int(sums[1]), int(sums[2]), i+1))

# # 提交事务
# conn.commit()

# # 关闭数据库连接
# cur.close()
# conn.close()


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
    SELECT c.rad_1, c.rad_2,c.rad_3,c.svi_rad_1,c.svi_rad_2,c.svi_rad_3
    FROM sgre2.fan_9 c
"""
df = pd.read_sql(query, conn)

# 关闭数据库连接
conn.close()

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
mae, rmse, medae, R, p_value, R2, rho, rho_p_value = calculate_metrics(df['rad_1'], df['svi_rad_1'])
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
mae, rmse, medae, R, p_value, R2, rho, rho_p_value = calculate_metrics(df['rad_2'], df['svi_rad_2'])
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
mae, rmse, medae, R, p_value, R2, rho, rho_p_value = calculate_metrics(df['rad_3'], df['svi_rad_3'])
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