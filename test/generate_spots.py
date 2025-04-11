from datetime import time

from app import app
from app.models import Spot
from app.extensions import db

coordinates = "119.484490,39.834912"
picture_url = "https://localhost:5000/download/wallpaper.png"
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

# 生成数据
spots_data = []
titles = [
    "老虎石海上公园", "山海关古城", "新澳海底世界", "碧螺塔酒吧公园", "野生动物园",
    "南戴河国际娱乐中心", "秦皇求仙入海处", "联峰山公园", "燕塞湖", "角山长城",
    "鸽子窝公园", "怪楼奇园", "天下第一关", "老龙头", "北戴河博物馆",
    "石河公园", "黄金海岸", "海滨汽车影院", "奥林匹克大道公园", "秦皇岛森林公园"
]
areas = ["北戴河区", "山海关区", "海港区"]

for i in range(20):
    title = titles[i]
    position = f"河北省秦皇岛市{areas[i % len(areas)]}"
    spot = Spot(
        title=title,
        good=50 + i * 3,
        bad=5 + i % 4,
        start_time=time(8, 0),
        end_time=time(21, 0),
        position=position,
        coordinates=coordinates,
        pictures=picture_url,
        views=100 + i * 10,
        content=content.format(title=title, position=position)
    )
    spots_data.append(spot)

# 插入数据库
with app.app_context():
    db.session.bulk_save_objects(spots_data)
    db.session.commit()
    print("成功插入 20 条景点数据。")