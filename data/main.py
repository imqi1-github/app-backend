from app import app
from app.extensions import db

with app.app_context():
    db.drop_all()
    db.create_all()

print("已重新生成数据表结构")

from app.models import User
from app.constants import UserRole, UserStatus
from app.extensions import db
from app import app
import faker

fake = faker.Faker("zh_CN")

count = 50
users = []

for index in range(count):
    username = fake.user_name()
    user = User(
        username=username,
        password=username,
        role=UserRole.User.value,
        state=UserStatus.Active.value,
    )
    users.append(user)
    print(f"准备添加第{index}名用户，用户名={user.username} 密码={user.password}")

users[0].role = UserRole.Admin.value
users[0].username = 'admin'
users[0].password = '123456'
users[1].role = UserRole.Admin.value
users[-1].state = UserStatus.Banned.value

with app.app_context():
    db.session.add_all(users)
    db.session.commit()

print(f"已添加{count}名用户")

from app.models import Information

from pathlib import Path
from shutil import copy

# 先移除所有文件

folder = Path("../uploads")
for item in folder.iterdir():
    if item.is_file():
        item.unlink()
    elif item.is_dir():
        item.rmdir()
print(f"已删除 {folder} 下的所有文件")

# 复制文件
folder = Path('./avatars/')

avatars = [f for f in folder.iterdir() if f.is_file()]

print(f"共{len(avatars)}张头像")

for avatar in avatars:
    copy(avatar, f'../uploads/{avatar.name}')

copy('./assets/imgs/avatar.png', '../uploads/avatar.png')
copy('./assets/imgs/wallpaper.png', '../uploads/wallpaper.png')

print(f"已复制头像")

nicknames = [
    "秦皇岛山海关发布",
    "秦皇岛北戴河官微",
    "秦皇岛野生动物园官方",
    "秦皇岛阿那亚旅游局",
    "秦皇岛老虎石海上公园",
    "秦皇岛鸽子窝官方",
    "秦皇岛奥林匹克公园",
    "秦皇岛南戴河官方号",
    "秦皇岛新澳海底世界",
    "秦皇岛祖山景区",
    "秦皇岛求仙入海处",
    "秦皇岛黄金海岸官号",
    "秦皇岛港口博物馆",
    "秦皇岛西港花园景区",
    "秦皇岛桃林口水库",
    "秦皇岛燕塞湖管理处",
    "秦皇岛怪楼奇园官方",
    "秦皇岛集发农业观光园",
    "秦皇岛山海文化公园",
    "秦皇岛滨海森林公园",
    "今天也想躺着",
    "海盐味的风",
    "月亮不营业",
    "桃子汽水",
    "晚风不等人",
    "小熊软糖不软",
    "一只会发光的猫",
    "日落之后",
    "奶茶味的日常",
    "想和你看海",
    "今夜星光灿烂",
    "豆乳拿铁少女",
    "凌晨三点的梦",
    "藏在云里的光",
    "甜味泡泡鱼",
    "焦糖味星球",
    "奶盖多多哒",
    "听说你很甜",
    "风住了星星",
    "宇宙小卖部",
    "夏天的柠檬汽",
    "温柔只给你",
    "爱吃小饼干",
    "猫系少女已上线",
    "在逃煎蛋卷",
    "翻滚的小章鱼",
    "打烊的奶茶店",
    "软绵绵的天气",
    "冬日限定热可可",
    "与你有关的风",
    "跑调的小曲奇",
    "追光的橘子",
    "甜到掉牙",
    "耳机里的温柔",
    "落日海岸线",
    "今日份可爱",
    "撒糖小天使",
    "凌晨的月亮",
    "猫窝日记本",
    "风吹少女裙",
    "奶油草莓派",
    "不想上班的咸鱼",
    "橘子汽泡水",
    "白日梦制造机",
    "温柔收容所",
    "躲进云朵里",
    "星河漫游指南",
    "斑斓泡泡",
    "镜子里的小怪兽",
    "随缘小辣椒",
    "野生柠檬茶",
    "风把耳朵吹红了",
    "冒泡的鲸鱼",
    "玫瑰味的宇宙",
    "鱼与西柚",
    "今天不营业",
    "月亮邮局",
    "沙滩捡壳人",
    "雨后起司蛋糕",
    "水蜜桃星球",
    "不加糖的可乐",
    "森林小偷",
    "今日开心了吗",
    "养猫少女",
    "我在云上写日记",
    "流浪星球旅客",
    "草莓味小夜灯",
    "梦里有猫",
    "清醒梦游者",
    "风中的菠萝包",
    "温柔的果冻",
    "可乐加点冰",
    "捡星星的人",
    "月亮派来的信使",
    "今天想你了",
    "云端甜品师",
    "住在森林的鲸",
    "穿裙子的夏天",
    "芒果气泡水",
    "想念变得很甜",
]

