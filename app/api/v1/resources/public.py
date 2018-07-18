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
            response = dict({"imei": args['imei'], "compliance": {}, "gsma": {}})
            tac = args['imei'][:GlobalConfig['TacLength']]  # slice TAC from IMEI
            if tac.isdigit():
                status = CommonResources.get_status(imei=args.get('imei'), seen_with=1, tac=tac)
                basic_status = status.get('response')
                if basic_status:
                    print(basic_status)
                    if basic_status['gsma']:  # TAC verification
                        response = CommonResources.serialize(basic_status, "basic")
                        blocking_conditions = basic_status['classification_state']['blocking_conditions']
                        complain_status = CommonResources.get_complaince_status(blocking_conditions,
                                                                         basic_status['seen_with'])  # get compliance status
                        response = dict(response, **complain_status) if complain_status else response
                        return Response(json.dumps(response), status=responses.get('ok'), mimetype=mime_types.get('json'))
                    else:
                        return custom_response("IMEI not found", responses.get('not_found'), mime_types.get('json'))
                else:
                    return custom_response(basic_status.get('message'), basic_status.get('status'), mime_types.get('json'))
            else:
                return custom_response("Bad TAC format", responses.get('bad_request'), mime_types.get('json'))

        except ValueError as error:
            return custom_response(str(error), 422, mime_types.get('json'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving basic status.")
            app.logger.exception(e)
            return custom_response("Failed to retrieve basic status.", responses.get('service_unavailable'),
                                   mime_types.get('json'))
