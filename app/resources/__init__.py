from flask import Blueprint
from flask_restful import Api

from app.resources.search import YutifySearch

bp = Blueprint("api", __name__)
api = Api(bp)

api.add_resource(YutifySearch, "/search/<path:artist>:<path:song>")