count = 50

print(f"共{len(nicknames)}个昵称")

provinces = ["河北省"] * int(count * 0.4)
provinces.extend(["河南省"] * (count - len(provinces)))

cities = ["秦皇岛市"] * int(count * 0.4)
cities.extend(["郑州市"] * (count - len(cities)))

informations = []

for index, (nickname, provinces, cities, avatar) in enumerate(zip(nicknames, provinces, cities, avatars)):
    information = Information(
        user_id=index + 1,
        nickname=nickname,
        position_province=provinces,
        position_city=cities,
        avatar_path=f"https://localhost:5000/download/{avatar.name}"
    )
    informations.append(information)

with app.app_context():
    db.session.add_all(informations)
    db.session.commit()

print("信息已添加")
import random
from datetime import time
from app.models import Spot
from app.extensions import db
from app import app
from pathlib import Path
from shutil import copy
import os

titles = [
    "老虎石海上公园",
    "山海关古城",
    "新澳海底世界",
    "碧螺塔酒吧公园",
    "野生动物园",
    "南戴河国际娱乐中心",
    "秦皇求仙入海处",
    "联峰山公园",
    "燕塞湖",
    "角山长城",
    "鸽子窝公园",
    "怪楼奇园",
    "仙螺岛景区",
    "老龙头",
    "哒哒岛旅游度假区",
    "半岛公园",
    "黄金海岸",
    "碣石山风景区",
    "奥林匹克大道公园",
    "秦皇岛森林公园",
]

image_folder = "./spot-imgs"
all_images = [
    f for f in os.listdir(image_folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))
]

spots = []

distinct_index = [0, 1, 2, 0, 2, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 2, 3, 3, 0, 2]
coordinates = [
    "119.488542,39.813902",
    "119.760042,40.01084",
    "119.562879,39.906134",
    "119.535365,39.82047",
    "119.521386,39.870255",
    "119.354625,39.735548",
    "119.622324,39.913949",
    "119.458809,39.824137",
    "119.704406,40.043875",
    "119.738222,40.039337",
    "119.526688,39.836216",
    "119.498241,39.827084",
    "119.431375,39.793113",
    "119.797255,39.968241",
    "119.399937,39.786491",
    "119.515209,39.899569",
    "119.341343,39.701754",
    "119.145666,39.756307",
    "119.514722,39.827887",
    "119.538652,39.934709",
]

image_folder = "./images2"
image_url_prefix = "https://localhost:5000/download/"
content = """**{title}**位于{position}，是一个集自然景观与人文历史于一体的旅游景点。

## 主要特色

- 地处优越，风光旖旎，气候宜人
- 是观赏自然景观的绝佳地点
- 拥有丰富的生态资源
- 每年吸引大量游客，是休闲好去处

## 交通信息

> 地址：{position}知名景点附近
> 可乘坐多路公交车直达

---

欢迎前往**{title}**，感受自然与文化的魅力！
"""

areas = ["北戴河区", "山海关区", "海港区", "昌黎县"]

for index in range(len(titles)):
    title = titles[index]
    selected_images = random.sample(all_images, k=random.randint(4, 8))
    picture_urls = ",".join(image_url_prefix + img for img in selected_images)
    full_address = "河北省秦皇岛市" + title
    position = f"河北省秦皇岛市{areas[distinct_index[index]]}"

    spot = Spot(
        title=title,
        good=50 + index * 3,
        bad=5 + index % 4,
        start_time=time(8, 0),
        end_time=time(21, 0),
        position=position,
        coordinates=coordinates[index],
        content=content.format(title=title, position=position),
        pictures=picture_urls,
        province="河北省",
        city="秦皇岛市",
        place=areas[distinct_index[index]],
        views=100 + index * 10,
    )
    spots.append(spot)

with app.app_context():
    db.session.add_all(spots)
    db.session.commit()

