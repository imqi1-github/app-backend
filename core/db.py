from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import db_config

# 处理数据库密码中的特殊字符
db_config.password = db_config.password.replace('@', '%40')

# 数据库连接URL
db_url = f'mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.name}?charset=utf8'

# 创建数据库连接和会话
engine = create_engine(db_url, pool_size=20, max_overflow=0, pool_recycle=3600, echo=True)
Session = sessionmaker(bind=engine)
BaseModel = declarative_base()


class Number(BaseModel):
    __tablename__ = 'number'
    number = Column(Integer, primary_key=True, autoincrement=False)

    def __repr__(self):
        return f'<Number {self.number}>'


create_tables = lambda: BaseModel.metadata.create_all(engine)

# 入口函数，直接调用创建表的函数
if __name__ == '__main__':
    create_tables()  # 创建所有继承自BaseModel的表
