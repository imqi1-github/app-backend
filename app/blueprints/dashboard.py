from functools import wraps

from flask import Blueprint, request, make_response
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import and_

from app.constants import UserRole
from app.extensions import db
from app.models.user import User

dashboard_blueprint = Blueprint("dashboard", __name__)

serializer = URLSafeTimedSerializer("admin-user-key")


def get_userid_by_cookie():
    user_id_cookie = request.cookies.get("admin_userid")
    if not user_id_cookie:
        return None
    try:
        return serializer.loads(user_id_cookie)
    except (BadSignature, SignatureExpired):
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_userid_by_cookie()

        if not user_id:
            return {"error": "用户未登录或登录状态过期"}, 403
        # 查询数据库验证用户是否存在
        user = db.session.query(User).where(User.id == user_id).first()
        if not user:
            return {"error": "用户不存在"}, 403
        if not user.role != UserRole.Admin:
            return {"error": "用户权限不足"}, 403

        # 将解密的user_id和用户对象作为参数传递给被装饰的函数
        return f(*args, **kwargs)

    return decorated_function


@dashboard_blueprint.route("/login", methods=["POST"])
def login():
    args = request.json
    username = args.get("username")
    if not username:
        return {"error": "必须填写用户名"}
    password = args.get("password")
    if not password:
        return {"error": "必须填写密码"}

    try:
        id = (
            db.session.query(User.id)
            .where(
                and_(
                    User.username == username,
                    User.password == password,
                    User.role == UserRole.Admin.value,
                )
            )
            .first()
        )
        if not id:
            return {"error": "用户名或密码填写错误"}

        response = make_response({"msg": "登录成功"})

        encrypted_user_id = serializer.dumps(str(id[0]))

        response.set_cookie(
            "admin_userid",
            encrypted_user_id,
            max_age=60 * 60 * 24 * 3,
            httponly=True,
            secure=True,
            samesite="None",
        )

        return response
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500


@dashboard_blueprint.route("/info", methods=["GET"])
@login_required
def info():
    user_id = get_userid_by_cookie()
    if not user_id:
        return {"error": "参数 user_id 缺失"}
    result = db.session.query(User).where(User.id == user_id).first()
    return result.json


@dashboard_blueprint.route("/logout", methods=["GET"])
def logout():
    try:
        response = make_response({"msg": "退出登录成功"})

        response.delete_cookie("admin_userid", secure=True, samesite="None")

        return response
    except Exception as e:
        return {"error": str(e)}, 500
