from app.models import Comment
from app.extensions import db
from app import app

with app.app_context():
    comments = Comment.query.all()
    for comment in comments:
        comment.content = comment.content.split("。")[0]

    db.session.commit()