from flask import Blueprint, request
from sqlalchemy import and_

from app.constants import UserRole
from app.extensions import db
from app.models.user import User

user_blueprint = Blueprint("user", __name__)

@user_blueprint.route("/new", methods=["POST"])
def new_user():
    args = request.json
    username = args.get("username")
    if not username:
        return {"error": "必须填写用户名"}, 400
    password = args.get("password")
    if not password:
        return {"error": "必须填写密码"}, 400
    email = args.get("email")
    if not email:
        return {"error": "必须填写邮箱"}, 400
    nickname = args.get("nickname")
    if not nickname:
        nickname = username
    role = UserRole.User

    try:
        db.session.add(User(username=username, password=password, email=email, nickname=nickname, role=role))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500

@user_blueprint.route("/login", methods=["POST"])
def login():
    args = request.json
    username = args.get("username")
    if not username:
        return {"error": "必须填写用户名"}, 400
    password = args.get("password")
    if not password:
        return {"error": "必须填写密码"}, 400

    try:
        id = db.session.query(User.id).where(and_(User.username == username, User.password == password)).first()
        if not id:
            return {"error": "用户名或密码填写错误"}, 400
        return {"msg": "登录成功", "user_id": id[0]}
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}, 500
