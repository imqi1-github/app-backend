import os
from os import getenv

import yaml


class ConfigReader:
    def __init__(self, config_dict):
        self._config = config_dict

    def __getattr__(self, name):
        if name in self._config:
            value = self._config[name]
            if isinstance(value, dict):
                value = ConfigReader(value)
            return value
        raise AttributeError(f"配置无 '{name}' 项，请检查")

    def __repr__(self):
        return str(self._config)


def load_config(file_path):
    with open(file_path, 'r') as file:
        config_data = yaml.load(file, Loader=yaml.SafeLoader)
    return ConfigReader(config_data)


current_file = os.path.realpath(__file__)
config_file = os.path.abspath(os.path.join(current_file, "../../config.yaml"))
config = load_config(config_file)

env = getenv("ENVIRONMENT", "development")

match env:
    case "development":
        db_config = config.development.db
    case "production":
        db_config = config.production.db
    case _:
        db_config = config.development.db

# 处理数据库密码中的特殊字符
db_config.password = db_config.password.replace('@', '%40')

# 数据库连接URL
db_url = f'mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.name}?charset=utf8'


class Config:
    SQLALCHEMY_DATABASE_URI = db_url  # 这里可以根据需要换成其他数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False
