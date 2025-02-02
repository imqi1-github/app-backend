from app.extensions import db


class Number(db.Model):
    __tablename__ = 'number'
    number = db.Column(db.Integer, primary_key=True, autoincrement=False)

    def __repr__(self):
        return f'<Number {self.number}>'
