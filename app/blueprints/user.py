import os.path
import time
import traceback
from functools import wraps

from flask import Blueprint, request, make_response
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import and_

from app.config import backend_url
from app.constants import UserRole, FileType, UserStatus
from app.extensions import db, is_redis_on, load, save, log
from app.models.post import Subscribe, Post
from app.models.user import User, Upload, Information

user_blueprint = Blueprint("user", __name__)

serializer = URLSafeTimedSerializer("user-key")


def get_userid_from_cookie():
    user_id_cookie = request.cookies.get("user_id")
    if not user_id_cookie:
        return None

    try:
        user_id = serializer.loads(user_id_cookie)
        return user_id
    except (BadSignature, SignatureExpired):
        return None


def login_required(f):
    def _():
        user_id_cookie = request.cookies.get("user_id")
        if not user_id_cookie:
            return None, None
        try:
            user_id = serializer.loads(user_id_cookie)
            return user_id, None
        except (BadSignature, SignatureExpired):
            response = make_response({"error": "用户未登录或登录状态过期"})
            response.delete_cookie("user_id")
            return None, response

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id, error_response = _()
        if error_response:
            return error_response

        if not user_id:
            response = make_response({"msg": "用户未登录"})
            response.delete_cookie("user_id")
            return response

        user = db.session.query(User).where(User.id == user_id).first()
        if not user:
            response = make_response({"error": "用户不存在"})
            response.delete_cookie("user_id")
            return response

        if user.state == UserStatus.Banned.value:
            response = make_response({"error": "用户状态异常"})
            response.delete_cookie("user_id")
            return response

        return f(*args, **kwargs)

    return decorated_function


@user_blueprint.route("/register", methods=["POST"])
def register_user():
    args = request.json
    username = args.get("username")
    if not username:
        return {"error": "必须填写用户名"}
    password = args.get("password")
    if not password:
        return {"error": "必须填写密码"}
    role = UserRole.User.value

    try:
        if db.session.query(User).where(User.username == username).count():
            return {"error": "该用户名已存在"}
        user = User(
            username=username,
            password=password,
            role=role,
        )
        information = Information(
            user=user,
        )
        db.session.add(user)
        db.session.add(information)
        db.session.commit()
        return {"msg": "注册成功", "user_id": user.id}
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500


@user_blueprint.route("/login", methods=["POST"])
def login():
    args = request.json
    username = args.get("username")
    if not username:
        return {"error": "必须填写用户名"}
    password = args.get("password")
    if not password:
        return {"error": "必须填写密码"}

    try:
        user = (
            db.session.query(User)
            .where(and_(User.username == username, User.password == password))
            .first()
        )
        if not user:
            return {"error": "用户名或密码填写错误"}
        if user.state == UserStatus.Banned.value:
            return {"error": "用户状态异常"}

        response = make_response({"msg": "登录成功", "user": user.json})

        encrypted_user_id = serializer.dumps(str(user.id))

        response.set_cookie(
            "user_id",
            encrypted_user_id,
            max_age=60 * 60 * 24 * 3,
            httponly=True,
            secure=True,
            samesite="None",
        )

        return response
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return {"error": str(e)}, 500


@user_blueprint.route("/logout", methods=["GET"])
def logout():
    response = make_response({"msg": "成功退出登录"})
    response.delete_cookie("user_id")
    return response


@user_blueprint.route("/test-login", methods=["GET"])
@login_required
def test_login():
    user_id = get_userid_from_cookie()
    user = db.session.query(User).where(User.id == user_id).first()
    return {"msg": "登录成功", "user": user.json}


def upload_file(filename: str, file: bytes):
    filepath = os.path.join("uploads", filename)

    with open(filepath, "wb") as f:
        f.write(file)

    filepath = os.path.join(backend_url, "download", filename)

    return filename, filepath, time.time()


@user_blueprint.route("/upload_avatar", methods=["POST"])
def upload_avatar():
    try:
        filename = request.headers.get("X-Filename", f"{int(time.time())}.png")

        content_type = request.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            return {"error": "只允许上传图片"}

        filename, filepath, upload_time = upload_file(filename, request.data)

        user_id = get_userid_from_cookie()
        if not user_id:
            return {"error": "user_id不能为空"}

        upload = (
            db.session.query(Upload).where(Upload.filepath == filepath).all()
        )
        if len(upload):
            upload[0].filename = filename
            upload[0].filepath = filepath
            upload[0].upload_time = time.time()

        else:
            db.session.add(
                Upload(
                    user_id=user_id,
                    filename=filename,
                    filepath=filepath,
                    filetype=FileType.Image.value,
                )
            )

        information = (
            db.session.query(Information)
            .where(Information.user_id == user_id)
            .all()
        )
        if len(information):
            information[0].avatar_path = filepath
        else:
            db.session.add(Information(user_id=user_id, avatar_path=filepath))

        db.session.commit()

        file_info = {
            "filename": filename,
            "filepath": filepath,
            "upload_time": time.time(),
        }

        return {
            "msg": "上传成功",
            "file_info": file_info,
            "user": db.session.query(User).where(User.id == user_id).first().json,
        }, 200
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500


