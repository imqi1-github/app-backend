import logging
import os
import sys
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import StrictRedis
import pickle
from app.config import redis_config, is_redis_on, logging_file
import inspect
from typing import Literal


# 定义颜色代码
class Colors:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


# 初始化 Flask 扩展
db = SQLAlchemy()
migrate = Migrate()


# 允许的日志级别类型
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


def setup_logger(log_file: str = logging_file) -> logging.Logger:
    """设置日志记录器，同时支持文件和控制台输出。

    Args:
        log_file (str): 日志文件路径。

    Returns:
        logging.Logger: 配置好的日志记录器实例。
    """
    logger = logging.getLogger("CustomLogger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)

        # 使用自定义字段名 custom_filename 和 custom_lineno
        formatter = logging.Formatter(
            "%(asctime)s - %(custom_filename)s[line:%(custom_lineno)d] - %(levelname)s: %(message)s"
        )
        fh.setFormatter(formatter)

        logger.addHandler(fh)

    return logger


logger = setup_logger()


def log(level: LogLevel, message: str) -> None:
    """自定义日志记录方法，将日志同时输出到控制台和文件。

    Args:
        level (Literal["DEBUG", "INFO", "WARNING", "ERROR"]): 日志级别。
            有效值包括 "DEBUG"、"INFO"、"WARNING"、"ERROR"。
        message (str): 要记录的日志消息内容。

    Raises:
        ValueError: 如果提供的日志级别不在允许的范围内。
        TypeError: 如果 level 不是字符串或 message 不是字符串。
    """
    # 类型检查
    if not isinstance(level, str):
        raise TypeError(f"日志级别必须是字符串类型，收到 {type(level).__name__}")
    if not isinstance(message, str):
        raise TypeError(f"日志消息必须是字符串类型，收到 {type(message).__name__}")

    # 验证日志级别
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
    if level not in valid_levels:
        raise ValueError(f"无效的日志级别: {level}，必须是 {valid_levels} 中的一个")

    # 获取调用者的帧信息（跳出 log 函数本身）
    frame = inspect.currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)  # 只取文件名
    line_no = frame.f_lineno

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_format = f"{timestamp} - {filename}[line:{line_no}] - {level}: {message}"

    # 使用自定义字段名，避免与内置字段冲突
    extra = {"custom_filename": filename, "custom_lineno": line_no}

    # 根据日志级别选择颜色并记录
    if level == "ERROR":
        print(f"{Colors.RED}{log_format}{Colors.RESET}")
        logger.error(message, extra=extra)
    elif level == "WARNING":
        print(f"{Colors.YELLOW}{log_format}{Colors.RESET}")
        logger.warning(message, extra=extra)
    elif level == "INFO":
        print(f"{Colors.BLUE}{log_format}{Colors.RESET}")
        logger.info(message, extra=extra)
    elif level == "DEBUG":
        print(f"{Colors.GREEN}{log_format}{Colors.RESET}")
        logger.debug(message, extra=extra)


# Redis 初始化
if is_redis_on():
    redis_cli = StrictRedis(
        decode_responses=False,
        host=redis_config.host,
        port=redis_config.port,
    )
else:
    redis_cli = None


def save(key: str, obj: any, ex=1800) -> bool:
    """将 Python 对象保存到 Redis"""
    if redis_cli is None:
        log("ERROR", "Redis未启动")
        raise Exception("Redis未启动")
    try:
        serialized_obj = pickle.dumps(obj)
        result = redis_cli.set(key, serialized_obj, ex)
        log("INFO", f"成功保存对象到Redis，key={key}")
        return result
    except Exception as e:
        log("ERROR", f"保存到Redis时出错: {str(e)}")
        return False


def load(key: str) -> any:
    """从 Redis 加载 Python 对象"""
    if redis_cli is None:
        log("ERROR", "Redis未启动")
        raise Exception("Redis未启动")
    try:
        serialized_obj = redis_cli.get(key)
        if serialized_obj is None:
            log("WARNING", f"Redis中未找到key={key}")
            return None
        result = pickle.loads(serialized_obj)
        log("INFO", f"成功从Redis加载对象，key={key}，value={result}")
        return result
    except Exception as e:
        log("ERROR", f"从Redis加载时出错: {str(e)}")
        return None
