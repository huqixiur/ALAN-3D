# 计算两点矢量方向方位角
import math

# 给定的值
dpi = 0.017453292519943295
latA, lonA = 1.2850728946834302, 103.84389992164976
latB, lonB = 1.2852567119628688, 103.84403704021372

# 计算xx和yy
yy = math.sin((lonA - lonB) * dpi) * math.cos(math.radians(latA))
xx = math.cos(math.radians(latB)) * math.sin(math.radians(latA)) - math.sin(math.radians(latB)) * math.cos(math.radians(latA)) * math.cos((lonA - lonB) * dpi)

# 计算yaw_AB
yaw_AB = math.atan2(yy, xx) / dpi

# 打印结果并加上180度,即从A出发到B的矢量的方位
print(yaw_AB + 180)