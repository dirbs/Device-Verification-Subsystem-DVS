from flask_restful import Resource
from app import app

@app.route('/')
def index_route():
    return 'Welcome to DVS'


class BaseRoutes(Resource):
    @staticmethod
    def get():
        return "inside /api/v1/"
