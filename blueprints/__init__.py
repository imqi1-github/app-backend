from flask import Blueprint

number_blueprint = Blueprint('number', __name__)


@number_blueprint.route('/')
def index():
    return ''