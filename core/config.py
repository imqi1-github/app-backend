import os

import yaml
from os import getenv


class Config:
    def __init__(self, config_dict):
        self._config = config_dict

    def __getattr__(self, name):
        if name in self._config:
            value = self._config[name]
            if isinstance(value, dict):
                value = Config(value)
            return value
        raise AttributeError(f"配置无 '{name}' 项，请检查")

    def __repr__(self):
        return str(self._config)


def load_config(file_path):
    with open(file_path, 'r') as file:
        config_data = yaml.load(file, Loader=yaml.SafeLoader)
    return Config(config_data)


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
