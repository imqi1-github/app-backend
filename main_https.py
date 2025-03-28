import os
import subprocess

from sqlalchemy import text

from app import app
from app.extensions import db, log
from app.models import User, UserInformation

if __name__ == "__main__":
    with app.app_context():
        with db.session.begin():
            if not db.session.execute(text("show tables")).fetchall().__len__() > 0:
                db.create_all()
            if not db.session.query(User).count() > 0:
                user = User(
                    id=1,
                    username="admin",
                    password="123456",
                    role="admin",
                )
                db.session.add(user)
                db.session.add(
                    UserInformation(
                        user_id=1,
                        email="example@email.com",
                    )
                )
            else:
                subprocess.call(["sh", "./migrate.sh"])

    log("INFO", "服务器启动中...")
    app.run(
        ssl_context=("./https/localhost.pem", "./https/localhost-key.pem"),
        debug=True,
        port=os.getenv("PORT", default=5000),
        host="0.0.0.0",
    )
