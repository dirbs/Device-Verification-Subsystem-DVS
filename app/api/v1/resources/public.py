import requests
from flask import request
from webargs.flaskparser import parser

from app import Root, GlobalConfig, version
from .common import CommonResources
from ..assets.error_handling import *
from ..assets.responses import responses, mime_types
from ..requests.status_request import basic_status_args


class BasicStatus:

    @staticmethod
    def get():
        try:
            args = parser.parse(basic_status_args, request)
            response = dict()
            tac = args['imei'][:GlobalConfig['TacLength']]  # slice TAC from IMEI
            if tac.isdigit():
                tac_response = requests.get('{}/{}/tac/{}'.format(Root, version, tac))  # dirbs core tac api call
                imei_response = requests.get('{}/{}/imei/{}?include_seen_with=1'.format(Root, version, args['imei']))  # dirbs core imei api call
                if tac_response.status_code == 200 and imei_response.status_code == 200:
                    tac_response = tac_response.json()
                    imei_response = imei_response.json()
                    basic_status = dict(tac_response, **imei_response)  # join api response
                else:
                    return custom_response("Connection error, Please try again later.", responses.get('timeout'), mime_types.get('json'))
                if basic_status['gsma']:  # TAC verification
                    response['imei'] = basic_status['imei_norm']
                    response['brand'] = basic_status['gsma']['brand_name']
                    response['model_name'] = basic_status['gsma']['model_name']
                    blocking_conditions = basic_status['classification_state']['blocking_conditions']
                    complain_status = CommonResources.get_complaince_status(blocking_conditions,
                                                                     basic_status['seen_with'])  # get compliance status
                    response = dict(response, **complain_status) if complain_status else response
                    return Response(json.dumps(response), status=responses.get('ok'), mimetype=mime_types.get('json'))
                else:
                    return custom_response("IMEI not found", responses.get('not_found'), mime_types.get('json'))
            else:
                return custom_response("Bad TAC format", responses.get('bad_request'), mime_types.get('json'))

        except ValueError as error:
            return custom_response(str(error), 422, mime_types.get('json'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving basic status.")
            app.logger.exception(e)
            return custom_response("Failed to retrieve basic status.", responses.get('service_unavailable'),
                                   mime_types.get('json'))
