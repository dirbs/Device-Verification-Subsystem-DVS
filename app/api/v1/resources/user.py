import requests
from flask_restful import Resource
from app import config
from app.api.v1.assets.error_handling import *

dirbs = config.get("Development", "dirbs_core")

class BasicStatus(Resource):
    def get(self, imei):
        try:
            if len(str(imei)) in range(14,17) and isinstance(imei, int):
                tac = int(str(imei)[:8])
                tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}?include_seen_with=0'.format(imei)).json()
                basic_status = dict(tac_response, **imei_response)
                return basic_status
            else:
                return bad_request()
        except Exception as e:
            print(e)

    def post(self, imei):
        try:
            if len(str(imei)) in range(14,17) and isinstance(imei, int):
                tac = int(str(imei)[:8])
                tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}?include_seen_with=0'.format(imei)).json()
                basic_status = dict(tac_response, **imei_response)
                return basic_status
            else:
                return bad_request()
        except Exception as e:
            print(e)

class FullStatus(Resource):
    def get(self, imei):
        try:
            if len(str(imei))in range(14,17) and isinstance(imei, int):
                tac = int(str(imei)[:8])
                tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}?include_seen_with=1'.format(imei)).json()
                full_status = dict(tac_response, **imei_response)
                return full_status
            else:
                return bad_request()
        except Exception as e:
            print(e)

    def post(self, imei):
        try:
            if len(str(imei)) in range(14,17) and isinstance(imei, int):
                tac = int(str(imei)[:8])
                tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}?include_seen_with=1'.format(imei)).json()
                full_status = dict(tac_response, **imei_response)
                return full_status
            else:
                return bad_request()
        except Exception as e:
            print(e)