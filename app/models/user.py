import random
import string
import time

from app.constants import UserRole, UserStatus
from app.extensions import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    role = db.Column(db.String(8), default=UserRole.User)
    state = db.Column(db.String(10), default=UserStatus.Active.value)

    # 关系定义
    information = db.relationship("Information", back_populates="user", lazy=True)
    uploads = db.relationship("Upload", back_populates="user", lazy=True)
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
            "state": self.state,
            "information": self.information[0].json if len(self.information) else None,
            "uploads": [upload.json for upload in self.uploads],
        }

    def __getstate__(self):
        return self.json


class Information(db.Model):
    __tablename__ = "information"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    nickname = db.Column(
        db.String(32),
        default=lambda _: "用户昵称" + "".join(random.choices(string.ascii_lowercase, k=8)),
    )
    position_province = db.Column(db.String(32), default="河北省")
    position_city = db.Column(db.String(32), default="秦皇岛市")
    avatar_path = db.Column(db.String(128), default="/img/default_avatar.png")
    user = db.relationship("User", back_populates="information")

    def __repr__(self):
        return "<Information %r>" % self.id

    @property
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nickname": self.nickname,
            "position_province": self.position_province,
            "position_city": self.position_city,
            "avatar_path": self.avatar_path,
        }

    def __getstate__(self):
        return self.json


class Upload(db.Model):
    __tablename__ = "upload"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(64), nullable=False)
    filetype = db.Column(db.String(16), nullable=False)
    filepath = db.Column(db.String(128), nullable=False)
    upload_time = db.Column(db.Integer, nullable=False, default=time.time())
    comment = db.Column(db.String(24))
    user = db.relationship("User", back_populates="uploads")

    def __repr__(self):
        return "<Upload %r>" % self.filename

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