print(f"已添加{len(spots)}个景点")

# 复制文件
folder = Path('./spot-imgs/')

imgs = [f for f in folder.iterdir() if f.is_file()]

print(f"共{len(imgs)}张照片")

for img in imgs:
    copy(img, f'../uploads/{img.name}')

print(f"已复制{len(imgs)}张照片")

import random
import time

import pandas as pd

from app.extensions import db
from app.models import Post, Comment, Category, Relationship

print("正在从 CSV 文件加载数据...")
categories_df = pd.read_csv("./post/categories.csv")
posts_df = pd.read_csv("./post/posts.csv")
comments_df = pd.read_csv("./post/comments.csv")
relationships_df = pd.read_csv("./post/relationships.csv")

print("正在调整帖子和评论中的 user_id，确保在 1 到 50 范围内...")
# 将 user_id 映射到 1 到 50 的范围：user_id = (user_id - 1) % 50 + 1
posts_df["user_id"] = posts_df["user_id"].apply(lambda x: (x - 1) % 50 + 1)
comments_df["user_id"] = comments_df["user_id"].apply(lambda x: (x - 1) % 50 + 1)

with app.app_context():
    print("正在将分类数据保存到数据库...")
    try:
        # 获取已存在的分类 ID
        existing_category_ids = set(category.id for category in Category.query.all())
        categories_to_insert = []

        for _, row in categories_df.iterrows():
            category_id = row["id"]
            if category_id in existing_category_ids:
                print(f"分类 ID {category_id} 已存在，跳过插入...")
                continue

            category = Category(
                id=category_id,
                name=row["name"],
                description=row["description"],
            )
            categories_to_insert.append(category)
            print(f"已准备分类 {category_id}：{row['name']}")

        if categories_to_insert:
            db.session.bulk_save_objects(categories_to_insert)
            db.session.commit()
            print(f"成功插入 {len(categories_to_insert)} 个新分类。")
        else:
            print("无需插入新分类，所有分类已存在。")
    except Exception as e:
        db.session.rollback()
        print(f"插入分类时出错：{e}")

    print("正在将帖子数据保存到数据库...")
    try:
        # 获取已存在的帖子 ID
        existing_post_ids = set(post.id for post in Post.query.all())
        posts_to_insert = []

        for _, row in posts_df.iterrows():
            post_id = row["id"]
            if post_id in existing_post_ids:
                print(f"帖子 ID {post_id} 已存在，跳过插入...")
                continue

            post = Post(
                id=post_id,
                user_id=row["user_id"],
                title=row["title"],
                content=row["content"],
                create_time=time.time() - random.randint(0, 24 * 60 * 60 * 30),
                update_time=time.time() - random.randint(0, 24 * 60 * 60 * 30),
                # comment_count=0,  # 初始为 0，后面更新
            )
            posts_to_insert.append(post)
            print(f"已准备帖子 {post_id}：{row['title']}")

        if posts_to_insert:
            db.session.bulk_save_objects(posts_to_insert)
            db.session.commit()
            print(f"成功插入 {len(posts_to_insert)} 个新帖子。")
        else:
            print("无需插入新帖子，所有帖子已存在。")
    except Exception as e:
        db.session.rollback()
        print(f"插入帖子时出错：{e}")

    print("正在将关系数据保存到数据库...")
    try:
        # 获取已存在的关系 ID
        existing_relationship_ids = set(
            relationship.id for relationship in Relationship.query.all()
        )
        relationships_to_insert = []

        for _, row in relationships_df.iterrows():
            relationship_id = row["id"]
            if relationship_id in existing_relationship_ids:
                print(f"关系 ID {relationship_id} 已存在，跳过插入...")
                continue

            relationship = Relationship(
                id=relationship_id,
                category_id=row["category_id"],
                post_id=row["post_id"],
            )
            relationships_to_insert.append(relationship)
            print(
                f"已准备关系 {relationship_id}：分类 {row['category_id']} - 帖子 {row['post_id']}"
            )

        if relationships_to_insert:
            db.session.bulk_save_objects(relationships_to_insert)
            db.session.commit()
            print(f"成功插入 {len(relationships_to_insert)} 个新关系。")
        else:
            print("无需插入新关系，所有关系已存在。")
    except Exception as e:
        db.session.rollback()
        print(f"插入关系时出错：{e}")

    try:
        # 获取已存在的评论 ID
        existing_comment_ids = set(comment.id for comment in Comment.query.all())
        comments_to_insert = []

        for _, row in comments_df.iterrows():
            comment_id = row["id"]
            if comment_id in existing_comment_ids:
                print(f"评论 ID {comment_id} 已存在，跳过插入...")
                continue

            comment = Comment(
                id=comment_id,
                user_id=row["user_id"],
                post_id=row["post_id"],
                parent_id=row["parent_id"] if pd.notna(row["parent_id"]) else None,
                content=row["content"],
                create_time=time.time() - random.randint(0, 24 * 60 * 60 * 30),
            )
            comments_to_insert.append(comment)
            print(f"已准备评论 {comment_id}：帖子 {row['post_id']}")

        if comments_to_insert:
            db.session.bulk_save_objects(comments_to_insert)
            db.session.commit()
            print(f"成功插入 {len(comments_to_insert)} 条新评论。")
        else:
            print("无需插入新评论，所有评论已存在。")
    except Exception as e:
        db.session.rollback()
        print(f"插入评论时出错：{e}")

    print("正在更新帖子的评论数量...")
    try:
        for post_id in posts_df["id"]:
            # 使用 db.session.get() 替代 Post.query.get()
            post = db.session.get(Post, post_id)
            if post:
                comment_count = Comment.query.filter_by(post_id=post_id).count()
                post.comment_count = comment_count
        db.session.commit()
        print("评论数量更新完成。")
    except Exception as e:
        db.session.rollback()
        print(f"更新评论数量时出错：{e}")

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
    current_dir = Path('.').parent
    images_dir = current_dir / "post-imgs"

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
    current_dir = Path('.').parent
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
    current_dir = Path('.').parent
    images_dir = current_dir / "post-imgs"
    uploads_dir = current_dir / ".." / "uploads"

    # 确保 uploads 文件夹存在
    uploads_dir.mkdir(parents=True, exist_ok=True)

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

