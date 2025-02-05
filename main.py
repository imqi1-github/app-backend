import os
import subprocess

from app import app
from app.extensions import db
from app.models import User

if __name__ == '__main__':
    subprocess.call(["sh", "./migrate.sh"])
    with app.app_context():
        with db.session.begin():
            if not db.session.query(User).count() > 0:
                db.session.add(User(
                    username="admin",
                    password="123456",
                    email="example@email.com",
                    nickname="昵称",
                    role="admin",
                ))

    app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')
