import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from faker import Faker

# 初始化 Faker，设置为中文
fake = Faker("zh_CN")

# 用户 ID 范围为 1 到 100
USER_IDS = list(range(1, 51))

# 线程锁，用于确保打印输出不乱序
print_lock = threading.Lock()


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
def generate_with_ollama(prompt, max_length=500, target_length=None, task_id=None, task_name=""):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "max_tokens": max_length,
        "temperature": 0.7,
        "top_p": 0.95,
        "stream": True,
    }
    start_time = time.time()
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

    with print_lock:
        print(f"\n{task_name} {task_id} 生成完成，耗时：{time.time() - start_time:.2f}秒")
        print(f"生成内容：{content}")

    return content


# 1. 生成 Category 数据（并发）
def generate_categories(num_categories):
    categories = []
    category_names = [
        "景点推荐", "美食攻略", "旅行日记", "文化探索", "海滨体验",
        "历史遗迹", "自然风光", "家庭游玩", "自驾游攻略", "避暑胜地"
    ]

    def generate_category(i, name):
        prompt = f"写一句简洁自然的描述，介绍秦皇岛旅游的《{name}》，突出其特色，吸引游客，用中文，字数约20-30字：\n"
        description = generate_with_ollama(
            prompt, max_length=50, target_length=30, task_id=f"{i}/{num_categories}", task_name=f"分类 {name}"
        )
        return {"id": i, "name": name, "description": description}

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_category = {
            executor.submit(generate_category, i, name): (i, name)
            for i, name in enumerate(category_names, 1)
        }
        for future in as_completed(future_to_category):
            i, name = future_to_category[future]
            try:
                category = future.result()
                categories.append(category)
            except Exception as e:
                with print_lock:
                    print(f"分类 {name} 生成失败: {e}")

    return pd.DataFrame(sorted(categories, key=lambda x: x["id"]))


