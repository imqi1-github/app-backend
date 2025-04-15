import math
from functools import wraps


def print_blanks(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        print("\n" + "-" * 10)
        result = func(*args, **kwargs)
        print("-" * 10, "\n")
        return result

    return decorator


def calc_distance(lon1, lat1, lon2, lat2):
    """计算两点之间的地球表面距离，单位为米"""
    R = 6371000  # 地球平均半径，单位：米
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
