import requests
import json
from flask import Response
from webargs.flaskparser import use_args
from app import Root
from ..assets.error_handling import *
from ..requests.status_request import status_args
from .common import CommonResoures

resource = CommonResoures()

class BasicStatus():

    @use_args(status_args)
    def get(self, args):
        try:
            response = {}
            tac = args['imei'][:8] # slice TAC from IMEI
            if tac.isdigit(): # TAC format validation
                tac_response = requests.get('{}/coreapi/api/v1/tac/{}'.format(Root, tac)).json() # dirbs core tac api call
                imei_response = requests.get('{}/coreapi/api/v1/imei/{}'.format(Root, args['imei'])).json() # dirbs core imei api call
                basic_status = dict(tac_response, **imei_response) # join api response
                if basic_status['gsma']: # TAC verification
                    response['imei'] = basic_status['imei_norm']
                    response['brand'] = basic_status['gsma']['brand_name']
                    response['model_name'] = basic_status['gsma']['model_name']
                    blocking_conditions = basic_status['classification_state']['blocking_conditions']
                    complain_status = resource.get_complaince_status(blocking_conditions) # get compliance status
                    response = dict(response, **complain_status) if complain_status else response
                    return Response(json.dumps(response), status=200, mimetype='application/json')
                else:
                    return custom_response("IMEI not found", 404, 'application/json')
            else:
                return custom_response("Bad TAC format", 400, 'application/json')
        except Exception as e:
            print(e)
