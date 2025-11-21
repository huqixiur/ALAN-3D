import cv2
from fisheyewarping import FisheyeWarping

# 读取鱼眼图像
fisheye_img = cv2.imread("./test_fisheye.jpg")

# 创建FisheyeWarping对象
frd = FisheyeWarping(fisheye_img, use_multiprocessing=False)

# 构建去畸变网格并保存
frd.build_dewarp_mesh(save_path='./dewarp-mesh.pkl')

# 执行去畸变处理，并将结果保存
frd.run_dewarp(save_path='./dewarp-output.png')