import random

from app.extensions import db
from app.models import User, Subscribe

def insert_random_subscriptions():
    print("正在插入随机订阅数据（两两组合，0.05 概率）...")
    try:
        # 获取所有用户
        existing_users = User.query.all()
        user_count = len(existing_users)
        print(f"当前用户总数: {user_count}")

        if user_count < 50:
            print(f"错误：用户数 {user_count} 小于 50，无法生成完整订阅数据")
            return
        elif user_count > 50:
            print(f"警告：用户数 {user_count} 多于 50，将使用所有用户生成订阅数据")

        # 清空现有的 Subscribe 表（可选）
        db.session.query(Subscribe).delete()
        db.session.commit()
        print("已清空 Subscribe 表")

        # 生成订阅关系
        subscriptions_to_insert = []
        for i in range(user_count):
            for j in range(user_count):
                if i != j:  # 避免自己关注自己
                    user1 = existing_users[i]
                    user2 = existing_users[j]
                    # 以 0.05 概率生成订阅关系
                    if random.random() < 0.05:
                        subscription = Subscribe(
                            user_id=user1.id,
                            subscribed_user_id=user2.id
                        )
                        subscriptions_to_insert.append(subscription)
                        print(f"已准备订阅关系: 用户 {user1.id} -> 用户 {user2.id}")

        # 插入订阅数据
        if subscriptions_to_insert:
            db.session.bulk_save_objects(subscriptions_to_insert)
            db.session.commit()
            print(f"成功插入 {len(subscriptions_to_insert)} 条订阅记录")
        else:
            print("未生成任何订阅关系（可能是概率太低或用户数不足）")

        # 验证插入结果
        sample_subscriptions = db.session.query(Subscribe).limit(5).all()
        print(f"Subscribe 表示例数据: {[s.json for s in sample_subscriptions]}")

    except Exception as e:
        db.session.rollback()
        print(f"插入订阅数据时出错：{type(e).__name__} - {str(e)}")
        return False

    return True

# 主函数
def main():
    # 确保表结构已创建
    try:
        db.create_all()
    except Exception as e:
        print(f"创建表结构时出错：{e}")
        return

    # 执行插入订阅数据
    if not insert_random_subscriptions():
        print("订阅数据插入失败")
        return

    print("订阅数据插入完成！")

from app import app

with app.app_context():
    main()
