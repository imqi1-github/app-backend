from flask import Blueprint, request

from app.api.qweather.weather import (
    get_weather_now,
    get_weather_forecast_daily,
    get_weather_forecast_hourly,
    get_air_quality_current,
    get_air_quality_forecast,
)

weather_blueprint = Blueprint("weather", __name__)


@weather_blueprint.route("/now", methods=["GET", "POST"])
def weather_now():
    """
    格式参考：https://dev.qweather.com/docs/api/weather/weather-now/
    """
    location = request.args.get("location", None)
    if not location:
        return {"error": "位置参数必须填写"}
    return get_weather_now(location)


@weather_blueprint.route("/forecast-daily", methods=["GET", "POST"])
def weather_forecast():
    """
    格式参考：https://dev.qweather.com/docs/api/weather/weather-daily-forecast/
    """
    location = request.args.get("location", None)
    if not location:
        return {"error": "位置参数必须填写"}
    day = request.args.get("day", None)
    return get_weather_forecast_daily(location, day)


@weather_blueprint.route("/forecast-hourly", methods=["GET", "POST"])
def weather_forecast_hourly():
    """
    格式参考：https://dev.qweather.com/docs/api/weather/weather-hourly-forecast/
    """
    location = request.args.get("location", None)
    if not location:
        return {"error": "位置参数必须填写"}
    return get_weather_forecast_hourly(location)


@weather_blueprint.route("/air-quality-current", methods=["GET", "POST"])
def air_quality_current():
    """
    格式参考 https://dev.qweather.com/docs/api/air-quality/air-current/
    """
    location = request.args.get("location", None)
    if not location:
        return {"error": "位置参数必须填写"}
    return get_air_quality_current(location)


@weather_blueprint.route("/air-quality-daily", methods=["GET", "POST"])
def air_quality_daily():
    """
    格式参考：https://dev.qweather.com/docs/api/air-quality/air-daily-forecast/
    """
    location = request.args.get("location", None)
    if not location:
        return {"error": "位置参数必须填写"}
    return get_air_quality_forecast(location)
