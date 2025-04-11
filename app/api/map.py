from requests import get

from app.config import map_web_api_key
from app.extensions import load, save

coordinates_api = "https://restapi.amap.com/v3/geocode/geo?key=%s&address=%s"

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