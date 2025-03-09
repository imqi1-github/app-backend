import time

from app.extensions import db
from app.constants import UserRole


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(64), default=UserRole.User)
    information = db.relationship("UserInformation", lazy=True)  # 关系字段

    def __repr__(self):
        return "<User %r>" % self.username

    @property
    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "role": self.role,
            "information": [info.json for info in self.information],
        }

    def __getstate__(self):
        return self.json


class UserInformation(db.Model):
    __tablename__ = "user_information"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # 定义外键
    email = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    position_province = db.Column(db.String(32))
    position_city = db.Column(db.String(32))
    avatar_path = db.Column(db.String(512))

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
        }

    def __getstate__(self):
        return self.json
