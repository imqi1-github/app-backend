import pandas as pd
from app.extensions import db
from app.models import Post, Comment, Category, Relationship, User, UserInformation
from faker import Faker

from constants import UserRole

# 初始化 Faker，设置为中文
fake = Faker("zh_CN")


# 插入 50 位用户，id 从 1 到 50，如果 id 已存在则跳过
def insert_random_users():
    print("正在插入随机用户（ID 从 1 到 50）...")
    try:
        # 获取已存在的用户 ID 和用户信息中的 user_id
        existing_user_ids = set(user.id for user in User.query.all())
        existing_info_user_ids = set(info.user_id for info in UserInformation.query.all())

        users_to_insert = []
        information_to_insert = []

        # 准备用户和用户信息
        for user_id in range(1, 51):  # id 从 1 到 50
            # 检查用户是否已存在
            if user_id in existing_user_ids:
                print(f"ID 为 {user_id} 的用户已存在，跳过插入用户...")
            else:
                # 生成唯一的用户名
                while True:
                    username = fake.user_name()
                    if not User.query.filter_by(username=username).first():
                        break

                user = User(
                    id=user_id,
                    username=username,
                    password="password123",
                    role=UserRole.User.value,
                )
                users_to_insert.append(user)
                print(f"已准备用户 {user_id}：{username}")

            # 检查用户信息是否已存在
            if user_id in existing_info_user_ids:
                print(f"ID 为 {user_id} 的用户信息已存在，跳过插入信息...")
            else:
                information = UserInformation(
                    user_id=user_id  # 显式设置 user_id
                )
                information_to_insert.append(information)
                print(f"已准备用户信息 {user_id}")

        # 插入用户
        if users_to_insert:
            db.session.bulk_save_objects(users_to_insert)
            db.session.commit()
            print(f"成功插入 {len(users_to_insert)} 个新用户。")
        else:
            print("无需插入新用户，所有用户已存在。")

        # 插入用户信息
        if information_to_insert:
            db.session.bulk_save_objects(information_to_insert)
            db.session.commit()
            print(f"成功插入 {len(information_to_insert)} 个新用户信息。")
        else:
            print("无需插入新用户信息，所有用户信息已存在。")

    except Exception as e:
        db.session.rollback()
        print(f"插入用户或信息时出错：{type(e).__name__} - {str(e)}")
        return False
    return True


# 从 CSV 文件读取数据并保存到数据库
def load_and_save_to_database():
    # 1. 读取 CSV 文件
    print("正在从 CSV 文件加载数据...")
    try:
        categories_df = pd.read_csv("./post/categories.csv")
        posts_df = pd.read_csv("./post/posts.csv")
        comments_df = pd.read_csv("./post/comments.csv")
        relationships_df = pd.read_csv("./post/relationships.csv")
    except FileNotFoundError as e:
        print(f"错误：未找到 CSV 文件 - {e}")
        return
    except Exception as e:
        print(f"加载 CSV 文件时出错：{e}")
        return

    # 2. 插入用户数据
    if not insert_random_users():
        return

    # 3. 调整 posts_df 和 comments_df 中的 user_id，确保在 1 到 50 范围内
    print("正在调整帖子和评论中的 user_id，确保在 1 到 50 范围内...")
    # 将 user_id 映射到 1 到 50 的范围：user_id = (user_id - 1) % 50 + 1
    posts_df["user_id"] = posts_df["user_id"].apply(lambda x: (x - 1) % 50 + 1)
    comments_df["user_id"] = comments_df["user_id"].apply(lambda x: (x - 1) % 50 + 1)

    # 确保数据库表已创建
    db.create_all()

    # 4. 插入 Category 数据，跳过已存在的 id
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
        return

    # 5. 插入 Post 数据，跳过已存在的 id
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
                create_time=row["create_time"],
                update_time=row["update_time"],
                comment_count=0,  # 初始为 0，后面更新
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
        return

    # 6. 插入 Relationship 数据，跳过已存在的 id
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
        return

    # 7. 插入 Comment 数据，跳过已存在的 id
    print("正在将评论数据保存到数据库...")
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
                create_time=row["create_time"],
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
        return

    # 8. 更新 Post 的 comment_count
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
        return

    print("数据加载和保存完成！")


# 主函数
def main():
    try:
        db.create_all()
    except:
        ...
    load_and_save_to_database()


if __name__ == "__main__":
    from app import app

    with app.app_context():
        # db.create_all()
        main()
