import math
import mimetypes
import os
import random
import time
import traceback

from flask import Blueprint, request, jsonify
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from sqlalchemy import and_

from app.extensions import db, log
from app.models.post import Post, Category, Subscribe, Comment, Attachment
from app.models.user import User
from app.config import backend_url
from app.models import UserUpload

post_blueprint = Blueprint("post", __name__, url_prefix="/post")

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


@post_blueprint.route("/list")
def post_list():
    try:
        # 获取查询参数
        page = request.args.get("page", 1, type=int)  # 默认第 1 页
        category_id = request.args.get("category_id", None, type=int)
        per_page = 24  # 固定每次返回 24 个帖子
        new_post_ratio = float(
            request.args.get("new_post_ratio", 0.7)
        )  # 默认 70% 较新帖子

        # 确保 new_post_ratio 在 0 到 1 之间
        new_post_ratio = max(0.0, min(1.0, new_post_ratio))

        # 计算较新和较旧帖子的数量
        new_post_count = math.ceil(per_page * new_post_ratio)  # 向上取整
        old_post_count = per_page - new_post_count  # 剩余数量

        # 查询所有帖子 ID 和创建时间
        query = db.session.query(Post.id, Post.create_time)

        # 如果提供了 category_id，则筛选属于该分类的帖子
        if category_id is not None:
            query = query.join(Post.categories).filter(Category.id == category_id)

        posts_data = query.all()

        if not posts_data:
            return (
                jsonify(
                    {
                        "code": 200,
                        "msg": "暂无帖子",
                        "data": {
                            "posts": [],
                            "total": 0,
                            "page": page,
                            "per_page": per_page,
                            "total_pages": 0,
                        },
                    }
                ),
                200,
            )

        # 提取 ID 和 create_time
        post_ids = [post[0] for post in posts_data]
        create_times = [post[1] for post in posts_data]

        # 计算 create_time 的中位数，用于划分“较新”和“较旧”
        sorted_create_times = sorted(create_times)
        median_index = len(sorted_create_times) // 2
        median_create_time = sorted_create_times[median_index]

        # 划分“较新”和“较旧”帖子 ID
        new_post_ids = []
        old_post_ids = []
        for pid, create_time in zip(post_ids, create_times):
            if create_time > median_create_time:
                new_post_ids.append(pid)
            else:
                old_post_ids.append(pid)

        # 随机抽取帖子 ID
        selected_new_ids = (
            random.sample(new_post_ids, min(new_post_count, len(new_post_ids)))
            if new_post_ids
            else []
        )
        selected_old_ids = (
            random.sample(old_post_ids, min(old_post_count, len(old_post_ids)))
            if old_post_ids
            else []
        )

        # 如果数量不足，调整抽取
        if len(selected_new_ids) < new_post_count and old_post_ids:
            # 从旧帖子中补充
            remaining_count = new_post_count - len(selected_new_ids)
            remaining_old_ids = [
                pid for pid in old_post_ids if pid not in selected_old_ids
            ]
            selected_new_ids.extend(
                random.sample(
                    remaining_old_ids, min(remaining_count, len(remaining_old_ids))
                )
            )
        elif len(selected_old_ids) < old_post_count and new_post_ids:
            # 从新帖子中补充
            remaining_count = old_post_count - len(selected_old_ids)
            remaining_new_ids = [
                pid for pid in new_post_ids if pid not in selected_new_ids
            ]
            selected_old_ids.extend(
                random.sample(
                    remaining_new_ids, min(remaining_count, len(remaining_new_ids))
                )
            )

        # 合并选中的帖子 ID
        selected_ids = selected_new_ids + selected_old_ids

        # 随机打乱最终列表
        random.shuffle(selected_ids)

        # 查询选中的帖子
        selected_posts = Post.query.filter(Post.id.in_(selected_ids)).all()

        # 按 selected_ids 的顺序排序（可选，如果需要保持随机顺序）
        selected_posts_dict = {post.id: post for post in selected_posts}
        ordered_posts = [
            selected_posts_dict[pid]
            for pid in selected_ids
            if pid in selected_posts_dict
        ]

        # 构造响应数据
        total_posts = len(post_ids)
        response = {
            "posts": [post.json for post in ordered_posts],
            "total": total_posts,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_posts + per_page - 1) // per_page,
        }

        return (
            jsonify({"code": 200, "msg": "成功获取加权随机帖子列表", "data": response}),
            200,
        )

    except Exception as e:
        return (
            jsonify({"code": 500, "msg": f"获取加权随机帖子列表失败：{str(e)}"}),
            500,
        )


