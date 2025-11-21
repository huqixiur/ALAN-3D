import psycopg2
from datetime import datetime

def get_time(status:str):
    """一个简单的时间打印函数，用于追踪脚本进度"""
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{status} {formatted_time}")

def create_redis_idx_final_optimized():
    """
    最终优化版函数：采用“分而治之”策略，将复杂查询分解为带索引的临时表，
    以解决超长查询时间和潜在的数据库锁问题。
    功能与原版Python脚本完全等价。
    """
    get_time("开始 (最终分而治之策略)：")
    conn = None  # 初始化conn变量
    try:
        # 1. 建立数据库连接
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="",  # ********** 请在这里填入您的数据库密码 **********
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # 2. 设置模式（Schema）
        cursor.execute("SET search_path TO whmax;")

        # 步骤1: 将第一个CTE物化为带索引的临时表
        get_time("步骤1: 创建并索引LandUseGroupStats临时表...")
        cursor.execute("DROP TABLE IF EXISTS temp_landuse_stats;")
        cursor.execute("""
            CREATE TEMP TABLE temp_landuse_stats AS
            SELECT
                fishnet_id,
                landuse_type,
                SUM(param_h) AS total_param_h,
                SUM(param_s) AS total_param_s,
                MAX(param_s) AS max_param_s
            FROM temp_combine
            GROUP BY fishnet_id, landuse_type;
        """)
        cursor.execute("CREATE INDEX idx_temp_landuse_stats ON temp_landuse_stats (fishnet_id, landuse_type);")
        cursor.execute("ANALYZE temp_landuse_stats;")
        get_time("步骤1完成.")

        # 步骤2: 将第二个CTE物化为带索引的临时表
        get_time("步骤2: 创建并索引FishnetFlags临时表...")
        cursor.execute("DROP TABLE IF EXISTS temp_fishnet_flags;")
        cursor.execute("""
            CREATE TEMP TABLE temp_fishnet_flags AS
            SELECT DISTINCT fishnet_id
            FROM temp_combine
            WHERE landuse_type = 9999;
        """)
        cursor.execute("CREATE INDEX idx_temp_fishnet_flags ON temp_fishnet_flags (fishnet_id);")
        cursor.execute("ANALYZE temp_fishnet_flags;")
        get_time("步骤2完成.")
        
        # 步骤3: 执行一个更简单的最终查询并插入数据
        get_time("步骤3: 执行简化的最终查询并插入...")
        cursor.execute("DROP TABLE IF EXISTS temp_redis;")
        cursor.execute("""
            CREATE TABLE temp_redis (
                fishnet_id INTEGER,
                land_use_type TEXT,
                gid INTEGER,
                redis_idx REAL
            );
        """)
        
        # 这个查询连接的是已经计算好、带索引的临时表，速度会快非常多
        sql_insert_query = """
        INSERT INTO temp_redis (fishnet_id, land_use_type, gid, redis_idx)
        SELECT DISTINCT
            n.fishnet_id, n.land_use_type, n.gid,
            -- CASE WHEN 逻辑完全复刻原Python代码的 if/else 分支
            CASE
                WHEN n.gid != 0 THEN tc.param_s * (tc.param_h / (s.total_param_h + 1))
                WHEN n.gid = 0 THEN
                    (CASE WHEN (1 - s.total_param_s) < 0 THEN (1 - s.max_param_s) ELSE (1 - s.total_param_s) END) *
                    (1 / (s.total_param_h + 1))
            END AS redis_idx
        FROM new_pts AS n
        LEFT JOIN temp_combine AS tc ON n.fishnet_id = tc.fishnet_id AND n.land_use_type = tc.landuse_type::TEXT AND n.gid = tc.gid
        JOIN temp_landuse_stats AS s ON n.fishnet_id = s.fishnet_id AND n.land_use_type = s.landuse_type::TEXT
        LEFT JOIN temp_fishnet_flags AS f ON n.fishnet_id = f.fishnet_id
        WHERE n.land_use_type <> '401' AND f.fishnet_id IS NULL AND n.land_use_type IS NOT NULL;
        """
        cursor.execute(sql_insert_query)
        conn.commit() # 在大操作后立刻提交，以尽快释放可能存在的锁
        get_time("步骤3完成.")
        
        # 步骤4: 添加并更新 total_redis 列
        get_time("步骤4: 更新total_redis...")
        cursor.execute("ALTER TABLE temp_redis ADD COLUMN total_redis REAL;")
        # 使用更高性能的 UPDATE ... FROM 语法
        cursor.execute("""
            UPDATE temp_redis
            SET total_redis = sub.total
            FROM (
                SELECT fishnet_id, land_use_type, SUM(redis_idx) as total
                FROM temp_redis
                GROUP BY fishnet_id, land_use_type
            ) AS sub
            WHERE temp_redis.fishnet_id = sub.fishnet_id AND temp_redis.land_use_type = sub.land_use_type;
        """)
        
        conn.commit()
        get_time("事务提交完成, 任务成功！")

    except Exception as e:
        print(f"发生错误: {e}")
        if conn:
            conn.rollback() # 如果发生错误，回滚事务
    finally:
        # 确保数据库连接在任何情况下都会被关闭
        if conn:
            cursor.close()
            conn.close()
            get_time("数据库连接已关闭.")

# 执行最终优化版的函数
create_redis_idx_final_optimized()