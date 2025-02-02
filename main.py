import os

from core.app import app
from core.db import db_url, create_tables

if __name__ == '__main__':
    print(f"连接数据库的URL：{db_url}")
    create_tables()
    app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')
