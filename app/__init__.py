from flask import Flask, render_template, request

from app.blueprints import number_blueprint, user_blueprint
from app.config import config
from app.extensions import db, migrate

app = Flask(__name__)

app.config.from_object("app.config.Config")

db.init_app(app)
migrate.init_app(app, db)
app.register_blueprint(number_blueprint, url_prefix="/number")
app.register_blueprint(user_blueprint, url_prefix="/user")


@app.route("/")
def hello_world():
    return render_template("index.html", title="毕设后端")


@app.errorhandler(404)
def page_not_found(e):
    return "", 404


@app.errorhandler(405)
def method_not_allowed(e):
    return "", 405


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = config.frontend
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.before_request
def before_request():
    referer = request.headers.get("Referer")
    if not referer:
        # return response
        return
    if not referer.startswith(config.frontend):
        return "", 403
    return
