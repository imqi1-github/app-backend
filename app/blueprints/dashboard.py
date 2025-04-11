import traceback
from functools import wraps

from flask import Blueprint, request, make_response
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import and_, func

from app.api.map import get_coordinates
from app.constants import UserRole
from app.extensions import db
from app.models import (
    Comment,
    Attachment,
    Relationship,
    User,
    Post,
    UserInformation,
    Subscribe,
    Category,
    Spot,
)

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


@dashboard_blueprint.route("/overview")
def overview():
    data = {}

    user_count = db.session.query(func.count(User.id)).scalar()
    data["user_count"] = user_count

    post_count = db.session.query(func.count(Post.id)).scalar()
    data["post_count"] = post_count

    comment_count = db.session.query(func.count(Comment.id)).scalar()
    data["comment_count"] = comment_count

    attachment_count = db.session.query(func.count(Attachment.id)).scalar()
    data["attachment_count"] = attachment_count

    recent_posts = (
        db.session.query(Post).order_by(Post.create_time.desc()).limit(8).all()
    )
    data["recent_posts"] = [post.json for post in recent_posts]

    recent_users = db.session.query(User).order_by(User.id.desc()).limit(5).all()
    data["recent_users"] = [user.json for user in recent_users]

    province_statistics = (
        db.session.query(
            UserInformation.position_province,
            func.count(UserInformation.id).label("count"),
        )
        .group_by(UserInformation.position_province)
        .all()
    )
    data["province_statistics"] = [
        {"name": province, "value": count} for province, count in province_statistics
    ]

    city_statistics = (
        db.session.query(
            UserInformation.position_city, func.count(UserInformation.id).label("count")
        )
        .group_by(UserInformation.position_city)
        .all()
    )
    data["city_statistics"] = [
        {"name": city, "value": count} for city, count in city_statistics
    ]

    top_users = (
        db.session.query(
            User.id,
            User.username,
            UserInformation.nickname,
            UserInformation.avatar_path,
            func.count(Subscribe.subscribed_user_id).label("fan_count"),
        )
        .join(Subscribe, User.id == Subscribe.subscribed_user_id)
        .outerjoin(UserInformation, User.id == UserInformation.user_id)
        .group_by(User.id, User.username, UserInformation.nickname)
        .order_by(func.count(Subscribe.subscribed_user_id).desc())
        .limit(5)
        .all()
    )

    data["top_users"] = [
        {
            "user_id": user_id,
            "username": username,
            "nickname": nickname,
            "avatar_path": avatar_path,
            "fan_count": fan_count,
        }
        for user_id, username, nickname, avatar_path, fan_count in top_users
    ]

    top_subscriber = (
        db.session.query(
            User.id,
            User.username,
            UserInformation.nickname,
            UserInformation.avatar_path,
            func.count(Subscribe.user_id).label("subscriber_count"),
        )
        .join(Subscribe, User.id == Subscribe.user_id)
        .outerjoin(UserInformation, User.id == UserInformation.user_id)
        .group_by(User.id, User.username, UserInformation.nickname)
        .order_by(func.count(Subscribe.user_id).desc())
        .limit(5)
        .all()
    )

    data["top_subscriber"] = [
        {
            "user_id": user_id,
            "username": username,
            "nickname": nickname,
            "avatar_path": avatar_path,
            "count": count,
        }
        for user_id, username, nickname, avatar_path, count in top_subscriber
    ]

    post_counts = (
        db.session.query(Category.name, func.count(Relationship.post_id).label("count"))
        .join(Relationship, Category.id == Relationship.category_id)
        .group_by(Category.name)
        .all()
    )

    data["post_counts"] = [
        {"name": category_name, "value": count} for category_name, count in post_counts
    ]

    return data


@dashboard_blueprint.route("/spot_new", methods=["POST"])
def new_spot():
    data = request.json

    title = data.get("title")
    if not title:
        return {"error": "标题不能为空"}

    start_time = data.get("start_time")
    if not start_time:
        return {"error": "开始时间不能为空"}

    end_time = data.get("end_time")
    if not end_time:
        return {"error": "结束时间不能为空"}

    position = data.get("position")
    if not position:
        return {"error": "位置不能为空"}

    coordinates = get_coordinates(position)
    try:
        if not coordinates:
            return {"error": "获取坐标失败"}
        coordinates = coordinates.get("geocodes")[0].get("location")
    except:
        return {"error": "获取坐标失败"}  

    picture = data.get("picture")
    content = data.get("content")
    if not content:
        return {"error": "内容不能为空"}

    try:

        spot = Spot(
            title=title,
            start_time=start_time,
            end_time=end_time,
            position=position,
            coordinates=coordinates,
            pictures=picture,
            content=content,
        )
        db.session.add(spot)

        db.session.commit()
        return {"msg": "添加成功", "spot_id": spot.id}
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500
