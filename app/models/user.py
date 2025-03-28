import random
import string
import time

from app.extensions import db
from app.constants import UserRole


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(64), default=UserRole.User)

    # 关系定义
    information = db.relationship("UserInformation", back_populates="user", lazy=True)
    uploads = db.relationship("UserUpload", back_populates="user", lazy=True)
    posts = db.relationship("Post", back_populates="user", lazy=True)
    comments = db.relationship("Comment", back_populates="user", lazy=True)  # 新增 comments 关系

    def __repr__(self):
        return "<User %r>" % self.username

    @property
    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "information": self.information[0].json if len(self.information) else None,
            "uploads": [upload.json for upload in self.uploads],
        }

    def __getstate__(self):
        return self.json


class UserInformation(db.Model):
    __tablename__ = "user_information"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    email = db.Column(db.String(64), default="你还未输入你的邮箱")
    nickname = db.Column(
        db.String(64),
        default="用户昵称" + "".join(random.choices(string.ascii_lowercase, k=8)),
    )
    position_province = db.Column(db.String(32), default="河北省")
    position_city = db.Column(db.String(32), default="秦皇岛市")
    avatar_path = db.Column(db.String(512), default="/img/default_avatar.png")
    user = db.relationship("User", back_populates="information")

    def __repr__(self):
        return "<UserInformation %r>" % self.id

    @property
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.email,
            "nickname": self.nickname,
            "position_province": self.position_province,
            "position_city": self.position_city,
            "avatar_path": self.avatar_path,
        }

    def __getstate__(self):
        return self.json


class UserUpload(db.Model):
    __tablename__ = "user_upload"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    filetype = db.Column(db.String(16), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    upload_time = db.Column(db.Integer, nullable=False, default=time.time())
    comment = db.Column(db.String(256))
    user = db.relationship("User", back_populates="uploads")

    def __repr__(self):
        return "<UserUpload %r>" % self.filename

    @property
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "filetype": self.filetype,
            "filepath": self.filepath,
            "upload_time": self.upload_time,
            "comment": self.comment,
        }

    def __getstate__(self):
        return self.json
