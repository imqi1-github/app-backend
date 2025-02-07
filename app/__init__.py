import os

from flask import Flask, render_template, request, send_file
from flask_cors import CORS

from app.blueprints import number_blueprint, user_blueprint
from app.blueprints.dashboard import dashboard_blueprint
from app.config import config
from app.extensions import db, migrate

app = Flask(__name__)

app.config.from_object("app.config.Config")
app.config["static_folder"] = os.path.join(app.root_path, "static")

CORS(app, origins=config.frontend, supports_credentials=True)

db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(number_blueprint, url_prefix="/number")
app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(dashboard_blueprint, url_prefix="/dashboard")


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
