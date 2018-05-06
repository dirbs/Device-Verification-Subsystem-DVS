import requests
from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs
from app import config
from app.api.v1.assets.error_handling import *

dirbs = config.get("Development", "dirbs_core")

class BasicStatus(Resource):

    status_args = {
        "imei": fields.Str(Required=True)
    }

    @use_kwargs(status_args)
    def get(self, imei):
        try:
            print(imei)
            if len(imei) in range(8,16):
                tac = imei[:8]
                if isinstance(tac, int):
                    tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                    print(tac_response)
                    imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}'.format(imei)).json()
                    print(imei_response)
                    basic_status = dict(tac_response, **imei_response)
                    return basic_status
                else:
                    return bad_request()
            else:
                return bad_request()
        except Exception as e:
            print(e)

    @use_kwargs(status_args)
    def post(self, imei):
        try:
            if len(imei) in range(8,16):
                tac = imei[:8]
                if isinstance(tac, int):
                    tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                    print(tac_response)
                    imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}'.format(imei)).json()
                    print(imei_response)
                    basic_status = dict(tac_response, **imei_response)
                    return basic_status
                else:
                    return bad_request()
            else:
                return bad_request()
        except Exception as e:
            print(e)

class FullStatus(Resource):

    status_arg = {
        "imei": fields.Str(Required=True),
        "seen_with": fields.Int(Required=True)
    }

    @use_args(status_arg)
    def get(self, args):
        try:
            if len(args['imei']) in range(8,16):
                tac = args['imei'][:8]
                if isinstance(tac, int):
                    tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                    print(tac_response)
                    imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}'.format(args['imei'])).json()
                    print(imei_response)
                    full_status = dict(tac_response, **imei_response)
                    return full_status
                else:
                    return bad_request()
            else:
                return bad_request()
        except Exception as e:
            print(e)

    @use_kwargs(status_arg)
    def post(self, imei, seen_with):
        try:
            if len(imei) in range(8,16):
                tac = imei[:8]
                if isinstance(tac, int):
                    tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                    print(tac_response)
                    if seen_with==0:
                        imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}'.format(imei)).json()
                        print(imei_response)
                    else:
                        imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}?include_seen_with={}'.format(imei, seen_with)).json()
                        print(imei_response)
                    full_status = dict(tac_response, **imei_response)
                    return full_status
                else:
                    return bad_request()
            else:
                return bad_request()
        except Exception as e:
            print(e)