from flask import request
from webargs.flaskparser import parser

from app import GlobalConfig
from .common import CommonResources
from ..assets.error_handling import *
from ..assets.responses import responses, mime_types
from ..requests.status_request import basic_status_args


class BasicStatus:

    @staticmethod
    def get():
        try:
            args = parser.parse(basic_status_args, request)
            tac = args['imei'][:GlobalConfig['TacLength']]  # slice TAC from IMEI
            status = CommonResources.get_imei(imei=args.get('imei'))  # get imei response
            compliance = CommonResources.compliance_status(status, "basic")  # get compliance status
            gsma = CommonResources.get_tac(tac, "basic")  # get gsma data from tac
            response = dict(compliance, **gsma, **{'imei': status.get('imei_norm')})  # merge responses
            return Response(json.dumps(response), status=responses.get('ok'), mimetype=mime_types.get('json'))
        except ValueError as error:
            return custom_response(str(error), 422, mime_types.get('json'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving basic status.")
            app.logger.exception(e)
            return custom_response("Failed to retrieve basic status.", responses.get('service_unavailable'),
                                   mime_types.get('json'))
