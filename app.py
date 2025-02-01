from flask import Flask, render_template
from flask_restx import Api

import blueprints

app = Flask(__name__)
api = Api(app, doc='/docs')

app.register_blueprint(blueprints.number_blueprint, url_prefix="/number")


@app.route('/')
def hello_world():
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
