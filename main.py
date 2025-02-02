import os

from core.app import app

if __name__ == '__main__':
    app.run(port=os.getenv("PORT", default=5000))
