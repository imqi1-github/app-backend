from flask import Flask, render_template
from flask_restx import Api

from blueprints import number_blueprint

app = Flask(__name__)
api = Api(app, doc='/docs')

app.register_blueprint(number_blueprint, url_prefix="/number")


@app.route('/')
def hello_world():
    return render_template("index.html")


# 自定义 CORS 头部，允许任何域访问
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # 允许任何域访问
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    response.headers[
        'Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


if __name__ == '__main__':
    app.run(debug=True)
