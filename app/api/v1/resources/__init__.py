import requests
from flask_restful import Resource, Api
from app import app

api = Api(app, prefix='/api/v1')

class BasicStatus(Resource):
    def get(self, imei):
        json = requests.get('http://dirbs.pta.gov.pk/coreapi/api/v1/tac/{}'.format(imei))
        print(json.json())
        return json.json()

class FullStatus(Resource):
    def get(self, imei):
        return "inside /api/v1/fullstatus/{}".format(imei)


# noinspection PyTypeChecker
api.add_resource(BasicStatus, '/basicstatus/<int: imei>')
api.add_resource(FullStatus, '/fullstatus/<int: imei>')
