from flask import Flask, render_template, request, Response

from app.blueprints import number_blueprint
from app.config import config
from app.extensions import db, migrate

app = Flask(__name__)

# 加载配置
app.config.from_object("app.config.Config")

db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(number_blueprint, url_prefix='/number')


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # 允许任何域访问
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.before_request
def before_request():
    referer = request.headers.get('Referer')

    print(f"Referer: {referer}")

    if referer is None:
        return

    if not referer.startswith(config.frontend):
        return render_template("403.html"), 403
