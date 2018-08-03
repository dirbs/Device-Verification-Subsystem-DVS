from flask import request
from webargs.flaskparser import parser

from app import GlobalConfig
from .common import CommonResources
from ..assets.error_handling import *
from ..assets.responses import responses, mime_types
from ..requests.status_request import full_status_args


class FullStatus:

    @staticmethod
    def get():
        try:
            response = dict()
            args = parser.parse(full_status_args, request)
            imei = args.get('imei')
            tac = imei[:GlobalConfig['TacLength']]  # slice TAC from IMEI
            paginate_sub = args.get('subscribers')
            paginate_pairs = args.get('pairs')
            status = CommonResources.get_imei(imei=args.get('imei'))  # get imei response from core
            gsma = CommonResources.get_tac(tac, "full")  # get gsma data from tac
            blocking_conditions = status['classification_state']['blocking_conditions']
            subscribers = CommonResources.subscribers(status.get('imei_norm'), paginate_sub.get('start', 1), paginate_sub.get('limit', 10))  # get subscribers data
            pairings = CommonResources.pairings(status.get('imei_norm'), paginate_pairs.get('start', 1), paginate_pairs.get('limit', 10))  # get pairing data
            response['imei'] = status.get('imei_norm')
            response['classification_state'] = status['classification_state']
            response['registration_status'] = CommonResources.get_status(status['registration_status'], "registration")
            response['stolen_status'] = CommonResources.get_status(status['stolen_status'], "stolen")
            compliance = CommonResources.compliance_status(status, "full")  # get compliance status
            response = dict(response, **gsma, **subscribers, **pairings, **compliance)
            return Response(json.dumps(response), status=responses.get('ok'), mimetype=mime_types.get('json'))

        except ValueError as error:
            return custom_response(str(error), 422, mime_types.get('json'))

        except Exception as e:
            app.logger.info("Error occurred while retrieving full status.")
            app.logger.exception(e)
            return custom_response("Failed to retrieve full status.", responses.get('service_unavailable'),
                                   mimetype=mime_types.get('json'))
