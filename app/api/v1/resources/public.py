import requests
import json
from flask import Response
from webargs.flaskparser import use_args
from app import Root, GlobalConfig, version
from ..assets.error_handling import *
from ..requests.status_request import basic_status_args
from .common import CommonResoures

resource = CommonResoures()


class BasicStatus():

    @use_args(basic_status_args)
    def get(self, args):
        try:
            response = dict()
            tac = args['imei'][:GlobalConfig['TacLength']] # slice TAC from IMEI
            if tac.isdigit():  # TAC format validation
                tac_response = requests.get('{}/{}/tac/{}'.format(Root, version, tac)).json()  # dirbs core tac api call
                imei_response = requests.get('{}/{}/imei/{}?include_seen_with=1'.format(Root, version, args['imei'])).json() # dirbs core imei api call
                basic_status = dict(tac_response, **imei_response)  # join api response
                if basic_status['gsma']: # TAC verification
                    response['imei'] = basic_status['imei_norm']
                    response['brand'] = basic_status['gsma']['brand_name']
                    response['model_name'] = basic_status['gsma']['model_name']
                    blocking_conditions = basic_status['classification_state']['blocking_conditions']
                    complain_status = resource.get_complaince_status(blocking_conditions, basic_status['seen_with'])  # get compliance status
                    response = dict(response, **complain_status) if complain_status else response
                    return Response(json.dumps(response), status=200, mimetype='application/json')
                else:
                    return custom_response("IMEI not found", 404, 'application/json')
            else:
                return custom_response("Bad TAC format", 400, 'application/json')
        except Exception as e:
            app.logger.info("Error occurred while retrieving basic status.")
            app.logger.exception(e)
            return custom_response("Failed to retrieve basic status.", 503, 'application/json')
