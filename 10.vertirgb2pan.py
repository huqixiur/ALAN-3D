import os
from PIL import Image

def convert_images_to_grayscale():
    """
    读取指定文件夹中的所有PNG图片，将其转换为灰度图，
    并按数字顺序重命名后保存到新的 'PhotoPan' 文件夹中。
    """
    # --- 请在这里修改您的图片输入文件夹路径 ---
    # 示例:
    # input_folder = 'C:/Users/YourName/Desktop/MyPhotos'  (Windows)
    # input_folder = '/Users/YourName/Documents/MyPhotos' (Mac/Linux)
    input_folder = "E:\科研\paper\V4\ALANPhotos"

    # 定义输出文件夹的名称
    output_folder = "E:\科研\paper\V4\PhotoPan"

    # 检查输入文件夹是否存在
    if not os.path.isdir(input_folder):
        print(f"错误：输入文件夹 '{input_folder}' 不存在。请检查路径是否正确。")
        return

    # 创建输出文件夹（如果它不存在的话）
    os.makedirs(output_folder, exist_ok=True)
    print(f"输出文件夹 '{output_folder}' 已准备就绪。")

    # 获取输入文件夹中所有的png文件
    try:
        # 使用列表推导式筛选出所有以.png结尾的文件（不区分大小写）
        image_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
        if not image_files:
            print(f"警告：在文件夹 '{input_folder}' 中没有找到任何 .png 文件。")
            return
    except Exception as e:
        print(f"读取文件夹时发生错误: {e}")
        return
        
    print(f"找到了 {len(image_files)} 个PNG文件。开始转换...")

    # 初始化图片序号
    image_counter = 1

    # 遍历所有找到的图片文件
    for filename in image_files:
        try:
            # 构建完整的输入文件路径
            input_path = os.path.join(input_folder, filename)

            # 打开图片
            with Image.open(input_path) as img:
                # 转换图片为灰度图 ('L'模式代表Luminance)
                # 这使用了标准的 ITU-R 601-2 luma 转换: L = R * 0.299 + G * 0.587 + B * 0.114
                grayscale_img = img.convert('L')

                # 构建新的文件名和输出路径
                new_filename = f"{image_counter}.png"
                output_path = os.path.join(output_folder, new_filename)

                # 保存转换后的图片
                grayscale_img.save(output_path, 'PNG')

                print(f"处理成功: '{filename}' -> '{new_filename}'")

                # 更新图片序号
                image_counter += 1
        
        except Exception as e:
            print(f"处理失败: '{filename}'。错误信息: {e}")

    print("\n所有图片处理完成！")
    print(f"共 {image_counter - 1} 张图片已成功转换并保存到 '{output_folder}' 文件夹中。")

# --- 运行主函数 ---
if __name__ == '__main__':
    convert_images_to_grayscale()