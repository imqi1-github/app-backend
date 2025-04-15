from requests import get

from app.config import map_web_api_key
from app.extensions import load, save

coordinates_api = "https://restapi.amap.com/v3/geocode/geo?key=%s&address=%s"

location_api = "https://restapi.amap.com/v3/geocode/regeo?key=%s&location=%s"


def get_coordinates(place, city=None):
    if not place:
        return {"error": "地点必须填写"}

    result = load(f"{place}{'+' + city if city else ''}@coordinates")
    if result:
        return result

    if not city:
        result = get(coordinates_api % (map_web_api_key, place))
    else:
        result = get(coordinates_api % (map_web_api_key, f"{place}&city={city}"))

    save(f"{place}{'+' + city if city else ''}@coordinates", result.json())

    return result.json()


def get_location(coordinates):
    if not coordinates:
        return {"error": "坐标必须填写"}

    result = load(f"{coordinates}@location")
    if result:
        return result

    result = get(location_api % (map_web_api_key, coordinates))

    save(f"{coordinates}@location", result.json())

    return result.json()