@post_blueprint.route("/<int:post_id>")
def get_post(post_id):
    if post_id is None:
        return {"error": "post_id不能为空"}, 400

    post = db.session.query(Post).where(Post.id == post_id).first()
    if post is None:
        return {"error": "帖子不存在"}, 404
    subscribe = (
        db.session.query(Subscribe)
        .filter(
            Subscribe.user_id == get_userid_from_cookie(),
            Subscribe.subscribed_user_id == post.user_id,
        )
        .first()
    )

    return {**post.json, "subscribed": subscribe is not None}


@post_blueprint.route("/categories")
def get_categories():
    categories = db.session.query(Category).all()
    return jsonify(
        {
            "code": 200,
            "msg": "成功获取所有分类",
            "data": [category.json for category in categories],
        }
    )


@post_blueprint.route("/like/<int:post_id>")
def like_post(post_id):
    if post_id is None:
        return {"error": "post_id不能为空"}, 400
    post = db.session.query(Post).where(Post.id == post_id).first()
    if post is None:
        return {"error": "帖子不存在"}, 404
    post.likes += 1
    db.session.commit()
    return {"msg": "成功喜欢该帖子。"}


@post_blueprint.route("/subscribe", methods=["POST"])
def subscribe():
    user_id = request.json.get("user_id", None)
    subscribed_user_id = request.json.get("subscribed_user_id", None)
    if user_id is None or subscribed_user_id is None:
        return {"error": "user_id或subscribed_user_id不能为空"}, 400
    if user_id == subscribed_user_id:
        return {"error": "不能关注自己"}, 400

    user1 = db.session.query(User).where(User.id == user_id).first()

    if not user1:
        return {"error": "用户不存在"}, 404

    user2 = db.session.query(User).where(User.id == subscribed_user_id).first()

    if not user2:
        return {"error": "用户不存在"}, 404

    result = (
        db.session.query(Subscribe)
        .where(
            and_(
                Subscribe.user_id == user_id,
                Subscribe.subscribed_user_id == subscribed_user_id,
            )
        )
        .first()
    )
    if result is not None:
        db.session.delete(result)
        db.session.commit()
        return {"msg": "取消关注成功"}, 200
    else:
        new_subscribe = Subscribe(
            user_id=user_id, subscribed_user_id=subscribed_user_id
        )
        db.session.add(new_subscribe)
        db.session.commit()
        return {"msg": "关注成功"}, 200


@post_blueprint.route("/comment", methods=["GET", "POST"])
def comment_post():
    try:
        data = request.json
        if data.get("post_id") is None:
            return {"error": "post_id不能为空"}, 400

        if data.get("user_id") is None:
            return {"error": "user_id不能为空"}, 400

        if data.get("content") is None or len(data.get("content")) == 0:
            return {"error": "评论内容不能为空"}, 400

        comment = Comment(
            user_id=data.get("user_id"),
            post_id=data.get("post_id"),
            content=data.get("content"),
            parent_id=data.get("parent_id", None),
        )

        db.session.add(comment)
        db.session.commit()
        return {"msg": "评论成功"}
    except Exception as e:
        db.session.rollback()
        log("ERROR", f"评论帖子时出错：{str(e)}")
        return {"error": str(e)}, 500


