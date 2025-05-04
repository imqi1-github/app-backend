import time

from app.extensions import db


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(
        db.Integer, nullable=False, default=lambda: int(time.time())
    )
    update_time = db.Column(
        db.Integer, nullable=False, default=lambda: int(time.time())
    )
    likes = db.Column(db.Integer, default=0)
    coordinates = db.Column(db.String(24))
    position_name = db.Column(db.String(32))
    user = db.relationship("User", back_populates="posts")
    comments = db.relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    published = db.Column(db.Integer, default=1)
    categories = db.relationship(
        "Category", secondary="relationship", back_populates="posts"
    )
    attachments = db.relationship(
        "Attachment", back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Post {self.title}>"

    def __eq__(self, other):
        return isinstance(other, Post) and other.id == self.id

    def __hash__(self):
        return hash(self.id)

    @property
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "create_time": self.create_time,
            "update_time": self.update_time,
            "likes": self.likes,
            "user": self.user.json,
            "published": self.published,
            "coordinates": self.coordinates,
            "position_name": self.position_name,
            "categories": [category.json for category in self.categories],
            "comments": [comment.json for comment in self.comments],
            "attachments": [
                attachment.json for attachment in self.attachments
            ],  # 新增：包含附件
        }


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(
        db.Integer, nullable=False, default=lambda: int(time.time())
    )

    # 关系定义
    post = db.relationship("Post", back_populates="comments")
    parent = db.relationship("Comment", remote_side=[id], back_populates="children")
    children = db.relationship("Comment", back_populates="parent")
    user = db.relationship("User", back_populates="comments")  # 新增 user 关系

    def __repr__(self) -> str:
        return f"<Comment {self.content}>"

    @property
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "parent_id": self.parent_id,
            "content": self.content,
            "create_time": self.create_time,
            "children": [child.json for child in self.children],
            "user": self.user.json if self.user else None,  # 确保 user 可选
        }


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    description = db.Column(db.String(64))
    posts = db.relationship(
        "Post", secondary="relationship", back_populates="categories"
    )

    def __repr__(self) -> str:
        return f"<Category {self.name}>"

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


class Relationship(db.Model):
    __tablename__ = "relationship"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<Relationship {self.category_id} {self.post_id}>"

    @property
    def json(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "post_id": self.post_id,
        }


class Attachment(db.Model):
    __tablename__ = "attachment"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    file_name = db.Column(db.String(64), nullable=False)
    file_path = db.Column(db.String(128), nullable=False)
    file_type = db.Column(db.String(16), nullable=False)
    create_time = db.Column(
        db.Integer, nullable=False, default=lambda: int(time.time())
    )
    # 新增：与 Post 的多对一关系
    post = db.relationship("Post", back_populates="attachments")

    def __repr__(self) -> str:
        return f"<Attachment {self.file_name}>"

    @property
    def json(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "create_time": self.create_time,
        }


class Subscribe(db.Model):
    __tablename__ = "subscribe"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    subscribed_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<Subscribe {self.user_id} {self.subscribed_user_id}>"

    @property
    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscribed_user_id": self.subscribed_user_id,
        }
