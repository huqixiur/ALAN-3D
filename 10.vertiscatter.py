import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error

# --- 第1步：读取数据 ---
# (此部分无改动)
try:
    df = pd.read_excel('E:/科研/paper/V4/夜光.xlsx', sheet_name=0, header=None,
                      names=['floor_number', 'col_b', 'brightness', 'col_d', 'col_e'])
except FileNotFoundError:
    print("错误: 文件 'E:/科研/paper/V4/夜光.xlsx' 未找到。请检查路径是否正确。")
    exit()
except ImportError:
    print("错误: 缺少 'openpyxl' 库。请运行 'pip install openpyxl' 来安装它。")
    exit()

df.dropna(subset=['floor_number', 'brightness'], inplace=True)
df['floor_number'] = pd.to_numeric(df['floor_number'], errors='coerce')
df['brightness'] = pd.to_numeric(df['brightness'], errors='coerce')
df.dropna(subset=['floor_number', 'brightness'], inplace=True)
df['height_m'] = df['floor_number'] * 3
x_data = df['height_m']
y_data = df['brightness']

# --- 计算亮度的分位数排名 ---
# (此部分无改动)
df['brightness_quantile'] = df['brightness'].rank(pct=True)

# --- 第2步：拟合 ---
# (此部分无改动)
def skewed_func(h, A, B, C):
    h_safe = h + 1e-9
    return A * (h_safe**4.5) * np.exp(-h_safe / (2 * B)) + C

popt, _ = curve_fit(skewed_func, x_data, y_data, p0=[1, 1.1, y_data.min()], maxfev=10000)
A_fit, B_fit, C_fit = popt
peak_height = 9 * B_fit
peak_brightness = skewed_func(peak_height, A_fit, B_fit, C_fit)

# --- 第3步：生成曲线 ---
# (此部分无改动)
h_fit = np.linspace(0, x_data.max(), 500)
brightness_fit = skewed_func(h_fit, *popt)

def R(h):
    k = 8.46
    delta = 1.5
    return (h**(k/2 - 1) * np.exp(-h/2)) / (2**(k/2) * delta) + 1
h_theory = np.linspace(0, 110, 6400)
R_values = 60 * R(h_theory)

# --- 第4步：计算相似度 ---
# (此部分无改动)
interp_R = np.interp(h_fit, h_theory, R_values)
rmse = np.sqrt(mean_squared_error(interp_R, brightness_fit))
sim_score = 1 - rmse / (np.max(interp_R) - np.min(interp_R))
sim_text = f'Similarity = {sim_score:.3f}'

# --- 第5步：绘图 (核心修改) ---
# --- 设置字体与风格 ---
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
sns.set(style="whitegrid", font='serif') # 应用serif字体风格

# --- 调整画布尺寸以获得更紧凑的观感 ---
plt.figure(figsize=(7, 5.5), dpi=150) # 适度缩小画布

# --- 绘制散点图 ---
scatter = plt.scatter(df['height_m'], df['brightness'],
                      c=df['brightness_quantile'],
                      cmap='RdYlBu_r',
                      s=50, alpha=0.9, edgecolor='none', label='Observed')

# --- 绘制曲线 ---
plt.plot(h_fit, brightness_fit, color='#377eb8', lw=2.5, alpha=0.9, linestyle='-', label='Fitted Curve')
plt.plot(h_theory, R_values, color='#e41a1c', lw=2.5, alpha=0.6, linestyle='--', label='Estimated Vertical Function')

# --- 绘制峰值标注 ---
plt.axvline(x=peak_height, color='#4daf4a', linestyle=':', lw=2, label=f'Peak Height: {peak_height:.2f} m')
plt.plot(peak_height, peak_brightness, 'o', color='#4daf4a', markersize=8, markeredgecolor='black')

# --- 调整标签与标题 ---
plt.xlabel('Height (m)', fontsize=13)
plt.ylabel('Brightness (a.u.)', fontsize=13)
plt.title('Vertical Profile of Nighttime Light Intensity', fontsize=14, pad=10) # 减小标题与图像的间距

# --- 颜色条 ---
cbar = plt.colorbar(scatter)
cbar.set_label('Brightness Quantile', fontsize=13)

# --- 图例 ---
plt.legend(loc='upper right', fontsize=9, frameon=True, title=sim_text)

# --- 网格与最终布局调整 ---
plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.4)
plt.tight_layout(pad=0.5) # 调用tight_layout确保元素间距紧凑

# --- 保存图像 ---
# bbox_inches='tight' 是关键，它会裁掉保存图像时多余的白边
plt.savefig('final_plot_compact.png', dpi=300, bbox_inches='tight')

# --- 输出信息 ---
print(f"[√] 最终图表已保存为 final_plot_compact.png")
print(f"[√] 峰值高度为: {peak_height:.2f} 米，亮度为: {peak_brightness:.2f}")
print(f"[√] 曲线相似度（归一化RMSE）：{sim_score:.3f}")