import time
from faker import Faker
import pandas as pd
import random
import requests
import json

# 初始化 Faker，设置为中文
fake = Faker("zh_CN")

# 用户 ID 范围为 1 到 100
USER_IDS = list(range(1, 101))

# 后处理生成的内容
def post_process_content(content, target_length, max_length):
    if not content:
        return None

    content_length = len(content)
    if content_length < target_length * 0.5:
        return None

    if content_length > max_length:
        content = content[:max_length]
        last_punctuation = max(
            content.rfind("。"), content.rfind("！"), content.rfind("？")
        )
        if last_punctuation != -1:
            content = content[: last_punctuation + 1]

    return content

# 使用 Ollama 调用模型生成内容
def generate_with_ollama(prompt, max_length=300, target_length=None):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "qwen2.5",
        "prompt": prompt,
        "max_tokens": max_length,
        "temperature": 0.7,
        "top_p": 0.95,
        "stream": True,
    }
    response = requests.post(url, json=data, stream=True)
    content = ""
    for line in response.iter_lines():
        if line:
            chunk = line.decode("utf-8")
            try:
                chunk_data = json.loads(chunk)
                if "response" in chunk_data:
                    content += chunk_data["response"]
            except json.JSONDecodeError:
                continue
    content = content.replace(prompt, "").strip()

    if target_length:
        max_length = int(target_length * 1.2)
        content = post_process_content(content, target_length, max_length)
        attempts = 0
        while content is None and attempts < 3:
            response = requests.post(url, json=data, stream=True)
            content = ""
            for line in response.iter_lines():
                if line:
                    chunk = line.decode("utf-8")
                    try:
                        chunk_data = json.loads(chunk)
                        if "response" in chunk_data:
                            content += chunk_data["response"]
                    except json.JSONDecodeError:
                        continue
            content = content.replace(prompt, "").strip()
            content = post_process_content(content, target_length, max_length)
            attempts += 1

    return content

# 1. 生成 Category 数据
def generate_categories(num_categories):
    categories = []
    category_names = [
        "景点推荐", "美食攻略", "旅行日记", "文化探索", "海滨体验",
        "历史遗迹", "自然风光", "家庭游玩", "自驾游攻略", "避暑胜地"
    ]
    for i in range(1, num_categories + 1):
        name = category_names[i - 1]
        prompt = f"写一句简洁自然的描述，介绍秦皇岛旅游的《{name}》，突出其特色，吸引游客，用中文，字数约20-30字：\n"
        print(f"\n生成分类 {i}/{num_categories}: {name}")
        start_time = time.time()
        description = generate_with_ollama(prompt, max_length=50, target_length=30)
        print(f"生成完成，耗时：{time.time() - start_time:.2f}秒")
        print(f"分类描述：{description}")
        categories.append({"id": i, "name": name, "description": description})
    return pd.DataFrame(categories)

