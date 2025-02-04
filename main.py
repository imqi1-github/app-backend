import os
import subprocess

from app import app

if __name__ == '__main__':
    subprocess.call(["sh", "./migrate.sh"])
    app.run(debug=True, port=os.getenv("PORT", default=5000), host='0.0.0.0')
