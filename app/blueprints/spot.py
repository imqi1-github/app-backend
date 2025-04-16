import random

from flask import Blueprint

from app.extensions import db
from app.models import Spot
from app.utils import calc_distance

spot_blueprint = Blueprint("spot", __name__)


@spot_blueprint.route("/<int:id>", methods=["GET"])
def get_spot(id):
    spot = db.session.query(Spot).where(Spot.id == id).first()
    if spot:
        spot.views += 1
        db.session.commit()
        return spot.json
    else:
        return {"error": "未找到此景点"}, 404

@spot_blueprint.route("/nearby/<int:id>", methods=["GET"])
def get_nearby_spots(id):
    spot = db.session.query(Spot).where(Spot.id == id).first()
    if not spot or not spot.coordinates:
        return {"error": "未找到此景点或坐标无效"}, 404

    try:
        lat, lon = map(float, spot.coordinates.split(","))
    except ValueError:
        return {"error": "坐标格式错误"}

    all_spots = Spot.query.all()
    nearby = []
    for s in all_spots:
        if s.id == spot.id or not s.coordinates:
            continue
        try:
            s_lat, s_lon = map(float, s.coordinates.split(","))
        except ValueError:
            continue
        distance = calc_distance(lat, lon, s_lat, s_lon)
        nearby.append({
            "spot": s.json,
            "distance": round(distance, 2)
        })

    nearest = sorted(nearby, key=lambda x: x["distance"])[:6]
    return nearest


@spot_blueprint.route("/<int:id>/good", methods=["GET"])
def good(id):
    spot = db.session.query(Spot).where(Spot.id == id).first()
    if spot:
        spot.good += 1
        db.session.commit()
        return {"msg": "成功点赞该景点"}
    else:
        return {"error": "未找到此景点"}, 404


@spot_blueprint.route("/<int:id>/bad", methods=["GET"])
def bad(id):
    spot = db.session.query(Spot).where(Spot.id == id).first()
    if spot:
        spot.bad += 1
        db.session.commit()
        return {"msg": "成功踩该景点"}
    else:
        return {"error": "未找到此景点"}, 404


@spot_blueprint.route("/random")
def get_spots():
    spots = db.session.query(Spot).all()
    if len(spots) <= 12:
        return [spot.json for spot in spots]
    return [spot.json for spot in random.sample(spots, 12)]