@user_blueprint.route("/upload", methods=["POST"])
def upload():
    try:
        filename = request.headers.get("X-Filename", f"{int(time.time())}.png")

        content_type = request.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            return {"error": "只允许上传图片"}

        filename, filepath, upload_time = upload_file(filename, request.data)

        user_id = get_userid_from_cookie()
        if not user_id:
            return {"error": "user_id不能为空"}

        upload = (
            db.session.query(Upload).where(Upload.filepath == filepath).first()
        )
        if upload:
            upload.filename = filename
            upload.filepath = filepath
            upload.upload_time = time.time()

        else:
            upload = Upload(
                user_id=user_id,
                filename=filename,
                filepath=filepath,
                filetype=FileType.Image.value,
            )
            db.session.add(upload)

        db.session.commit()

        file_info = {
            "id": upload.id,
            "filename": filename,
            "filepath": filepath,
            "upload_time": time.time(),
        }

        return {
            "msg": "上传成功",
            "file_info": file_info,
            "user": db.session.query(User).where(User.id == user_id).first().json,
        }, 200
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500


@user_blueprint.route("/my-uploads")
def my_uploads():
    try:
        user_id = get_userid_from_cookie()
        if not user_id:
            return {"error": "user_id不能为空"}

        uploads = (
            db.session.query(Upload).where(Upload.user_id == user_id).all()
        )

        return {"msg": "获取成功", "uploads": [upload.json for upload in uploads]}
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500


@user_blueprint.route("/set-nickname", methods=["POST"])
@login_required
def set_nickname():
    try:
        nickname = request.json.get("nickname", None)
        if not nickname:
            return {"error": "必须填写昵称"}

        if len(nickname) > 64:
            return {"error": "昵称长度不能超过64"}

        user_id = request.json.get("user_id", None) or get_userid_from_cookie()
        if not user_id:
            return {"error": "user_id不能为空"}

        user = (
            db.session.query(Information)
            .where(Information.user_id == user_id)
            .first()
        )
        user.nickname = nickname
        db.session.commit()

        user = db.session.query(User).where(User.id == user_id).first()
        return {"msg": "昵称修改成功", "user": user.json}
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500


@user_blueprint.route("/set-position", methods=["POST"])
@login_required
def set_position():
    try:
        province = request.json.get("province", None)
        if not province:
            return ({"error": "必须填写省名称"},)

        city = request.json.get("city", None)
        if not city:
            return {"error": "必须填写市名称"}

        user_id = request.json.get("user_id", None) or get_userid_from_cookie()
        if not user_id:
            return {"error": "user_id不能为空"}

        user = (
            db.session.query(Information)
            .where(Information.user_id == user_id)
            .first()
        )
        user.position_province = province
        user.position_city = city
        db.session.commit()

        user = db.session.query(User).where(User.id == user_id).first()
        return {"msg": "昵称修改成功", "user": user.json}
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500


@user_blueprint.route("/information")
def get_user_information():
    user_id = request.args.get("user_id")
    if not user_id:
        user_id = get_userid_from_cookie()

    if not user_id:
        return {"error": "user_id不能为空"}

    log("INFO", f"获取信息 API，'user_id: '{user_id}")

    if is_redis_on():
        information = load(f"{user_id}@information")
        if information:
            log("INFO", f"从缓存中获取信息，information: {information}")
            return information

    user = db.session.query(User).where(User.id == user_id).first()

    if not user:
        return {"error": "用户不存在"}, 404

    information = (
        db.session.query(Information)
        .where(Information.user_id == user_id)
        .first()
    )

    if not information:
        return {"error": "用户信息不存在"}, 404

    subscribe_count = (
        db.session.query(Subscribe).where(Subscribe.user_id == user_id).count()
    )
    fans_count = (
        db.session.query(Subscribe)
        .where(Subscribe.subscribed_user_id == user_id)
        .count()
    )

    posts = db.session.query(Post).where(Post.user_id == user_id).all()

    result = {
        "information": information.json,
        "subscribe_count": subscribe_count,
        "fans_count": fans_count,
        "posts": [post.json for post in posts],
        "user": user.json,
    }

    if is_redis_on():
        log("INFO", f"将信息保存到缓存中，information: {result}")
        save(f"{user_id}@information", result, 10)

    log("INFO", f"获取信息 API，result: {result}")
    return result
