"""
天气查询
"""

from app.api.qweather import qweather_api_key, geo_api
from requests import get

# 实时天气
real_api = "https://devapi.qweather.com/v7/weather/now"
weather_forecast_api_daily = "https://devapi.qweather.com/v7/weather/%dd"
weather_forecast_api_hour = "https://devapi.qweather.com/v7/weather/24h"
quality_api_current = "https://devapi.qweather.com/airquality/v1/current/%s/%s"
quality_api_daily = "https://devapi.qweather.com/airquality/v1/daily/%s/%s"

def get_location_code(location):
    geo_response = get(
        geo_api,
        params={"location": location},
        headers={"X-QW-Api-Key": qweather_api_key},
    )
    geo_response.raise_for_status()
    location_code = geo_response.json()["location"][0]["id"]
    return location_code


def get_location_coordinate(location):
    geo_response = get(
        geo_api,
        params={"location": location},
        headers={"X-QW-Api-Key": qweather_api_key},
    )
    geo_response.raise_for_status()
    latitude = geo_response.json()["location"][0]["lat"]
    longitude = geo_response.json()["location"][0]["lon"]
    return latitude, longitude


def get_weather_now(location):
    weather_response = get(
        real_api,
        params={"location": get_location_code(location)},
        headers={"X-QW-Api-Key": qweather_api_key},
    )
    weather_response.raise_for_status()
    return weather_response.json()


def get_weather_forecast_daily(location, day=None):
    """
    获取每日天气预报
    """
    if day is None:
        day = 7
    forecast_response = get(
        weather_forecast_api_daily % day,
        params={"location": get_location_code(location)},
        headers={"X-QW-Api-Key": qweather_api_key},
    )
    forecast_response.raise_for_status()
    return forecast_response.json()


def get_weather_forecast_hourly(location):
    forecast_response = get(
        weather_forecast_api_hour,
        params={"location": get_location_code(location)},
        headers={"X-QW-Api-Key": qweather_api_key},
    )
    forecast_response.raise_for_status()
    return forecast_response.json()

def get_air_quality_current(location):
    coordinate = get_location_coordinate(location)
    quality_response = get(
        quality_api_current % coordinate,
        headers={"X-QW-Api-Key": qweather_api_key},
    )
    quality_response.raise_for_status()
    return quality_response.json()

def get_air_quality_forecast(location):
    coordinate = get_location_coordinate(location)
    forecast_response = get(
        quality_api_daily % coordinate,
        headers={"X-QW-Api-Key": qweather_api_key},
    )
    forecast_response.raise_for_status()
    return forecast_response.json()