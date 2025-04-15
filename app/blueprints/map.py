from flask import Blueprint, request

from app.api.map import get_coordinates, get_location
from app.extensions import db
from app.models import Spot

map_blueprint = Blueprint("map", __name__, url_prefix="/map")


@map_blueprint.route("/coordinates")
def coordinates():
    city = request.args.get("city", None)
    place = request.args.get("place", None)

    if not place:
        return {"error": "地点必须填写"}

    return get_coordinates(place, city)


@map_blueprint.route("/location")
def location():
    coordinates = request.args.get("coordinates", None)

    if not coordinates:
        return {"error": "坐标必须填写"}

    return get_location(coordinates)


@map_blueprint.route("/spots")
def spots():
    return [spot.json for spot in db.session.query(Spot).all()]
