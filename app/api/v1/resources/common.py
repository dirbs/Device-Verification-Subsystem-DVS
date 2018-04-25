from flask_restful import Resource, Api
from app import app

api = Api(app, prefix='/api/v1')


@app.route('/')
def index_route():
    return 'Welcome to DVS'


class BaseRoutes(Resource):
    @staticmethod
    def get():
        return "inside /api/v1/"


# noinspection PyTypeChecker
api.add_resource(BaseRoutes, '/base')
