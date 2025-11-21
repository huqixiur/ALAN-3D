import psycopg2
from psycopg2.extras import RealDictCursor

# --- 功能完全不变，性能提升巨大的优化版脚本 ---

try:
    # 1. 连接数据库
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="",  # 请填入您的密码
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    # 2. 设置搜索路径
    cursor.execute("SET search_path TO whmax;")

    # 3. (如果需要) 添加param_s字段，使用IF NOT EXISTS避免重复执行时报错
    print("正在向temp_combine表添加param_s字段 (如果不存在)...")
    cursor.execute("""
        ALTER TABLE temp_combine ADD COLUMN IF NOT EXISTS param_s FLOAT;
    """)

    # 4. 【核心优化】使用单一的、基于集合的UPDATE语句完成所有计算
    # 将原来Python中的所有循环和IF/ELSE逻辑，全部转换为SQL的CASE WHEN逻辑
    print("正在执行高性能的批量更新，这可能需要几秒到几分钟...")
    sql_update_query = """
    UPDATE temp_combine
    SET param_s =
        CASE
            -- 首先，根据 landuse_type 的值，动态选择正确的 area_xxx 字段作为分母。
            -- 如果分母大于0，则进行计算。这个条件同时处理了原代码中 area_i is not None 和 area_i != 0 的情况。
            WHEN (CASE landuse_type
                    WHEN '101' THEN area_101 WHEN '201' THEN area_201 WHEN '202' THEN area_202
                    WHEN '301' THEN area_301 WHEN '401' THEN area_401 WHEN '402' THEN area_402
                    WHEN '403' THEN area_403 WHEN '501' THEN area_501 WHEN '502' THEN area_502
                    WHEN '503' THEN area_503 WHEN '504' THEN area_504 WHEN '505' THEN area_505
                 END) > 0
            THEN
                -- 分母有效，开始计算 param_s。
                -- 这里再用一个CASE处理原代码中 param_s > 1 的情况。
                CASE
                    WHEN (overlap_area / (CASE landuse_type
                                            WHEN '101' THEN area_101 WHEN '201' THEN area_201 WHEN '202' THEN area_202
                                            WHEN '301' THEN area_301 WHEN '401' THEN area_401 WHEN '402' THEN area_402
                                            WHEN '403' THEN area_403 WHEN '501' THEN area_501 WHEN '502' THEN area_502
                                            WHEN '503' THEN area_503 WHEN '504' THEN area_504 WHEN '505' THEN area_505
                                         END)) > 1
                    THEN 0.001
                    ELSE (overlap_area / (CASE landuse_type
                                            WHEN '101' THEN area_101 WHEN '201' THEN area_201 WHEN '202' THEN area_202
                                            WHEN '301' THEN area_301 WHEN '401' THEN area_401 WHEN '402' THEN area_402
                                            WHEN '403' THEN area_403 WHEN '501' THEN area_501 WHEN '502' THEN area_502
                                            WHEN '503' THEN area_503 WHEN '504' THEN area_504 WHEN '505' THEN area_505
                                         END))
                END
            -- 如果分母为NULL或0，则param_s为0.0，对应原代码的 ELSE 分支。
            ELSE 0.0
        END
    WHERE
        -- 只对landuse_type不为9999的行进行计算，对应原代码的 if land_use_type != 9999
        landuse_type <> '9999';
    """
    cursor.execute(sql_update_query)
    
    # 5. 提交事务
    conn.commit()
    print("更新成功！性能优化完成。")

except Exception as e:
    print(f"发生错误: {e}")

finally:
    # 6. 关闭连接
    if 'conn' in locals() and conn is not None:
        cursor.close()
        conn.close()
        print("数据库连接已关闭。")