# 2. 生成 Post 数据并基于内容匹配分类（并发）
def generate_posts(num_posts, user_ids, categories_df):
    posts = []
    post_categories = []
    lock = threading.Lock()  # 用于线程安全地追加数据

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
            "title_templates": [
                "{}旅游攻略",
                "秦皇岛CityWalk打卡攻略，今天的目的地是{}",
                "秦皇岛必去的{}景点",
                "打卡秦皇岛最值得去的{}",
                "第一次来秦皇岛，{}真的惊艳到我了！",
                "{}是秦皇岛隐藏的宝藏打卡地吗？",
                "去了{}才发现，秦皇岛原来这么好玩",
                "谁懂啊！这个{}真的美哭了",
                "秦皇岛{}游玩路线全攻略来了",
                "去{}是种什么体验？我来告诉你！"
            ],
            "keywords": category_keywords["景点推荐"]
        },
        "美食攻略": {
            "title_templates": [
                "秦皇岛必吃的{}美食",
                "如何品尝秦皇岛的{}",
                "秦皇岛{}美食攻略",
                "探店！秦皇岛最好吃的{}是哪家？",
                "吃了一口{}，我彻底爱上秦皇岛",
                "{}控狂喜！秦皇岛也能吃到地道味道",
                "秦皇岛超好吃{}推荐（含店铺地址）",
                "不踩雷的{}店都在这儿了",
                "{}原来可以这么好吃！秦皇岛也太会做饭了吧",
                "来秦皇岛一定要吃的{}，错过会后悔"
            ],
            "keywords": category_keywords["美食攻略"]
        },
        "旅行日记": {
            "title_templates": [
                "秦皇岛{}旅行日记",
                "我的秦皇岛{}之旅",
                "记录秦皇岛的{}",
                "超治愈的一次秦皇岛{}旅行",
                "去秦皇岛{}那几天，我好像爱上了这里",
                "在{}的每一刻，都好想暂停时间",
                "一场说走就走的秦皇岛{}之旅",
                "{}让我重新认识了秦皇岛",
                "那些年我在秦皇岛{}的瞬间",
                "超真实！秦皇岛{}游记分享"
            ],
            "keywords": category_keywords["旅行日记"]
        },
        "文化探索": {
            "title_templates": [
                "探秘秦皇岛的{}文化",
                "秦皇岛的{}历史",
                "感受秦皇岛的{}魅力",
                "{}原来是秦皇岛文化的灵魂",
                "秦皇岛人的{}情结有多深？",
                "走进秦皇岛{}的前世今生",
                "沉浸式体验秦皇岛{}",
                "关于秦皇岛{}你了解多少？",
                "从{}看秦皇岛文化底蕴",
                "去秦皇岛{}，仿佛穿越了历史"
            ],
            "keywords": category_keywords["文化探索"]
        },
        "海滨体验": {
            "title_templates": [
                "秦皇岛的{}海滨体验",
                "如何玩转秦皇岛的{}",
                "秦皇岛{}海滨攻略",
                "我在{}吹了一整个夏天的海风",
                "来秦皇岛{}看海真的太舒服了",
                "谁说北方的海不美？秦皇岛{}不服",
                "{}真的是拍照圣地！出片率百分百",
                "在秦皇岛{}，把烦恼全都留在海里了",
                "{}适合发呆，也适合恋爱",
                "超小众！秦皇岛的{}你一定没去过"
            ],
            "keywords": category_keywords["海滨体验"]
        },
        "历史遗迹": {
            "title_templates": [
                "探秘秦皇岛的{}历史",
                "秦皇岛一日游：体验{}",
                "秦皇岛的{}文化",
                "{}：穿越秦皇岛的千年光阴",
                "站在{}，仿佛能听见历史在说话",
                "{}是秦皇岛最有故事的地方之一",
                "秦皇岛人的童年记忆：{}",
                "{}真的太震撼了，历史感扑面而来",
                "漫步{}，仿佛走进历史画卷",
                "秦皇岛{}打卡指南，附交通&票价"
            ],
            "keywords": category_keywords["历史遗迹"]
        },
        "自然风光": {
            "title_templates": [
                "秦皇岛的{}自然风光",
                "如何欣赏秦皇岛的{}",
                "秦皇岛{}风光攻略",
                "{}：随手一拍就是壁纸级别",
                "在秦皇岛{}，把城市的喧嚣抛在脑后",
                "秦皇岛这个{}太低调了吧？",
                "拍照党的福音！秦皇岛{}推荐",
                "{}真的有种世外桃源的感觉",
                "谁懂？{}真的太适合心情低落时去了",
                "原来秦皇岛的{}可以这么治愈"
            ],
            "keywords": category_keywords["自然风光"]
        },
        "家庭游玩": {
            "title_templates": [
                "秦皇岛的{}家庭游",
                "带孩子去秦皇岛体验{}",
                "秦皇岛{}亲子攻略",
                "{}是适合带孩子打卡的好去处",
                "亲测！秦皇岛{}对娃太友好了",
                "全家出行首选：秦皇岛{}",
                "{}不仅孩子玩得开心，大人也轻松",
                "秦皇岛{}一日游攻略，附停车&吃饭",
                "{}让孩子边玩边学，家长放心又满意",
                "周末遛娃去哪里？推荐秦皇岛{}"
            ],
            "keywords": category_keywords["家庭游玩"]
        },
        "自驾游攻略": {
            "title_templates": [
                "秦皇岛{}自驾游攻略",
                "如何规划秦皇岛的{}",
                "秦皇岛{}自驾体验",
                "这条{}自驾路线真的太舒服了",
                "开车去秦皇岛{}是一种什么体验",
                "自驾游小众路线推荐：{}",
                "{}自驾一日游，不走回头路",
                "路线+停车+景点，一篇搞定秦皇岛{}",
                "{}适合新手司机的自驾线路",
                "秦皇岛{}轻松自驾，不累还好玩"
            ],
            "keywords": category_keywords["自驾游攻略"]
        },
        "避暑胜地": {
            "title_templates": [
                "秦皇岛{}避暑攻略",
                "如何在秦皇岛度过一个{}假期",
                "秦皇岛的{}体验",
                "{}：夏天最值得去的地方",
                "避暑圣地！秦皇岛{}真的凉快又舒服",
                "不想空调续命了，去秦皇岛{}吹海风吧",
                "{}成了我夏天最爱的避暑地",
                "夏天来秦皇岛{}，简直人间清凉",
                "超实用！{}避暑避晒避烦恼",
                "逃离高温天，秦皇岛{}等你来"
            ],
            "keywords": category_keywords["避暑胜地"]
        }
    }

    def generate_post(i):
        main_category = random.choice(categories_df.to_dict('records'))
        category_name = main_category["name"]
        category_id = main_category["id"]
        topic_data = topics[category_name]
        keyword = random.choice(topic_data["keywords"])
        title = random.choice(topic_data["title_templates"]).format(keyword)
        prompt = f"""你现在是一个熟悉秦皇岛本地生活和旅游的小红书博主，请根据以下信息生成一篇内容真实、有情绪、有细节、有实用建议的图文内容，风格请模仿小红书热帖（轻松口语、有干货、有感受）。分类是{category_name}，关键词为{keyword}，标题为{title}，要求：

内容不少于200字，风格亲切自然，像是在分享自己的旅行体验

开头吸引人，中间描述细节，结尾可以推荐路线或贴士

不能使用AI或工具生成内容的口吻，要像人写的

内容不要列举景点介绍，要写“我去了”“我觉得”“这里很适合xxx”等主观表达"""
        content = generate_with_ollama(
            prompt, max_length=700, target_length=500, task_id=f"{i}/{num_posts}",
            task_name=f"帖子 {title} (分类: {category_name})"
        )

        # 基于内容匹配分类
        related_categories = [main_category]
        for cat in categories_df.to_dict('records'):
            if cat["name"] == category_name:
                continue
            keywords = category_keywords[cat["name"]]
            if any(keyword in content for keyword in keywords):
                related_categories.append(cat)
        if len(related_categories) > 3:
            related_categories = related_categories[:3]

        post_data = {
            "id": i,
            "user_id": random.choice(user_ids),
            "title": title,
            "content": content,
            "create_time": int(time.time()) - random.randint(0, 30 * 24 * 60 * 60),
            "update_time": int(time.time()) - random.randint(0, 25 * 24 * 60 * 60),
            "main_category": category_name,
        }
        category_data = {
            "post_id": i,
            "category_ids": [cat["id"] for cat in related_categories]
        }

        with lock:
            posts.append(post_data)
            post_categories.append(category_data)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(generate_post, i) for i in range(1, num_posts + 1)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                with print_lock:
                    print(f"帖子生成失败: {e}")

    return pd.DataFrame(posts), post_categories


