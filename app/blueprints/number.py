from flask import Blueprint, request

from app.extensions import db
from app.models.number import Number

number_blueprint = Blueprint('number', __name__)


@number_blueprint.route('/get', methods=['GET'])
def get_number():
    try:
        number = db.session.query(Number.number).first()
        if number:
            return {'number': number.number}
        else:
            db.session.add(Number(number=0))
            db.session.commit()
            return {'number': 0}
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500


@number_blueprint.route('/set', methods=['GET'])
def set_number():
    number_value = request.args.get('number', 0, type=int)
    try:
        number = db.session.query(Number).first()
        if number:
            number.number = number_value
        else:
            db.session.add(Number(number=number_value))
        db.session.commit()
        return {'number': number_value}
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500


@number_blueprint.route('/add', methods=['GET'])
def add_number():
    try:
        number = db.session.query(Number).first()
        if number:
            number.number += 1
        else:
            db.session.add(Number(number=1))
        db.session.commit()
        return {'number': number.number if number else 1}
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500
