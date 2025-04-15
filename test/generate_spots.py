import os
import random
from datetime import time
from os import getcwd

from app import app
from app.extensions import db
from app.models import Spot

print(getcwd())

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

# 获取图片列表
all_images = [
    f for f in os.listdir(image_folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))
]

spots_data = []
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
areas = ["北戴河区", "山海关区", "海港区", "昌黎县"]

for i in range(20):
    title = titles[i]
    position = f"河北省秦皇岛市{areas[distinct_index[i]]}"

    # 随机选择 2-4 张图片
    selected_images = random.sample(all_images, k=random.randint(4, 8))
    picture_urls = ",".join(image_url_prefix + img for img in selected_images)
    full_address = "河北省秦皇岛市" + title

    spot = Spot(
        title=title,
        good=50 + i * 3,
        bad=5 + i % 4,
        start_time=time(8, 0),
        end_time=time(21, 0),
        position=position,
        coordinates=coordinates[i],
        province="河北省",
        city="秦皇岛市",
        place=areas[distinct_index[i]],
        pictures=picture_urls,
        views=100 + i * 10,
        content=content.format(title=title, position=position),
    )
    spots_data.append(spot)

# 插入数据库
with app.app_context():
    spots = db.session.query(Spot).all()
    for spot in spots:
        db.session.delete(spot)
    db.session.commit()
    db.session.bulk_save_objects(spots_data)
    db.session.commit()
    print("成功插入 20 条景点数据。")
