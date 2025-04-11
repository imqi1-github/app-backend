import random
import shutil
import string
from pathlib import Path

from flask import current_app

from app.config import backend_url
from app.extensions import db
from app.models import Post, Attachment

# 定义图片文件的常见扩展名及其对应的 MIME 类型
IMAGE_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".webp": "image/webp",
}

def generate_random_string(length=8):
    """生成指定长度的随机字符串（字母和数字）"""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

def rename_and_collect_images():
    """遍历 images 文件夹，重命名图片，并返回图片信息"""
    current_dir = Path(__file__).parent
    images_dir = current_dir / "images"

    if not images_dir.exists() or not images_dir.is_dir():
        print("错误：images 文件夹不存在！")
        return []

    image_info_list = []
    used_names = set()

    for file_path in images_dir.iterdir():
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()
        if extension not in IMAGE_EXTENSIONS:
            print(f"跳过非图片文件：{file_path.name}")
            continue

        while True:
            new_name = generate_random_string(8)
            if new_name not in used_names:
                used_names.add(new_name)
                break

        new_file_name = f"{new_name}{extension}"
        new_file_path = images_dir / new_file_name

        try:
            file_path.rename(new_file_path)
            print(f"已重命名：{file_path.name} -> {new_file_name}")
            image_info_list.append(
                {
                    "file_name": new_file_name,
                    "extension": extension,
                    "file_type": IMAGE_EXTENSIONS[extension],
                }
            )
        except Exception as e:
            print(f"重命名失败：{file_path.name} -> {new_file_name}，错误：{e}")

    return image_info_list

def clear_uploads_except_special():
    """清理 uploads 文件夹，保留以 avatar 和 wallpaper 开头的文件"""
    current_dir = Path(__file__).parent
    uploads_dir = current_dir / ".." / "uploads"

    # 如果 uploads 文件夹不存在，直接返回
    if not uploads_dir.exists() or not uploads_dir.is_dir():
        print("uploads 文件夹不存在，无需清理")
        return

    # 遍历 uploads 文件夹中的所有文件
    for file_path in uploads_dir.iterdir():
        if not file_path.is_file():
            continue

        file_name = file_path.name
        # 保留以 "avatar" 或 "wallpaper" 开头的文件
        if file_name.startswith("avatar") or file_name.startswith("wallpaper"):
            continue

        # 删除其他文件
        try:
            file_path.unlink()
            print(f"已删除：{file_name}")
        except Exception as e:
            print(f"删除失败：{file_name}，错误：{e}")

def copy_images_to_uploads():
    """将 images 文件夹中的图片复制到 ../uploads 文件夹"""
    current_dir = Path(__file__).parent
    images_dir = current_dir / "images"
    uploads_dir = current_dir / ".." / "uploads"

    # 确保 uploads 文件夹存在
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # 先清理 uploads 文件夹，保留特定文件
    clear_uploads_except_special()

    # 遍历 images 文件夹中的所有文件
    for file_path in images_dir.iterdir():
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()
        if extension not in IMAGE_EXTENSIONS:
            continue

        target_path = uploads_dir / file_path.name

        try:
            shutil.copy2(file_path, target_path)
            print(f"已复制：{file_path.name} -> {target_path}")
        except Exception as e:
            print(f"复制失败：{file_path.name} -> {target_path}，错误：{e}")

def add_attachments_to_posts():
    """为每个 Post 添加 3~7 个 Attachment"""
    image_info_list = rename_and_collect_images()
    if not image_info_list:
        print("没有可用的图片，无法添加 Attachment！")
        return

    copy_images_to_uploads()

    posts = Post.query.all()
    if not posts:
        print("没有找到任何 Post，无法添加 Attachment！")
        return

    for post in posts:
        num_attachments = random.randint(1, 6)
        selected_images = random.sample(
            image_info_list, k=min(num_attachments, len(image_info_list))
        )

        while len(selected_images) < num_attachments:
            selected_images.append(random.choice(image_info_list))

        for image_info in selected_images:
            file_name = image_info["file_name"]
            file_type = image_info["file_type"]
            file_path = f"{backend_url}/download/{file_name}"

            attachment = Attachment(
                post_id=post.id,
                file_name=file_name,
                file_path=file_path,
                file_type=file_type,
            )
            db.session.add(attachment)
            print(f"已为 Post {post.id} 添加 Attachment：{file_name}")

    try:
        db.session.commit()
        print("所有 Attachment 已成功添加到数据库！")
    except Exception as e:
        db.session.rollback()
        print(f"添加 Attachment 失败：{e}")

def main():
    print("开始为 Post 添加 Attachment...")
    with current_app.app_context():
        add_attachments_to_posts()
    print("操作完成！")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        main()