# 2. 生成 Post 数据并基于内容匹配分类
def generate_posts(num_posts, user_ids, categories_df):
    posts = []
    post_categories = []

    # 定义分类和关键词的映射
    category_keywords = {
        "景点推荐": ["鸽子窝公园", "老龙头景区", "山海关古城", "黄金海岸", "北戴河海滨", "碣石山", "渔岛风景区"],
        "美食攻略": ["海鲜大餐", "烤鱿鱼", "扇贝烧烤", "海胆炒饭", "螃蟹盛宴", "当地小吃", "海鲜市场"],
        "旅行日记": ["海滨漫步", "日出观赏", "古城探秘", "沙滩露营", "亲子时光", "自驾体验", "美食之旅"],
        "文化探索": ["秦始皇东巡", "碣石山传说", "港口历史", "渔民文化", "节庆活动", "民俗风情", "历史遗迹"],
        "海滨体验": ["沙滩露营", "海上运动", "海景摄影", "亲子游乐", "日落美景", "海钓乐趣", "海滨漫步"],
        "历史遗迹": ["天下第一关", "老龙头入海", "长城文化", "明代遗迹", "军事历史", "古城风貌", "文化遗产"],
        "自然风光": ["鸽子窝日出", "黄金海岸", "北戴河海景", "碣石山风光", "渔岛美景", "湿地观鸟", "森林公园"],
        "家庭游玩": ["沙滩玩耍", "亲子露营", "海滨乐园", "动物园探秘", "游乐场欢乐", "采摘体验", "科普活动"],
        "自驾游攻略": ["沿海公路", "北戴河路线", "山海关古道", "黄金海岸", "沿途美景", "停车指南", "自驾注意事项"],
        "避暑胜地": ["北戴河清凉", "海滨度假", "森林氧吧", "避暑山庄", "海风吹拂", "夏日乐趣", "凉爽体验"]
    }

    topics = {
        "景点推荐": {
            "title_templates": ["秦皇岛{}景点推荐", "带你游览秦皇岛的{}", "秦皇岛必去的{}景点"],
            "keywords": category_keywords["景点推荐"]
        },
        "美食攻略": {
            "title_templates": ["秦皇岛必吃的{}美食", "如何品尝秦皇岛的{}", "秦皇岛{}美食攻略"],
            "keywords": category_keywords["美食攻略"]
        },
        "旅行日记": {
            "title_templates": ["秦皇岛{}旅行日记", "我的秦皇岛{}之旅", "记录秦皇岛的{}"],
            "keywords": category_keywords["旅行日记"]
        },
        "文化探索": {
            "title_templates": ["探秘秦皇岛的{}文化", "秦皇岛的{}历史", "感受秦皇岛的{}魅力"],
            "keywords": category_keywords["文化探索"]
        },
        "海滨体验": {
            "title_templates": ["秦皇岛的{}海滨体验", "如何玩转秦皇岛的{}", "秦皇岛{}海滨攻略"],
            "keywords": category_keywords["海滨体验"]
        },
        "历史遗迹": {
            "title_templates": ["探秘秦皇岛的{}历史", "秦皇岛一日游：体验{}", "秦皇岛的{}文化"],
            "keywords": category_keywords["历史遗迹"]
        },
        "自然风光": {
            "title_templates": ["秦皇岛的{}自然风光", "如何欣赏秦皇岛的{}", "秦皇岛{}风光攻略"],
            "keywords": category_keywords["自然风光"]
        },
        "家庭游玩": {
            "title_templates": ["秦皇岛的{}家庭游", "带孩子去秦皇岛体验{}", "秦皇岛{}亲子攻略"],
            "keywords": category_keywords["家庭游玩"]
        },
        "自驾游攻略": {
            "title_templates": ["秦皇岛{}自驾游攻略", "如何规划秦皇岛的{}", "秦皇岛{}自驾体验"],
            "keywords": category_keywords["自驾游攻略"]
        },
        "避暑胜地": {
            "title_templates": ["秦皇岛{}避暑攻略", "如何在秦皇岛度过一个{}假期", "秦皇岛的{}体验"],
            "keywords": category_keywords["避暑胜地"]
        }
    }

    for i in range(1, num_posts + 1):
        # 随机选择一个主分类
        main_category = random.choice(categories_df.to_dict('records'))
        category_name = main_category["name"]
        category_id = main_category["id"]

        # 生成标题和内容
        topic_data = topics[category_name]
        keyword = random.choice(topic_data["keywords"])
        title = random.choice(topic_data["title_templates"]).format(keyword)
        prompt = f"写一篇300字左右的游记，标题为《{title}》，内容与秦皇岛的《{category_name}》相关，语言自然通顺，适合家庭游客，描述具体景点、活动和感受，吸引读者前往，用中文：\n"
        print(f"\n生成帖子 {i}/{num_posts}: {title} (分类: {category_name})")
        start_time = time.time()
        content = generate_with_ollama(prompt, max_length=500, target_length=300)
        print(f"生成完成，耗时：{time.time() - start_time:.2f}秒")
        print(f"帖子内容：{content}")

        # 基于内容匹配分类
        related_categories = [main_category]  # 主分类始终包含
        for cat in categories_df.to_dict('records'):
            if cat["name"] == category_name:
                continue  # 跳过主分类，已添加
            keywords = category_keywords[cat["name"]]
            if any(keyword in content for keyword in keywords):
                related_categories.append(cat)

        # 限制最多关联 3 个分类
        if len(related_categories) > 3:
            related_categories = related_categories[:3]

        # 记录分类关系
        post_categories.append({
            "post_id": i,
            "category_ids": [cat["id"] for cat in related_categories]
        })

        # 创建帖子数据
        create_time = int(time.time()) - random.randint(0, 30 * 24 * 60 * 60)
        update_time = create_time + random.randint(0, 5 * 24 * 60 * 60)
        user_id = random.choice(user_ids)
        posts.append({
            "id": i,
            "user_id": user_id,
            "title": title,
            "content": content,
            "create_time": create_time,
            "update_time": update_time,
            "main_category": category_name,
        })

    return pd.DataFrame(posts), post_categories

