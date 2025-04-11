import random

from flask import Blueprint

from app.extensions import db
from app.models import Spot

spot_blueprint = Blueprint("spot", __name__)


@spot_blueprint.route("/<int:id>", methods=["GET"])
def get_spot(id):
    spot = db.session.query(Spot).where(Spot.id == id).first()
    if spot:
        return spot.json
    else:
        return {"error": "未找到此景点"}, 404


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
