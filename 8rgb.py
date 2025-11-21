import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine
import laspy
from pyproj import CRS
from tqdm import tqdm
import time

# --- 1. 配置参数 ---
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "postgres",
    "user": "postgres",
    "password": ""
}

TABLE_CONFIG = {
    "schema": "whmax",
    "table": "bdg_verti_pts_radiance",
    "geom_col": "geom",
    "rad_cols": ["rad_1", "rad_2", "rad_3"]
}

OUTPUT_CONFIG = {
    "las_path": "E:/ALAN/output/verti_normalized_stream.las",
    "srid": 32650  # UTM Zone 50N
}

PROCESSING_CONFIG = {
    "chunk_size": 200000
}

# --- 2. 获取分位数 ---
def get_percentiles_from_db(engine, rad_col):
    query = f"""
    SELECT
        percentile_cont(0.01) WITHIN GROUP (ORDER BY "{rad_col}") AS p1,
        percentile_cont(0.99) WITHIN GROUP (ORDER BY "{rad_col}") AS p99
    FROM "{TABLE_CONFIG['schema']}"."{TABLE_CONFIG['table']}";
    """
    with engine.connect() as connection:
        result = pd.read_sql(query, connection)
        return result['p1'].iloc[0], result['p99'].iloc[0]

# --- 3. 主函数 ---
def process_data():
    start_time = time.time()
    db_url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    engine = create_engine(db_url)

    print("正在从数据库计算分位数...")
    percentiles = {}
    for col in TABLE_CONFIG['rad_cols']:
        p1, p99 = get_percentiles_from_db(engine, col)
        percentiles[col] = {'min': p1, 'max': p99}
        print(f" - 列 '{col}': 1% = {p1:.4f}, 99% = {p99:.4f}")

    # --- 4. 预设 SQL 查询 ---
    x_col = f"ST_X({TABLE_CONFIG['geom_col']})"
    y_col = f"ST_Y({TABLE_CONFIG['geom_col']})"
    z_col = f"ST_Z({TABLE_CONFIG['geom_col']})"
    all_cols = f"{x_col} AS x, {y_col} AS y, {z_col} AS z, " + ", ".join(f'"{c}"' for c in TABLE_CONFIG['rad_cols'])

    sql_query = f'SELECT {all_cols} FROM "{TABLE_CONFIG["schema"]}"."{TABLE_CONFIG["table"]}";'

    with engine.connect() as connection:
        total_rows = pd.read_sql(f'SELECT COUNT(*) FROM "{TABLE_CONFIG["schema"]}"."{TABLE_CONFIG["table"]}";', connection).iloc[0, 0]

    print("\n开始分块处理数据并流式写入LAS文件...")

    # --- 5. 创建 LAS 头信息 ---
    header = laspy.LasHeader(point_format=3, version="1.2")
    crs = CRS.from_epsg(OUTPUT_CONFIG["srid"])
    header.parse_crs(crs)

    # --- 6. 流式写入 LAS 文件 ---
    with laspy.open(OUTPUT_CONFIG["las_path"], mode="w", header=header) as writer, tqdm(total=total_rows, unit=" points") as pbar:
        for chunk_df in pd.read_sql_query(sql_query, engine, chunksize=PROCESSING_CONFIG['chunk_size']):
            # 裁剪 + 归一化 + 映射为uint16
            rad1_clipped = chunk_df[TABLE_CONFIG['rad_cols'][0]].clip(
                lower=percentiles['rad_1']['min'],
                upper=percentiles['rad_1']['max']
            )
            rad2_clipped = chunk_df[TABLE_CONFIG['rad_cols'][1]].clip(
                lower=percentiles['rad_2']['min'],
                upper=percentiles['rad_2']['max']
            )
            rad3_clipped = chunk_df[TABLE_CONFIG['rad_cols'][2]].clip(
                lower=percentiles['rad_3']['min'],
                upper=percentiles['rad_3']['max']
            )

            denom1 = percentiles['rad_1']['max'] - percentiles['rad_1']['min'] or 1
            denom2 = percentiles['rad_2']['max'] - percentiles['rad_2']['min'] or 1
            denom3 = percentiles['rad_3']['max'] - percentiles['rad_3']['min'] or 1

            # 创建 LAS 块
            las_chunk = laspy.LasData(header)
            las_chunk.x = chunk_df['x'].to_numpy()
            las_chunk.y = chunk_df['y'].to_numpy()
            las_chunk.z = chunk_df['z'].to_numpy()
            # las_chunk.red = ((rad1_clipped - percentiles['rad_1']['min']) / denom1 * 65535).astype(np.uint16)
            # las_chunk.green = ((rad2_clipped - percentiles['rad_2']['min']) / denom2 * 65535).astype(np.uint16)
            # las_chunk.blue = ((rad3_clipped - percentiles['rad_3']['min']) / denom3 * 65535).astype(np.uint16)
            las_chunk.red = ((rad1_clipped - percentiles['rad_1']['min']) / denom1 * 65535).fillna(10).clip(0, 65535).astype(np.uint16)
            las_chunk.green = ((rad2_clipped - percentiles['rad_2']['min']) / denom2 * 65535).fillna(10).clip(0, 65535).astype(np.uint16)
            las_chunk.blue = ((rad3_clipped - percentiles['rad_3']['min']) / denom3 * 65535).fillna(10).clip(0, 65535).astype(np.uint16)

            writer.write_points(las_chunk.points)
            pbar.update(len(chunk_df))

    print(f"\n任务完成！总耗时: {(time.time() - start_time):.2f} 秒。")

# --- 入口 ---
if __name__ == "__main__":
    process_data()
