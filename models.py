from os import getenv
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# 环境变量判断来选择不同的配置
match getenv("ENVIRONMENT"):
    case "development":
        import config_dev as config
    case "production":
        import config_prod as config
    case _:
        import config_dev as config

# 处理数据库密码中的特殊字符
config.DB_PASS = config.DB_PASS.replace('@', '%40')

# 数据库连接URL
db_url = f'mysql+pymysql://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}?charset=utf8'

# 创建数据库连接和会话
engine = create_engine(db_url, pool_size=20, max_overflow=0, pool_recycle=3600, echo=True)
Session = sessionmaker(bind=engine)
BaseModel = declarative_base()


class Number(BaseModel):
    __tablename__ = 'number'
    number = Column(Integer, primary_key=True)
    age = Column(Integer)


# 入口函数，直接调用创建表的函数
if __name__ == '__main__':
    BaseModel.metadata.create_all(engine)  # 创建所有继承自BaseModel的表
