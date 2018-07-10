import requests
from flask import request
from webargs.flaskparser import parser

from app import Root, BaseUrl, GlobalConfig, version
from .common import CommonResources
from ..assets.error_handling import *
from ..assets.pagination import Pagination
from ..assets.responses import responses, mime_types
from ..requests.status_request import full_status_args


class FullStatus:

    @staticmethod
    def get():
        try:
            args = parser.parse(full_status_args, request)
            response = dict({"imei": args['imei'], "compliance": {}, "gsma": {},
                             "subscribers": "N/A", "stolen_status": "N/A", "registration_status": "N/A"})
            imei = args.get('imei')
            tac = imei[:GlobalConfig['TacLength']]  # slice TAC from IMEI
            if tac.isdigit():
                tac_response = requests.get('{}/{}/tac/{}'.format(Root, version, tac))  # dirbs core TAC api call
                imei_response = requests.get('{}/{}/imei/{}?include_seen_with=1'.format(Root, version, imei))  # dirbs core IMEI api call with seen with information
                if tac_response.status_code == 200 and imei_response.status_code == 200:
                    tac_response = tac_response.json()
                    imei_response = imei_response.json()
                    full_status = dict(tac_response, **imei_response)
                else:
                    return custom_response("Connection error, Please try again later.", responses.get('timeout'), mime_types.get('json'))
                if full_status['gsma']:  # TAC verification
                    response['imei'] = full_status['imei_norm']
                    response['gsma']['brand'] = full_status['gsma']['brand_name']
                    response['gsma']['model_name'] = full_status['gsma']['model_name']
                    response['gsma']['model_number'] = full_status['gsma']['marketing_name']
                    response['gsma']['device_type'] = full_status['gsma']['device_type']
                    response['gsma']['manufacturer'] = full_status['gsma']['manufacturer']
                    response['gsma']['operating_system'] = full_status['gsma']['operating_system']
                    response['gsma']['radio_access_technology'] = full_status['gsma']['bands']
                    response['classification_state'] = full_status['classification_state']
                    blocking_conditions = full_status['classification_state']['blocking_conditions']
                    response = CommonResources.get_complaince_status(response,
                                                                     blocking_conditions,
                                                                     full_status.get('seen_with'), "full")  # get compliance status
                    response['associated_msisdn'] = full_status.get('seen_with')
                    if len(full_status.get('seen_with')) > 0:
                        response = Pagination.paginate(data=response, start=args.get('start', 1),
                                                       limit=args.get('limit', 2), imei=imei,
                                                       url='{}/fullstatus'.format(BaseUrl))
                        return Response(json.dumps(response), status=responses.get('ok'),
                                        mimetype=mime_types.get('json'))

                    return Response(json.dumps(response), status=responses.get('ok'),
                                    mimetype=mime_types.get('json'))
                else:
                    data = {
                        "imei": args['imei'],
                        "gsma": None,
                        "compliance": None,
                        "classification_state": None,
                        "seen_with": None,
                        "stolen_status": None,
                        "registration_status": None,
                        "subscribers": None

                    }
                    return Response(json.dumps(data), status=responses.get('ok'), mimetype=mime_types.get('json'))
            else:
                return custom_response("Bad TAC format", responses.get('bad_request'), mime_types.get('json'))

        except ValueError as error:
            return custom_response(str(error), 422, mime_types.get('json'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving full status.")
            app.logger.exception(e)
            return custom_response("Failed to retrieve full status.", responses.get('service_unavailable'),
                                   mimetype=mime_types.get('json'))
