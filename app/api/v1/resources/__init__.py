import requests, json
from flask_restful import Resource, Api
from app import app

api = Api(app, prefix='/api/v1')

class BasicStatus(Resource):
    def get(self, imei):
        if len(str(imei))==15 and isinstance(imei, int):
            tac = int(str(imei)[:8])
            tac_response = requests.get('http://dirbs.pta.gov.pk/coreapi/api/v1/tac/{}'.format(tac)).json()
            imei_response = requests.get('http://dirbs.pta.gov.pk/coreapi/api/v1/imei/{}?include_seen_with=0'.format(imei)).json()
            basic_status = dict(tac_response, **imei_response)
            return basic_status
        else:
            return json.dumps({"message":"Bad IMEI format"}), 400

class FullStatus(Resource):
    def get(self, imei):
        if len(str(imei))==15 and isinstance(imei, int):
            tac = int(str(imei)[:8])
            tac_response = requests.get('http://dirbs.pta.gov.pk/coreapi/api/v1/tac/{}'.format(tac)).json()
            imei_response = requests.get('http://dirbs.pta.gov.pk/coreapi/api/v1/imei/{}?include_seen_with=1'.format(imei)).json()
            full_status = dict(tac_response, **imei_response)
            return full_status
        else:
            return json.dumps({"message":"Bad IMEI format"}), 400


api.add_resource(BasicStatus, '/basicstatus/<int:imei>')
api.add_resource(FullStatus, '/fullstatus/<int:imei>')
