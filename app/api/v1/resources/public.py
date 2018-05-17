import requests
import json
from flask import jsonify, Response
from webargs.flaskparser import use_args
from app import config
from ..assets.error_handling import *
from ..requests.status_request import status_args
from .common import CommonResoures

dirbs = config.get("Development", "dirbs_core")
resource = CommonResoures()

class BasicStatus():

    @use_args(status_args)
    def get(self, args):
        try:
            response = {}
            if len(args['imei']) in range(14,16):
                tac = args['imei'][:8]
                if tac.isdigit():
                    tac_response = requests.get(dirbs+'/coreapi/api/v1/tac/{}'.format(tac)).json()
                    imei_response = requests.get(dirbs+'/coreapi/api/v1/imei/{}'.format(args['imei'])).json()
                    basic_status = dict(tac_response, **imei_response)
                    if basic_status['gsma']:
                        response['imei'] = basic_status['imei_norm']
                        response['brand'] = basic_status['gsma']['brand_name']
                        response['model_name'] = basic_status['gsma']['model_name']
                        blocking_conditions = basic_status['classification_state']['blocking_conditions']
                        complain_status = resource.get_complaince_status(blocking_conditions)
                        response = dict(response, **complain_status) if complain_status else response
                        return Response(json.dumps(response), status=200, mimetype='application/json')
                    else:
                        return custom_error_handeling("IMEI not found", 404, 'application/json')
                else:
                    return custom_error_handeling("Bad TAC format", 400, 'application/json')
            else:
                return custom_error_handeling("Bad IMEI format", 400, 'application/json')
        except Exception as e:
            print(e)