@post_blueprint.route("/comments/<int:post_id>")
def comments(post_id):
    if post_id is None:
        return {"error": "post_id不能为空"}, 400
    return {
        "comments": db.session.query(Post)
        .where(Post.id == post_id)
        .first()
        .json.get("comments")
    }


@post_blueprint.route("/new", methods=["POST"])
def new_post():
    try:
        data = request.json

        user_id = data.get("user_id")
        if not user_id:
            return {"error": "user_id不能为空"}, 400

        title = data.get("title")
        if not title:
            return {"error": "标题不能为空"}, 400

        content = data.get("content")
        if not content:
            return {"error": "内容不能为空"}, 400

        post = Post(
            user_id=user_id,
            title=title,
            content=content,
        )

        attachments = data.get("attachments", [])
        for attachment in attachments:
            post.attachments.append(Attachment(
                post_id=post.id,
                file_name = attachment.get('filename'),
                file_path = attachment.get('filepath'),
                file_type="image/png"
            ))

        categories = data.get("categories", [])
        for category in categories:
            post.categories.append(
                Category.query.filter_by(id=category).first()
            )

        db.session.add(post)
        db.session.commit()
        return {"msg": "发布成功", 'id': post.id}
    except Exception as e:
        db.session.rollback()
        log("ERROR", f"发布帖子时出错：{str(e)}")
        traceback.print_exc()
        return {"error": str(e)}, 500


@post_blueprint.route("/upload_attachment", methods=["POST"])
def upload_attachment():
    try:
        filename = request.headers.get(
            "X-Filename", f"{int(time.time())}.png"
        )  # 生成默认文件名
        filepath = os.path.join("uploads", filename)

        content_type = request.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            return {"error": "只允许上传图片"}, 400

        with open(filepath, "wb") as f:
            f.write(request.data)

        filepath = os.path.join(backend_url, "download", filename)

        user_id = get_userid_from_cookie()
        if not user_id:
            return {"error": "user_id不能为空"}, 400

        upload = UserUpload(
            user_id=user_id,
            filename=filename,
            filepath=filepath,
            filetype=mimetypes.guess_type(filename)[0],
            comment="文章附件",
        )

        db.session.add(upload)
        db.session.commit()

        return {
            "msg": "上传成功",
            "id": upload.id,
            "filename": filename,
            "filepath": filepath,
        }, 200
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return {"error": str(e)}, 500


@post_blueprint.route("/attachment/delete")
def delete_attachment():
    try:
        upload_id = request.args.get("id")
        if not upload_id:
            return {"error": "upload_id不能为空"}, 400
        upload = db.session.query(UserUpload).where(UserUpload.id == upload_id).first()
        if upload:
            db.session.delete(upload)
        return {"msg": "删除成功"}
    except Exception as e:
        db.session.rollback()
        log("ERROR", f"删除附件时出现错误：{str(e)}")
        return {"error": str(e)}, 500


@post_blueprint.route("/delete")
def delete_post():
    try:
        post_id = request.args.get("id")
        if not post_id:
            return {"error": "post_id不能为空"}, 400
        post = db.session.query(Post).where(Post.id == post_id).first()
        if post:
            db.session.delete(post)
        return {"msg": "删除成功"}
    except Exception as e:
        db.session.rollback()
        log("ERROR", f"删除帖子时出现错误：{str(e)}")


@post_blueprint.route("/subscribed")
def get_subscribed():
    user_id = request.args.get("user_id")

    if not user_id:
        return {"error": "user_id不能为空"}

    subscribed_user_id = request.args.get("subscribed_user_id")

    if not subscribed_user_id:
        return {"error": "subscribed_user_id"}

    return {"subscribed": len(db.session.query(Subscribe).where(and_(Subscribe.user_id == user_id, subscribed_user_id == Subscribe.subscribed_user_id)).all())}