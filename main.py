import os

from app import app
from app.extensions import db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("尝试创建数据库")
    app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')
