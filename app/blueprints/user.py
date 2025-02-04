from flask import Blueprint, request

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