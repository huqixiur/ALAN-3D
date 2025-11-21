def calculate_rectangle_centroid(rect):
    # 解析矩形的坐标
    x1, y1, x2, y2 = rect
    
    # 计算中心坐标
    centroid_x = (x1 + x2) / 2
    centroid_y = (y1 + y2) / 2
    
    return (centroid_x, centroid_y)

# 商业区矩形坐标
commercial_rect = (29026.701700000092, 29778.65240000002, 29426.701700000092, 29378.65249999985)

# 住宅区矩形坐标
# residential_rect = (24946.701700000092, 33618.65240000002, 25346.701700000092, 33218.65249999985)
residential_rect = (12400.3640999999, 35927.7923000008, 12800.3640999999, 36327.7923000008)
# 学校矩形坐标
school_rect = (21066.701700000092, 31454.65829999931, 21466.701700000092, 31054.65839999914)

# 工业区矩形坐标
industrial_rect = (6866.701700000092, 34552.479699999094, 7266.701700000092, 34152.47980000079)

# 计算中心坐标
commercial_centroid = calculate_rectangle_centroid(commercial_rect)
residential_centroid = calculate_rectangle_centroid(residential_rect)
school_centroid = calculate_rectangle_centroid(school_rect)
industrial_centroid = calculate_rectangle_centroid(industrial_rect)

print("商业区中心坐标:", commercial_centroid)
print("住宅区中心坐标:", residential_centroid)
print("学校中心坐标:", school_centroid)
print("工业区中心坐标:", industrial_centroid)