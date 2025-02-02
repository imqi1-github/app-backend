import os

from core.app import app
from core.db import create_tables

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')
