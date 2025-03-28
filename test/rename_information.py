from app.extensions import db
from app.models.user import UserInformation
from app import app
from faker import Faker
import random

# 形容词列表
adjectives = [
    "温柔",
    "活泼",
    "安静",
    "勇敢",
    "聪明",
    "可爱",
    "优雅",
    "善良",
    "幽默",
    "坚强",
    "灵动",
    "甜美",
    "沉稳",
    "热情",
    "神秘",
    "纯真",
]

# 名词列表
nouns = [
    "风",
    "云",
    "花",
    "月",
    "星",
    "海",
    "梦",
    "雪",
    "光",
    "影",
    "雨",
    "林",
    "鸟",
    "石",
    "泉",
    "舟",
]


# 封装方法，每次返回一个随机昵称
def get_random_nickname():
    adj = random.choice(adjectives)
    noun = random.choice(nouns)
    return f"{adj}的{noun}"


fake = Faker()

with app.app_context():
    informations = db.session.query(UserInformation).all()

    for information in informations:
        information.email = fake.email()
        information.nickname = f"{get_random_nickname()}"

    db.session.commit()
