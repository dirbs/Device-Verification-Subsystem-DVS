import requests
from webargs.flaskparser import use_kwargs
from app import Root, BaseUrl, GlobalConfig, version
from ..assets.error_handling import *
from ..requests.status_request import full_status_args
from .common import CommonResoures

resource = CommonResoures()


class FullStatus():

    @use_kwargs(full_status_args)
    def get(self, imei, seen_with, start, limit):
        try:
            response = {}
            tac = imei[:GlobalConfig['TacLength']]  # slice TAC from IMEI
            if tac.isdigit():  # TAC format validation
                tac_response = requests.get('{}/{}/tac/{}'.format(Root, version, tac)).json()  # dirbs core TAC api call
                imei_response = requests.get('{}/{}/imei/{}?include_seen_with=1'.format(Root, version, imei)).json()  # dirbs core IMEI api call with seen with information
                full_status = dict(tac_response, **imei_response)
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
                    complain_status = resource.get_complaince_status(blocking_conditions, full_status.get('seen_with'))  # get compliance status
                    response = dict(response, **complain_status) if complain_status else response
                    if seen_with == 1:
                        response['associated_msisdn'] = full_status.get('seen_with')
                        response, status = self.paginated_list(response, start, limit, imei, seen_with, '{}/fullstatus'.format(BaseUrl))
                    status = 200
                    return Response(json.dumps(response), status=status, mimetype='application/json')
                else:
                    return custom_response("IMEI not found", 404, 'application/json')
            else:
                return custom_response("Bad TAC format", 400, 'application/json')
        except Exception as e:
            app.logger.info("This error occurs while retrieving full status.")
            app.logger.exception(e)
            return internal_error()

    def paginated_list(self, data, start, limit, imei, seen_with, url):  # TODO: optmizaion required
        try:
            count = len(data['associated_msisdn'])
            if (count < start):
                return "Index out of bound.", 400
            # make response
            data['start'] = start
            data['limit'] = limit
            data['count'] = count
            # make URLs
            # make previous url
            if start == 1:
                data['previous'] = ''
            else:
                start_copy = max(1, start - limit)
                limit_copy = max(1, start - 1)
                data['previous'] = url + '?imei=%s&seen_with=%d&start=%d&limit=%d' % (imei, seen_with, start_copy, limit_copy)
            # make next url
            if start + limit > count:
                data['next'] = ''
            else:
                start_copy = start + limit
                data['next'] = url + '?imei=%s&seen_with=%d&start=%d&limit=%d' % (imei, seen_with, start_copy, limit)
            # finally extract result according to bounds
            data['associated_msisdn'] = data['associated_msisdn'][(start - 1):(start - 1 + limit) if (start - 1 + limit) <= count else count]
            return data, 200

        except Exception as e:
            app.logger.info("This error occurs while pagination.")
            app.logger.exception(e)
            return internal_error()




