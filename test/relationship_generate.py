import csv

# 定义输入和输出文件路径
input_posts_file = "./post/posts.csv"  # 原始帖子文件
input_categories_file = "./post/categories.csv"  # 分类定义文件
output_file = "./post/relationships.csv"  # 输出结果文件

# 存储分类映射：name到id的映射
category_map = {}
# 存储帖子数据
posts_data = []

# 读取categories.csv，建立分类映射
with open(input_categories_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        category_map[row["name"]] = int(row["id"])

# 读取posts.csv，获取帖子数据
with open(input_posts_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        posts_data.append(row)


# 手动分类函数
def manual_classify(post):
    print("\n=== 帖子信息 ===")
    print(f"标题: {post['title']}")
    print(f"内容: {post['content']}")
    print("\n可用分类:")
    for name, id_ in category_map.items():
        print(f"分类名称: {name}, ID: {id_}")

    while True:
        try:
            user_input = input("\n请输入分类ID: ")
            category_id = int(user_input)
            if category_id in category_map.values():
                return category_id
            else:
                print("无效的ID，请输入列表中的ID！")
        except ValueError:
            print("请输入有效的数字ID！")


# 处理每个帖子并存储结果
results = []
result_id = 1  # 用于生成连续的id

for post in posts_data:
    post_id = int(post["id"])

    # 手动分类
    category_id = manual_classify(post)

    # 添加结果
    results.append({"id": result_id, "category_id": category_id, "post_id": post_id})
    result_id += 1

# 将结果写入新的CSV文件
with open(output_file, "w", encoding="utf-8", newline="") as f:
    fieldnames = ["id", "category_id", "post_id"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"\n分类完成，结果已保存到 {output_file}")
