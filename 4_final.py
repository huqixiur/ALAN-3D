import psycopg2
from datetime import datetime

def get_time(status: str):
    """一个简单的时间打印函数，用于追踪脚本进度"""
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{status} {formatted_time}")

def calculate_all_bands_definitive_fix():
    """
    最终定义版（重构）：使用嵌套CTE分离计算与转换逻辑，确保所有分支都被完美保护。
    """
    get_time("开始 (最终定义版-重构-下溢终极修复)：")
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="",  # ********** 请在此填写您的数据库密码 **********
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        cursor.execute("SET search_path TO whmax;")

        # 预计算步骤保持不变
        get_time("步骤A.1: 创建并索引PointCounts临时表...")
        cursor.execute("DROP TABLE IF EXISTS temp_point_counts;")
        cursor.execute("""
            CREATE TEMP TABLE temp_point_counts AS
            SELECT fishnet_id, gid, land_use_type, COUNT(*) as n_pts
            FROM new_pts
            GROUP BY fishnet_id, gid, land_use_type;
        """)
        cursor.execute("CREATE INDEX idx_temp_point_counts ON temp_point_counts (fishnet_id, gid, land_use_type);")
        cursor.execute("ANALYZE temp_point_counts;")

        get_time("步骤A.2: 创建并索引FishnetFlags临时表...")
        cursor.execute("DROP TABLE IF EXISTS temp_fishnet_flags;")
        cursor.execute("""
            CREATE TEMP TABLE temp_fishnet_flags AS
            SELECT DISTINCT fishnet_id FROM temp_combine WHERE landuse_type = 9999;
        """)
        cursor.execute("CREATE INDEX idx_temp_fishnet_flags ON temp_fishnet_flags (fishnet_id);")
        cursor.execute("ANALYZE temp_fishnet_flags;")
        get_time("预计算步骤完成.")

        get_time("步骤B: 执行最终的合并更新...")

        # ✅ 终极定义版SQL (重构): 使用两层CTE，先计算NUMERIC，再安全转换
        sql_final_update = """
        WITH NumericResults AS (
            -- 步骤1: 仅用NUMERIC类型计算出高精度原始值，不做任何转换
            SELECT DISTINCT
                n.fishnet_id, 
                n.gid, 
                n.land_use_type,
                -- 为rad_1计算高精度NUMERIC值
                (CASE
                    WHEN n.land_use_type = '401' OR f.fishnet_id IS NOT NULL THEN
                        CASE WHEN pc.n_pts > 0 THEN (CASE n.land_use_type WHEN '101' THEN f10.r101 WHEN '201' THEN f10.r201 WHEN '202' THEN f10.r202 WHEN '301' THEN f10.r301 WHEN '401' THEN f10.r401 WHEN '402' THEN f10.r402 WHEN '403' THEN f10.r403 WHEN '501' THEN f10.r501 WHEN '502' THEN f10.r502 WHEN '503' THEN f10.r503 WHEN '504' THEN f10.r504 WHEN '505' THEN f10.r505 END)[1]::NUMERIC / pc.n_pts::NUMERIC ELSE 0::NUMERIC END
                    ELSE
                        CASE WHEN tr.redis_idx > 0 AND tr.total_redis > 0 AND pc.n_pts > 0 THEN ((CASE n.land_use_type WHEN '101' THEN f10.r101 WHEN '201' THEN f10.r201 WHEN '202' THEN f10.r202 WHEN '301' THEN f10.r301 WHEN '401' THEN f10.r401 WHEN '402' THEN f10.r402 WHEN '403' THEN f10.r403 WHEN '501' THEN f10.r501 WHEN '502' THEN f10.r502 WHEN '503' THEN f10.r503 WHEN '504' THEN f10.r504 WHEN '505' THEN f10.r505 END)[1]::NUMERIC * tr.redis_idx::NUMERIC) / (tr.total_redis::NUMERIC * pc.n_pts::NUMERIC) ELSE 0::NUMERIC END
                END) AS numeric_rad_1,
                -- 为rad_2计算高精度NUMERIC值
                (CASE
                    WHEN n.land_use_type = '401' OR f.fishnet_id IS NOT NULL THEN
                        CASE WHEN pc.n_pts > 0 THEN (CASE n.land_use_type WHEN '101' THEN f10.r101 WHEN '201' THEN f10.r201 WHEN '202' THEN f10.r202 WHEN '301' THEN f10.r301 WHEN '401' THEN f10.r401 WHEN '402' THEN f10.r402 WHEN '403' THEN f10.r403 WHEN '501' THEN f10.r501 WHEN '502' THEN f10.r502 WHEN '503' THEN f10.r503 WHEN '504' THEN f10.r504 WHEN '505' THEN f10.r505 END)[2]::NUMERIC / pc.n_pts::NUMERIC ELSE 0::NUMERIC END
                    ELSE
                        CASE WHEN tr.redis_idx > 0 AND tr.total_redis > 0 AND pc.n_pts > 0 THEN ((CASE n.land_use_type WHEN '101' THEN f10.r101 WHEN '201' THEN f10.r201 WHEN '202' THEN f10.r202 WHEN '301' THEN f10.r301 WHEN '401' THEN f10.r401 WHEN '402' THEN f10.r402 WHEN '403' THEN f10.r403 WHEN '501' THEN f10.r501 WHEN '502' THEN f10.r502 WHEN '503' THEN f10.r503 WHEN '504' THEN f10.r504 WHEN '505' THEN f10.r505 END)[2]::NUMERIC * tr.redis_idx::NUMERIC) / (tr.total_redis::NUMERIC * pc.n_pts::NUMERIC) ELSE 0::NUMERIC END
                END) AS numeric_rad_2,
                -- 为rad_3计算高精度NUMERIC值
                (CASE
                    WHEN n.land_use_type = '401' OR f.fishnet_id IS NOT NULL THEN
                        CASE WHEN pc.n_pts > 0 THEN (CASE n.land_use_type WHEN '101' THEN f10.r101 WHEN '201' THEN f10.r201 WHEN '202' THEN f10.r202 WHEN '301' THEN f10.r301 WHEN '401' THEN f10.r401 WHEN '402' THEN f10.r402 WHEN '403' THEN f10.r403 WHEN '501' THEN f10.r501 WHEN '502' THEN f10.r502 WHEN '503' THEN f10.r503 WHEN '504' THEN f10.r504 WHEN '505' THEN f10.r505 END)[3]::NUMERIC / pc.n_pts::NUMERIC ELSE 0::NUMERIC END
                    ELSE
                        CASE WHEN tr.redis_idx > 0 AND tr.total_redis > 0 AND pc.n_pts > 0 THEN ((CASE n.land_use_type WHEN '101' THEN f10.r101 WHEN '201' THEN f10.r201 WHEN '202' THEN f10.r202 WHEN '301' THEN f10.r301 WHEN '401' THEN f10.r401 WHEN '402' THEN f10.r402 WHEN '403' THEN f10.r403 WHEN '501' THEN f10.r501 WHEN '502' THEN f10.r502 WHEN '503' THEN f10.r503 WHEN '504' THEN f10.r504 WHEN '505' THEN f10.r505 END)[3]::NUMERIC * tr.redis_idx::NUMERIC) / (tr.total_redis::NUMERIC * pc.n_pts::NUMERIC) ELSE 0::NUMERIC END
                END) AS numeric_rad_3
            FROM new_pts n
            LEFT JOIN temp_point_counts pc ON n.fishnet_id = pc.fishnet_id AND n.gid = pc.gid AND n.land_use_type = pc.land_use_type
            LEFT JOIN temp_fishnet_flags f ON n.fishnet_id = f.fishnet_id
            LEFT JOIN temp_redis tr ON n.fishnet_id = tr.fishnet_id AND n.land_use_type = tr.land_use_type AND n.gid = tr.gid
            LEFT JOIN fishnet_10 f10 ON n.fishnet_id = f10.fishnet_id
            WHERE n.list_type IS NOT NULL AND n.land_use_type IS NOT NULL
        ),
        CalculatedValues AS (
            -- 步骤2: 基于上一步的高精度结果，进行统一、安全的检查和转换
            SELECT
                fishnet_id, gid, land_use_type,
                -- 统一的保护逻辑
                CASE WHEN numeric_rad_1 > 0 AND numeric_rad_1 < 1e-300::NUMERIC THEN 0.0 ELSE numeric_rad_1::DOUBLE PRECISION END AS final_rad_1,
                CASE WHEN numeric_rad_2 > 0 AND numeric_rad_2 < 1e-300::NUMERIC THEN 0.0 ELSE numeric_rad_2::DOUBLE PRECISION END AS final_rad_2,
                CASE WHEN numeric_rad_3 > 0 AND numeric_rad_3 < 1e-300::NUMERIC THEN 0.0 ELSE numeric_rad_3::DOUBLE PRECISION END AS final_rad_3
            FROM NumericResults
        )
        -- 步骤3: 执行最终的更新
        UPDATE new_pts
        SET
            pts_rad_1 = COALESCE(cv.final_rad_1, 0.0),
            pts_rad_2 = COALESCE(cv.final_rad_2, 0.0),
            pts_rad_3 = COALESCE(cv.final_rad_3, 0.0)
        FROM CalculatedValues cv
        WHERE new_pts.fishnet_id = cv.fishnet_id
          AND new_pts.gid = cv.gid
          AND new_pts.land_use_type = cv.land_use_type;
        """

        cursor.execute(sql_final_update)
        conn.commit()
        get_time("所有波段计算与更新完毕！任务成功！")

    except Exception as e:
        print(f"发生错误: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()
            get_time("数据库连接已关闭.")

# 执行函数
calculate_all_bands_definitive_fix()