# 3. 生成 Comment 数据（并发）
def generate_comments(num_comments, user_ids, posts_df):
    comments = []
    lock = threading.Lock()

    def generate_comment(i, post_id=None):
        if post_id is None:
            post_id = random.choice(posts_df["id"].tolist())
        post = posts_df[posts_df["id"] == post_id].iloc[0]
        title = post["title"]
        user_id = random.choice(user_ids)
        available_parents = [c["id"] for c in comments if c["post_id"] == post_id]
        parent_id = random.choice(available_parents) if random.random() < 0.5 and available_parents else None
        prompt = f"""
你现在是小红书评论区的活跃用户，请根据以下笔记内容生成10条风格自然、有互动感的小红书评论：

笔记标题：{title}

笔记内容：<贴上正文内容或精简描述，越细节越好>

要求如下：

每条评论不超过50字，风格真实、轻松、有共鸣

有人提问（如“具体在哪？”“适合带孩子吗？”）

有人点赞认同（如“我也超喜欢这！”）

有人分享自己的经验（如“我上次去人好多~”）

不要出现“AI”“ChatGPT”等词

不要机械重复，内容要多样，符合真实用户语气"""
        content = generate_with_ollama(
            prompt, max_length=150, target_length=100, task_id=f"{i}/{num_comments}",
            task_name=f"评论 for 帖子 {post_id}: {title}"
        )
        comment_data = {
            "id": i,
            "user_id": user_id,
            "post_id": post_id,
            "parent_id": parent_id,
            "content": content,
            "create_time": int(time.time()) - random.randint(0, 15 * 24 * 60 * 60),
        }
        with lock:
            comments.append(comment_data)

    with ThreadPoolExecutor(max_workers=10) as executor:
        # 为每个帖子生成至少一条评论
        post_ids = posts_df["id"].tolist()
        futures = [executor.submit(generate_comment, i, post_id) for i, post_id in enumerate(post_ids, 1)]
        # 剩余的评论随机分配
        futures += [executor.submit(generate_comment, i) for i in range(len(post_ids) + 1, num_comments + 1)]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                with print_lock:
                    print(f"评论生成失败: {e}")

    return pd.DataFrame(comments)


# 4. 生成 Relationship 数据（无需并发，数据量小）
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
start_time = time.time()
categories_df = generate_categories(num_categories)
print(f"类别生成完成，耗时：{time.time() - start_time:.2f}秒")

print("正在生成帖子...")
start_time = time.time()
posts_df, post_categories = generate_posts(num_posts, USER_IDS, categories_df)
print(f"帖子生成完成，耗时：{time.time() - start_time:.2f}秒")

print("正在生成评论...")
start_time = time.time()
comments_df = generate_comments(num_comments, USER_IDS, posts_df)
print(f"评论生成完成，耗时：{time.time() - start_time:.2f}秒")

print("正在建立关系...")
start_time = time.time()
relationships_df = generate_relationships(post_categories)
print(f"关系生成完成，耗时：{time.time() - start_time:.2f}秒")

# 打印数据预览
print("\n分类:")
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
