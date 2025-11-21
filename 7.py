import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from datetime import datetime

def get_time(status: str):
    now = datetime.now()
    print(f"{status}: {now.strftime('%Y-%m-%d %H:%M:%S')}")

get_time("开始")

# 连接数据库
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)

# 创建字典形式的 cursor
cursor = conn.cursor(cursor_factory=RealDictCursor)
cursor.execute("SET search_path TO process2;")

# 优化后的SQL查询（包含地面点辐射值和排序）
cursor.execute("""
    SELECT 
        gid, 
        hori_idx, 
        array_agg(height ORDER BY height) AS heights,
        array_agg(rad_1 ORDER BY height) AS rad_1_list,
        array_agg(rad_2 ORDER BY height) AS rad_2_list,
        array_agg(rad_3 ORDER BY height) AS rad_3_list,
        MAX(CASE WHEN height = 0 THEN rad_1 END) AS ground_rad_1,
        MAX(CASE WHEN height = 0 THEN rad_2 END) AS ground_rad_2,
        MAX(CASE WHEN height = 0 THEN rad_3 END) AS ground_rad_3
    FROM bdg_verti_pts_radiance
    GROUP BY gid, hori_idx;
""")
result = cursor.fetchall()

# 向量化计算函数
def f(x):
    result = np.zeros_like(x, dtype=np.float64)
    mask1 = (x > 0) & (x <= 30)
    mask2 = x > 30
    x_masked = x[mask1]
    result[mask1] = ((x_masked**4.5) * np.exp(-0.5 * x_masked) / 5 + 5) / 5
    result[mask2] = (5/4) ** (-0.1 * x[mask2] + 2)
    return result

# 准备更新语句
sql_statement = """
    UPDATE bdg_verti_pts_radiance
    SET rad_1 = %s, rad_2 = %s, rad_3 = %s
    WHERE gid = %s AND hori_idx = %s AND height = %s;
"""

batch_size = 50000
updates = []
total_processed = 0

for row in result:
    # 跳过没有地面点的记录
    if None in (row['ground_rad_1'], row['ground_rad_2'], row['ground_rad_3']):
        continue
    
    # 转换为numpy数组
    heights = np.array(row['heights'], dtype=np.float64)
    if len(heights) == 0:
        continue
    
    # 过滤地面点并计算
    non_ground_mask = heights != 0
    non_ground_heights = heights[non_ground_mask]
    
    if len(non_ground_heights) == 0:
        continue
    
    # 向量化计算
    f_values = f(non_ground_heights)
    new_rad_1 = f_values * float(row['ground_rad_1'])
    new_rad_2 = f_values * float(row['ground_rad_2'])
    new_rad_3 = f_values * float(row['ground_rad_3'])
    
    # 生成更新数据（确保顺序一致）
    for h, nr1, nr2, nr3 in zip(non_ground_heights, new_rad_1, new_rad_2, new_rad_3):
        updates.append((
            float(nr1), float(nr2), float(nr3),
            row['gid'], row['hori_idx'], float(h)
        ))
    
    # 批量提交
    if len(updates) >= batch_size:
        execute_batch(cursor, sql_statement, updates)
        conn.commit()
        total_processed += len(updates)
        get_time(f"已提交 {total_processed} 条更新")
        updates = []

# 提交剩余数据
if updates:
    execute_batch(cursor, sql_statement, updates)
    conn.commit()
    total_processed += len(updates)
    get_time(f"最终提交 {len(updates)} 条更新")

get_time(f"处理完成 总更新量: {total_processed}")
cursor.close()
conn.close()