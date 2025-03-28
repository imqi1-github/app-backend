import random
import string
from pathlib import Path

# 定义图片文件的常见扩展名
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}


def generate_random_string(length=8):
    """生成指定长度的随机字符串（字母和数字）"""
    characters = string.ascii_letters + string.digits  # 包含 a-z, A-Z, 0-9
    return "".join(random.choice(characters) for _ in range(length))


def rename_images_in_folder():
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    images_dir = current_dir / "images"

    # 检查 images 文件夹是否存在
    if not images_dir.exists() or not images_dir.is_dir():
        print("错误：images 文件夹不存在！")
        return

    # 用于存储已使用的新文件名（避免冲突）
    used_names = set()

    # 遍历 images 文件夹中的所有文件
    for file_path in images_dir.iterdir():
        # 只处理文件（排除子文件夹）
        if not file_path.is_file():
            continue

        # 获取文件扩展名（小写）
        extension = file_path.suffix.lower()

        # 检查是否为图片文件
        if extension not in IMAGE_EXTENSIONS:
            print(f"跳过非图片文件：{file_path.name}")
            continue

        # 生成新的随机文件名（确保不重复）
        while True:
            new_name = generate_random_string(8)
            if new_name not in used_names:
                used_names.add(new_name)
                break

        # 构造新文件名（随机字符串 + 原扩展名）
        new_file_name = f"{new_name}{extension}"
        new_file_path = images_dir / new_file_name

        # 重命名文件
        try:
            file_path.rename(new_file_path)
            print(f"已重命名：{file_path.name} -> {new_file_name}")
        except Exception as e:
            print(f"重命名失败：{file_path.name} -> {new_file_name}，错误：{e}")


def main():
    print("开始重命名 images 文件夹中的图片...")
    rename_images_in_folder()
    print("重命名完成！")


if __name__ == "__main__":
    main()
