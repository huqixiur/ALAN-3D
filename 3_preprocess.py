import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from scipy.optimize import lsq_linear
from datetime import datetime
import numpy as np
from tqdm import tqdm

def get_time(status:str):
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(status, formatted_time)

get_time("开始：")

def all_band():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        # 【说明】下面这行可以保留，也可以删除，因为我们已经在查询中明确指定了 whmax。
        cursor.execute("SET search_path TO whmax;") 
        
        get_time("数据库连接成功，开始查询...")
        
        # ==========================================================
        # == 【修改点 1】: 在表名前面明确加上模式名 "whmax."
        # ==========================================================
        cursor.execute("""
            SELECT fishnet_id, "PH",
            area_101,area_201,area_202,area_301,area_401,area_402,
            area_403,area_501,area_502,area_503,area_504,area_505
            FROM whmax.rgb_fishnet_10_radiance 
        """)
        r10 = cursor.fetchall()
        r10_dict = {row['fishnet_id']: row for row in r10}

        # ==========================================================
        # == 【修改点 2】: 在表名前面明确加上模式名 "whmax."
        # ==========================================================
        cursor.execute("""SELECT id, b1,b2,b3,pan_list FROM whmax.fishnet_40""")
        rows = cursor.fetchall()
        get_time('查询结束')

        # 1. 数据预处理
        lulc_idx=[101,201,202,301,401,402,403,501,502,503,504,505]
        all_fishnet_ids = list(r10_dict.keys())
        id_to_idx_map = {fid: i for i, fid in enumerate(all_fishnet_ids)}
        num_r10_rows = len(all_fishnet_ids)
        area_columns = [f'area_{idx}' for idx in lulc_idx]
        r10_data_np = np.zeros((num_r10_rows, 1 + len(area_columns)))

        for fid, row_data in r10_dict.items():
            idx = id_to_idx_map.get(fid)
            if idx is not None:
                r10_data_np[idx, 0] = row_data.get('PH', 0)
                for i, col_name in enumerate(area_columns):
                    r10_data_np[idx, i + 1] = row_data.get(col_name, 0)
        
        get_time("Numpy数据预处理完成")
        
        updates_f40, updates_f10 = [], []
        batch_size, counter = 10000, 0

        # 2. 主循环
        for row in tqdm(rows, desc="正在处理40m格网"):
            counter += 1
            id, b11, b22, b33 = row['id'], row['b1'], row['b2'], row['b3']

            if not (np.isfinite(b11) and np.isfinite(b22) and np.isfinite(b33)): continue
            pan_list = row['pan_list']
            if not pan_list: continue
            indices = [id_to_idx_map[fid] for fid in pan_list if fid in id_to_idx_map]
            if not indices: continue

            r10_subset = r10_data_np[indices]
            A = r10_subset[:, 1:]
            PH_list = r10_subset[:, 0]
            b1, b2, b3 = PH_list * b11, PH_list * b22, PH_list * b33
            
            # ... (这部分核心算法逻辑保持完全不变)
            active_cols_mask = A.any(axis=0)
            active_indices = np.where(active_cols_mask)[0]

            if active_indices.size == 0 or A.shape[0] < 1:
                # ...
                continue

            A_eff = A[:, active_indices]

            try:
                res1 = lsq_linear(A_eff, b1, bounds=(0, np.inf))
                res2 = lsq_linear(A_eff, b2, bounds=(0, np.inf))
                res3 = lsq_linear(A_eff, b3, bounds=(0, np.inf))
                x1_eff, x2_eff, x3_eff = res1.x, res2.x, res3.x
            except Exception as e:
                # ...
                continue
            
            num_lulc_types = 12
            x1_np = np.zeros(num_lulc_types)
            x1_np[active_indices] = x1_eff
            x2_np = np.zeros(num_lulc_types)
            x2_np[active_indices] = x2_eff
            x3_np = np.zeros(num_lulc_types)
            x3_np[active_indices] = x3_eff
            
            b1_np, b2_np, b3_np = np.dot(A,x1_np), np.dot(A,x2_np), np.dot(A,x3_np)
            x = np.vstack([x1_np, x2_np, x3_np]).T
            updates_f40.append(tuple(x.tolist()) + (id,))
            b_sum = b1_np + b2_np + b3_np
            b_sum[b_sum == 0] = 1e-9
            
            f10_all_bands_np = (A.T[:, :, np.newaxis] * x[:, np.newaxis, :]) * (PH_list / b_sum)[np.newaxis, :, np.newaxis]
            f10_all_bands_np = f10_all_bands_np.transpose(1, 0, 2)
            
            for i, idx in enumerate(indices):
                original_fishnet_id = all_fishnet_ids[idx]
                updates_f10.append(tuple(f10_all_bands_np[i].tolist()) + (original_fishnet_id,))
            
            # 批处理逻辑
            if counter % batch_size == 0 and updates_f40:
                get_time(f"处理完 {counter}行，开始提交批次...")
                # ==========================================================
                # == 【修改点 3】: 在表名前面明确加上模式名 "whmax."
                # ==========================================================
                cursor.executemany("""UPDATE whmax.fishnet_40 SET x101=%s,x201=%s,x202=%s,x301=%s,x401=%s,x402=%s,x403=%s,x501=%s,x502=%s,x503=%s,x504=%s,x505=%s WHERE id=%s""", updates_f40)
                cursor.executemany("""UPDATE whmax.fishnet_10 SET r101=%s,r201=%s,r202=%s,r301=%s,r401=%s,r402=%s,r403=%s,r501=%s,r502=%s,r503=%s,r504=%s,r505=%s WHERE fishnet_id=%s""", updates_f10)
                conn.commit()
                updates_f40, updates_f10 = [], []
                get_time("批次提交完成，内存已释放。")

        # 3. 处理循环结束后剩余的数据
        if updates_f40:
            get_time("开始提交最后一批剩余数据...")
            # ==========================================================
            # == 【修改点 4】: 在表名前面明确加上模式名 "whmax."
            # ==========================================================
            cursor.executemany("""UPDATE whmax.fishnet_40 SET x101=%s,x201=%s,x202=%s,x301=%s,x401=%s,x402=%s,x403=%s,x501=%s,x502=%s,x503=%s,x504=%s,x505=%s WHERE id=%s""", updates_f40)
            cursor.executemany("""UPDATE whmax.fishnet_10 SET r101=%s,r201=%s,r202=%s,r301=%s,r401=%s,r402=%s,r403=%s,r501=%s,r502=%s,r503=%s,r504=%s,r505=%s WHERE fishnet_id=%s""", updates_f10)
            conn.commit()

        get_time("所有计算和提交已全部完成")

    except psycopg2.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("数据库连接已关闭。")

if __name__ == "__main__":
    all_band()