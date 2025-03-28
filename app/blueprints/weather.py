from flask import Blueprint, request

from app.api.qweather.weather import (
    get_weather_now,
    get_weather_forecast_daily,
    get_weather_forecast_hourly,
    get_air_quality_current,
    get_air_quality_forecast,
    get_location_coordinate,
    get_minutely_precipitation,
    get_indices,
    get_indices_daily
)
from app.config import is_redis_on
from app.extensions import load, save, log
from app.utils import print_blanks

weather_blueprint = Blueprint("weather", __name__)


@weather_blueprint.route("/coordinates", methods=["GET"])
@print_blanks
def get_coordinates():
    """获取指定位置的经纬度坐标"""
    log("INFO", f"{request.method} /coordinates, args: {request.args.to_dict()}")
    location = request.args.get("location", None)
    if not location:
        log("ERROR", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        result = load(f"coordinates@{location}")
        if result:
            log("INFO", f"从缓存加载坐标: {location}")
            return {"lat": result[0], "lon": result[1]}
    result = get_location_coordinate(location)
    if is_redis_on():
        save(f"coordinates@{location}", result)
        log("INFO", f"保存坐标到缓存: {location}")
    return {"lat": result[0], "lon": result[1]}


@weather_blueprint.route("/now", methods=["GET", "POST"])
@print_blanks
def weather_now():
    """
    获取实时天气信息
    格式参考：https://dev.qweather.com/docs/api/weather/weather-now/
    """
    log("INFO", f"{request.method} /now, args: {request.args.to_dict()}")
    location = request.args.get("location", None)
    if not location:
        log("ERROR", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        result = load(f"weather_now@{location}")
        if result:
            log("INFO", f"从缓存加载实时天气: {location}")
            return result
    result = get_weather_now(location)
    if is_redis_on():
        save(f"weather_now@{location}", result)
        log("INFO", f"保存实时天气到缓存: {location}")
    return result


@weather_blueprint.route("/forecast-daily", methods=["GET", "POST"])
@print_blanks
def weather_forecast():
    """
    获取每日天气预报
    格式参考：https://dev.qweather.com/docs/api/weather/weather-daily-forecast/
    """
    log("INFO", f"{request.method} /forecast-daily, args: {request.args.to_dict()}")
    location = request.args.get("location", None)
    day = request.args.get("day", None)
    if not location:
        log("ERROR", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        cache_key = (
            f"forecast_daily@{location}@{day}" if day else f"forecast_daily@{location}"
        )
        result = load(cache_key)
        if result:
            log("INFO", f"从缓存加载每日天气预报: {location}, day: {day}")
            return result
    result = get_weather_forecast_daily(location, day)
    if is_redis_on():
        save(cache_key, result)
        log("INFO", f"保存每日天气预报到缓存: {location}, day: {day}")
    return result


@weather_blueprint.route("/forecast-hourly", methods=["GET", "POST"])
@print_blanks
def weather_forecast_hourly():
    """
    获取逐小时天气预报
    格式参考：https://dev.qweather.com/docs/api/weather/weather-hourly-forecast/
    """
    log("INFO", f"{request.method} /forecast-hourly, args: {request.args.to_dict()}")
    location = request.args.get("location", None)
    if not location:
        log("ERROR", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        result = load(f"forecast_hourly@{location}")
        if result:
            log("INFO", f"从缓存加载逐小时天气预报: {location}")
            return result
    result = get_weather_forecast_hourly(location)
    if is_redis_on():
        save(f"forecast_hourly@{location}", result)
        log("INFO", f"保存逐小时天气预报到缓存: {location}")
    return result


@weather_blueprint.route("/air-quality-current", methods=["GET", "POST"])
@print_blanks
def air_quality_current():
    """
    获取当前空气质量
    格式参考：https://dev.qweather.com/docs/api/air-quality/air-current/
    """
    log(
        "INFO", f"{request.method} /air-quality-current, args: {request.args.to_dict()}"
    )
    location = request.args.get("location", None)
    if not location:
        log("ERROR", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        result = load(f"air_quality_current@{location}")
        if result:
            log("INFO", f"从缓存加载当前空气质量: {location}")
            return result
    result = get_air_quality_current(location)
    if is_redis_on():
        save(f"air_quality_current@{location}", result)
        log("INFO", f"保存当前空气质量到缓存: {location}")
    return result


@weather_blueprint.route("/air-quality-daily", methods=["GET", "POST"])
@print_blanks
def air_quality_daily():
    """
    获取每日空气质量预报
    格式参考：https://dev.qweather.com/docs/api/air-quality/air-daily-forecast/
    """
    log("INFO", f"{request.method} /air-quality-daily, args: {request.args.to_dict()}")
    location = request.args.get("location", None)
    if not location:
        log("ERROR", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        result = load(f"air_quality_daily@{location}")
        if result:
            log("INFO", f"从缓存加载每日空气质量预报: {location}")
            return result
    result = get_air_quality_forecast(location)
    if is_redis_on():
        save(f"air_quality_daily@{location}", result)
        log("INFO", f"保存每日空气质量预报到缓存: {location}")
    return result


@weather_blueprint.route("/minutely-precipitation", methods=["GET", "POST"])
@print_blanks
def minutely_precipitation():
    """
    获取分钟级降水信息
    格式参考：https://dev.qweather.com/docs/api/minutely/minutely-precipitation/
    """
    log(
        "INFO",
        f"{request.method} /minutely-precipitation, args: {request.args.to_dict()}",
    )
    location = request.args.get("location", None)
    if not location:
        log("WARNING", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        result = load(f"minutely_precipitation@{location}")
        if result:
            log("INFO", f"从缓存加载分钟级降水: {location}")
            return result
    result = get_minutely_precipitation(location)
    if is_redis_on():
        save(f"minutely_precipitation@{location}", result)
        log("INFO", f"保存分钟级降水到缓存: {location}")
    return result


@weather_blueprint.route("/get_indices", methods=["GET", "POST"])
@print_blanks
def get_indices_forecast():
    """
    获取天气指数预报
    格式参考：https://dev.qweather.com/docs/api/indices/indices-forecast/
    """
    log("INFO", f"{request.method} /get_indices, args: {request.args.to_dict()}")
    location = request.args.get("location", None)
    if not location:
        log("WARNING", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        result = load(f"indices@{location}")
        if result:
            log("INFO", f"从缓存加载天气指数: {location}")
            return result
    result = get_indices(location)
    if is_redis_on():
        save(f"indices@{location}", result)
        log("INFO", f"保存天气指数到缓存: {location}")
    return result


@weather_blueprint.route("/get_indices_daily", methods=["GET", "POST"])
@print_blanks
def get_indices_daily_forecast():
    """
    获取天气指数预报
    格式参考：https://dev.qweather.com/docs/api/indices/indices-forecast/
    """
    log("INFO", f"{request.method} /get_indices_daily, args: {request.args.to_dict()}")
    location = request.args.get("location", None)
    if not location:
        log("WARNING", "位置参数未填写")
        return {"error": "位置参数必须填写"}
    if is_redis_on():
        result = load(f"indices_daily@{location}")
        if result:
            log("INFO", f"从缓存加载天气指数: {location}")
            return result
    result = get_indices_daily(location)
    if is_redis_on():
        save(f"indices_daily@{location}", result)
        log("INFO", f"保存天气指数到缓存: {location}")
    return result
