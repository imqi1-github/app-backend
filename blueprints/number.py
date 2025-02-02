from flask import Blueprint, request
from core.db import Session, Number

number_blueprint = Blueprint('number', __name__)


@number_blueprint.route('/get', methods=['GET'])
def get_number():
    with (Session() as session):
        try:
            number = session.query(Number.number).first()
            if number:
                return {'number': number.number}
            else:
                session.add(Number(number=0))
                session.commit()
                return {'number': 0}
        except Exception as e:
            session.rollback()
            return {'error': str(e)}, 500


@number_blueprint.route('/set', methods=['GET'])
def set_number():
    with Session() as session:
        number_value = request.args.get('number', 0, type=int)
        try:
            number = session.query(Number).first()
            if number:
                number.number = number_value
            else:
                session.add(Number(number=number_value))
            session.commit()
            return {'number': number_value}
        except Exception as e:
            session.rollback()
            return {'error': str(e)}, 500


@number_blueprint.route('/add', methods=['GET'])
def add_number():
    with Session() as session:
        try:
            number = session.query(Number).first()
            if number:
                number.number += 1
            else:
                session.add(Number(number=1))
            session.commit()
            return {'number': number.number if number else 1}
        except Exception as e:
            session.rollback()
            return {'error': str(e)}, 500
