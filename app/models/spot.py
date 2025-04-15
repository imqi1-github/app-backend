from app.extensions import db


class Spot(db.Model):
    __tablename__ = "spot"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    good = db.Column(db.Integer, default=0)
    bad = db.Column(db.Integer, default=0)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    position = db.Column(db.String(32))
    province = db.Column(db.String(16))
    city = db.Column(db.String(16))
    place = db.Column(db.String(16))
    coordinates = db.Column(db.String(32))
    pictures = db.Column(db.String(1024))
    views = db.Column(db.Integer, default=0)
    content = db.Column(db.Text)

    def __repr__(self):
        return "<Spot %r>" % self.title

    @property
    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "good": self.good,
            "bad": self.bad,
            "start_time": self.start_time.strftime("%H:%M"),
            "end_time": self.end_time.strftime("%H:%M"),
            "position": self.position,
            "province": self.province,
            "city": self.city,
            "place": self.place,
            "coordinates": self.coordinates,
            "pictures": self.pictures.split(","),
            "views": self.views,
            "content": self.content,
        }
