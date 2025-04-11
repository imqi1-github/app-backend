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

if __name__ == "__main__":
    from app import app

    with app.app_context():
        main()