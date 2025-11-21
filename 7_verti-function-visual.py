import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体为黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
# 定义函数
def R(h):
    k = 11
    delta = 5
    return (h**(k/2 - 1) * np.exp(-h/2)) / (2**(k/2) * delta) + 1

# 生成h的值
h = np.linspace(0, 80, 6400)  # 从0到20，生成400个点

# 计算R(h)
R_values = R(h)

# 绘制图像
plt.figure(figsize=(8, 6))
plt.plot(h, R_values, label="R(h)")
plt.xlabel("高度")
plt.ylabel("R(h)")
plt.title("垂直辐射值随高度变化拟合函数 R(h)")
plt.legend()
plt.grid(True)
plt.show()