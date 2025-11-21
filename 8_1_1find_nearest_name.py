import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# 计算两点之间的距离（单位：公里）
def haversine(lon1, lat1, lon2, lat2):
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 
    r = 6371  # 地球平均半径，单位为公里
    return c * r

# 读取CSV文件
def find_nearest_point(csv_file, target_lat, target_lon):
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"文件未找到，请检查路径：{csv_file}")
        return None
    
    # 计算每个点到目标点的距离
    df['distance'] = df.apply(lambda row: haversine(target_lon, target_lat, row['night_svi_lon'], row['night_svi_lat']), axis=1)
    
    # 找到距离最近的点
    idx_nearest = df['distance'].idxmin()
    nearest_point = df.loc[idx_nearest]
    
    # 返回最近点的坐标、day_svi_id和行号
    return nearest_point[['night_svi_lat', 'night_svi_lon', 'day_svi_id']], idx_nearest   # +1 是因为行号通常从1开始计数

# 给定的经纬度坐标
target_lon, target_lat =103.8443238, 1.2853383
# CSV文件路径
csv_file_path = r'E://文献//资料收集//3.新加坡//day_night_SVI_pairs.csv'  # 确保文件名和路径正确

# 执行函数并打印结果
result = find_nearest_point(csv_file_path, target_lat, target_lon)
if result is not None:
    nearest, row_number = result
    print("最近的点坐标和ID：")
    print(nearest)
    print(f"该点位于第 {row_number} 行")
else:
    print("未能找到最近点")