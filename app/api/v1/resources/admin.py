import requests
from flask import request
from webargs.flaskparser import parser

from app import Root, BaseUrl, GlobalConfig, version
from .common import CommonResoures
from ..assets.error_handling import *
from ..assets.pagination import Pagination
from ..assets.responses import responses, mime_types
from ..requests.status_request import full_status_args


class FullStatus:

    @staticmethod
    def get():
        try:
            args = parser.parse(full_status_args, request)
            response = {}
            imei = args.get('imei')
            seen_with = args.get('seen_with', 0)
            tac = imei[:GlobalConfig['TacLength']]  # slice TAC from IMEI
            if tac.isdigit():
                tac_response = requests.get('{}/{}/tac/{}'.format(Root, version, tac))  # dirbs core TAC api call
                imei_response = requests.get('{}/{}/imei/{}?include_seen_with=1'.format(Root, version, imei))  # dirbs core IMEI api call with seen with information
                if tac_response.status_code == 200 and imei_response.status_code == 200:
                    tac_response = tac_response.json()
                    imei_response = imei_response.json()
                    full_status = dict(tac_response, **imei_response)
                else:
                    return custom_response("Server timeout, Please try again later.", responses.get('timeout'), mime_types.get('json'))
                if full_status['gsma']:  # TAC verification
                    response['imei'] = full_status['imei_norm']
                    response['brand'] = full_status['gsma']['brand_name']
                    response['model_name'] = full_status['gsma']['model_name']
                    response['model_number'] = full_status['gsma']['marketing_name']
                    response['device_type'] = full_status['gsma']['device_type']
                    response['manufacturer'] = full_status['gsma']['manufacturer']
                    response['operating_system'] = full_status['gsma']['operating_system']
                    response['radio_access_technology'] = full_status['gsma']['bands']
                    response['classification_state'] = full_status['classification_state']
                    blocking_conditions = full_status['classification_state']['blocking_conditions']
                    complain_status = CommonResoures.get_complaince_status(blocking_conditions, full_status.get(
                        'seen_with'))  # get compliance status
                    response = dict(response, **complain_status) if complain_status else response
                    if seen_with == 1:
                        response['associated_msisdn'] = full_status.get('seen_with')
                        response, status = Pagination.paginate(data=response, start=args.get('start', 1),
                                                               limit=args.get('limit', 2), imei=imei,
                                                               seen_with=seen_with, url='{}/fullstatus'.format(BaseUrl))
                        return Response(json.dumps(response), status=status,
                                        mimetype=mime_types.get('json'))

                    return Response(json.dumps(response), status=responses.get('ok'),
                                    mimetype=mime_types.get('json'))
                else:
                    return custom_response("IMEI not found", responses.get('not_found'),
                                           mimetype=mime_types.get('json'))
            else:
                return custom_response("Bad TAC format", responses.get('bad_request'), mime_types.get('json'))

        except ValueError as error:
            return custom_response(str(error), 422,
                                   mime_types.get('json'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving full status.")
            app.logger.exception(e)
            return custom_response("Failed to retrieve full status.", responses.get('service_unavailable'),
                                   mimetype=mime_types.get('json'))
