from flask import Blueprint, request

from app.api.map import get_coordinates

map_blueprint = Blueprint("map", __name__, url_prefix="/map")
coordinates_api = "https://restapi.amap.com/v3/geocode/geo?key=%s&address=%s"


@map_blueprint.route("/coordinates")
def coordinates():
    city = request.args.get("city", None)
    place = request.args.get("place", None)

    if not place:
        return {"error": "地点必须填写"}

    return get_coordinates(place, city)
