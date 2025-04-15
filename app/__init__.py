import logging
import os
from urllib.parse import unquote

from flask import Flask, render_template, send_file
from flask import send_from_directory, request
from flask_cors import CORS

from app.blueprints import (
    number_blueprint,
    user_blueprint,
    dashboard_blueprint,
    weather_blueprint,
    post_blueprint,
    map_blueprint,
    spot_blueprint,
)
from app.config import config
from app.extensions import db, migrate, log

app = Flask(__name__)

app.config.from_object("app.config.Config")
app.config["static_folder"] = os.path.join(app.root_path, "static")

UPLOAD_FOLDER = os.path.abspath("uploads")  # 转换为绝对路径
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 限制文件大小为 16MB

CORS(app, origins=config.frontend, supports_credentials=True)

db.init_app(app)
migrate.init_app(app, db)

# 日志相关
app.config["SQLALCHEMY_ECHO"] = False  # 禁用 SQLAlchemy 的 SQL 输出
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # 禁用跟踪修改警告
logging.getLogger("alembic").disabled = True
logging.getLogger("alembic.runtime.migration").disabled = (
    True  # 专门针对 migration 子记录器
)
logging.getLogger("werkzeug").disabled = True
logging.getLogger("sqlalchemy.engine").disabled = True
logging.getLogger("sqlalchemy").disabled = True

app.register_blueprint(number_blueprint, url_prefix="/number")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(dashboard_blueprint, url_prefix="/dashboard")
app.register_blueprint(weather_blueprint, url_prefix="/weather")
app.register_blueprint(post_blueprint, url_prefix="/post")
app.register_blueprint(map_blueprint, url_prefix="/map")
app.register_blueprint(spot_blueprint, url_prefix="/spot")


@app.route("/")
def hello_world():
    return render_template("index.html", title="毕设后端", frontend=config.frontend)


@app.route("/assets/<path:path>")
def assets(path):
    return send_file(os.path.join(app.static_folder, path))


@app.errorhandler(404)
def page_not_found(e):
    return "", 404


@app.errorhandler(405)
def method_not_allowed(e):
    return "", 405


@app.before_request
def before_request():
    referer = request.headers.get("Referer")
    if not referer:
        # return response
        return
    if not referer.startswith(config.frontend):
        return "", 403
    return




@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    filename = filename.replace(" ", "%20")
    # log("INFO", f"filename={filename}")
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename
    )