# 3. 生成 Comment 数据
def generate_comments(num_comments, user_ids, posts_df):
    comments = []
    post_ids = posts_df["id"].tolist()
    for i, post_id in enumerate(post_ids, 1):
        post = posts_df[posts_df["id"] == post_id].iloc[0]
        title = post["title"]
        user_id = random.choice(user_ids)
        prompt = f"写一条100字左右的简短评论，针对《{title}》的游记，内容与帖子相关，语言自然，表达真实感受或建议，适合旅游爱好者，用中文：\n"
        print(f"\n生成评论 {i}/{num_comments} 为文章 {post_id}: {title}")
        start_time = time.time()
        content = generate_with_ollama(prompt, max_length=150, target_length=100)
        print(f"生成完成，耗时：{time.time() - start_time:.2f}秒")
        print(f"评论内容：{content}")
        create_time = int(time.time()) - random.randint(0, 15 * 24 * 60 * 60)
        comments.append({
            "id": i,
            "user_id": user_id,
            "post_id": post_id,
            "parent_id": None,
            "content": content,
            "create_time": create_time,
        })

    for i in range(len(post_ids) + 1, num_comments + 1):
        post_id = random.choice(post_ids)
        post = posts_df[posts_df["id"] == post_id].iloc[0]
        title = post["title"]
        user_id = random.choice(user_ids)
        available_parents = [c["id"] for c in comments if c["post_id"] == post_id]
        parent_id = random.choice(available_parents) if random.random() < 0.5 and available_parents else None
        prompt = f"写一条100字左右的简短评论，针对《{title}》的游记，内容与帖子相关，语言自然，表达真实感受或建议，适合旅游爱好者，用中文：\n"
        print(f"\n生成评论 {i}/{num_comments} 为文章 {post_id}: {title}")
        start_time = time.time()
        content = generate_with_ollama(prompt, max_length=150, target_length=100)
        print(f"生成完成，耗时：{time.time() - start_time:.2f}秒")
        create_time = int(time.time()) - random.randint(0, 15 * 24 * 60 * 60)
        comments.append({
            "id": i,
            "user_id": user_id,
            "post_id": post_id,
            "parent_id": parent_id,
            "content": content,
            "create_time": create_time,
        })
    return pd.DataFrame(comments)

# 4. 生成 Relationship 数据
def generate_relationships(post_categories):
    relationships = []
    for entry in post_categories:
        post_id = entry["post_id"]
        category_ids = entry["category_ids"]
        for category_id in category_ids:
            relationships.append({
                "id": len(relationships) + 1,
                "category_id": category_id,
                "post_id": post_id,
            })
    return pd.DataFrame(relationships)

# 生成数据
num_categories = 10
num_posts = 200
num_comments = 500

print("正在生成类别...")
categories_df = generate_categories(num_categories)

print("正在生成帖子...")
posts_df, post_categories = generate_posts(num_posts, USER_IDS, categories_df)

print("正在生成评论...")
comments_df = generate_comments(num_comments, USER_IDS, posts_df)

print("正在建立关系...")
relationships_df = generate_relationships(post_categories)

# 打印数据预览
print("分类:")
print(categories_df.head())
print("\n帖子:")
print(posts_df.head())
print("\n评论:")
print(comments_df.head())
print("\n关系:")
print(relationships_df.head())

# 保存到 CSV 文件
categories_df.to_csv("./post/categories.csv", index=False)
posts_df.to_csv("./post/posts.csv", index=False)
comments_df.to_csv("./post/comments.csv", index=False)
relationships_df.to_csv("./post/relationships.csv", index=False)

print("数据生成完成。")