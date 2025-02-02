import os

from core.app import app
from core.db import db_url

if __name__ == '__main__':
    print(f"连接数据库的URL：{db_url}")
    app.run(port=os.getenv("PORT", default=5000))