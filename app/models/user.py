from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    nickname = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'nickname': self.nickname,
            'role': self.role,
        }
