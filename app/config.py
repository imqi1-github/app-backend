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
    with open(file_path, "r") as file:
        config_data = yaml.load(file, Loader=yaml.SafeLoader)
    return ConfigReader(config_data)


current_file = os.path.realpath(__file__)
config_file = os.path.abspath(os.path.join(current_file, "../../config.yaml"))
config = load_config(config_file)

# 和风天气API key
qweather_api_key = config.qweather_api_key
map_web_api_key = config.map_web_api_key
logging_file = config.logging_file
ai_url = config.ai_url
model = config.model

env = getenv("ENVIRONMENT", "development")

match env:
    case "development":
        config = config.development
    case "production":
        config = config.production
    case _:
        config = config.production

db_config = config.db
db_config.password = db_config.password.replace("@", "%40")

backend_url = config.backend
redis_config = config.redis
print(f"Redis状态：{redis_config}")

# 数据库连接URL
db_url = f"mysql+pymysql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.name}?charset=utf8"


class Config:
    SQLALCHEMY_DATABASE_URI = db_url  # 这里可以根据需要换成其他数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def is_redis_on():
    return config.redis.state
