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
                             "subscribers": [], "stolen_status": [], "registration_status": []})
            imei = args.get('imei')
            tac = imei[:GlobalConfig['TacLength']]  # slice TAC from IMEI
            if tac.isdigit():
                status = CommonResources.get_status(imei=args.get('imei'), tac=tac)
                full_status = status.get('response')
                blocking_conditions = full_status['classification_state']['blocking_conditions']
                response = CommonResources.get_complaince_status(response, blocking_conditions,
                                                                 full_status['subscribers'],
                                                                 "full")  # get compliance status
                response['classification_state'] = full_status['classification_state']
                response['stolen_status'] = full_status.get('stolen_status')
                response['registration_status'] = full_status.get('registration_status')
                response['subscribers'] = full_status.get('subscribers')
                if len(full_status.get('subscribers')) > 0:
                    response = Pagination.paginate(data=response, start=args.get('start', 1),
                                                   limit=args.get('limit', 2), imei=imei,
                                                   url='{}/fullstatus'.format(BaseUrl))
                if full_status['gsma']:  # TAC verification
                        response = CommonResources.serialize(response, full_status, "full")
                        return Response(json.dumps(response), status=responses.get('ok'),
                                        mimetype=mime_types.get('json'))
                else:
                    return Response(json.dumps(response), status=responses.get('ok'), mimetype=mime_types.get('json'))
            else:
                return custom_response("Bad TAC format", responses.get('bad_request'), mime_types.get('json'))

        except ValueError as error:
            return custom_response(str(error), 422, mime_types.get('json'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving full status.")
            app.logger.exception(e)
            return custom_response("Failed to retrieve full status.", responses.get('service_unavailable'),
                                   mimetype=mime_types.get('json'))
