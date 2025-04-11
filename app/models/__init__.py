from app.models.number import Number
from app.models.post import Post, Comment, Category, Relationship, Attachment, Subscribe
from app.models.user import User, UserInformation, UserUpload
from app.models.spot import Spot

models = [
    Number,
    User,
    UserInformation,
    UserUpload,
    Post,
    Comment,
    Category,
    Relationship,
    Attachment,
    Subscribe,
    Spot
]
