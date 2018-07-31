import requests
from app import GlobalConfig, Root, version


class CommonResources:

    @staticmethod
    def get_compliance_status(blocking_conditions, seen_with, status):
        try:
            response = dict()
            response['status'] = "Non compliant" if any(key['condition_met'] for key in blocking_conditions) else "Compliant (Active)" if seen_with else "Compliant (Inactive)"
            if response['status'] == "Non compliant":
                response['block_date'] = GlobalConfig['BlockDate']
                if status == "basic":
                    response['inactivity_reasons'] = [key['condition_name'].capitalize() for key in blocking_conditions if key['condition_met']]
                    response['link_to_help'] = GlobalConfig['HelpUrl']
            return {'compliance': response}
        except Exception as e:
            raise e

    @staticmethod
    def get_imei(imei):
        try:
            imei_url = requests.get('{base}/{version}/imei/{imei}'.format(base=Root, version=version, imei=imei))  # dirbs core imei api call
            response = imei_url.json()
            return response
        except Exception as error:
            raise error

    @staticmethod
    def get_tac(tac, status_type):
        try:
            response = dict()
            tac_response = requests.get('{}/{}/tac/{}'.format(Root, version, tac))  # dirbs core tac api call
            if tac_response.status_code == 200:
                tac_response = tac_response.json()
                if tac_response['gsma']:
                    response = CommonResources.serialize(response, tac_response['gsma'], status_type)
                    return response
                elif tac_response['registration']:
                    response = CommonResources.serialize(response, tac_response['registration'], status_type)
                    return response
            return {"gsma": None}
        except Exception as error:
            raise error

    @staticmethod
    def subscribers(imei, start, limit):
        try:
            seen_with_url = requests.get('{base}/{version}/imei/{imei}/subscribers?limit={limit}&offset={offset}'
                                         .format(base=Root, version=version, imei=imei, limit=limit, offset=start))  # dirbs core imei api call
            seen_with_resp = seen_with_url.json()
            response = {"count": seen_with_resp.get('_keys').get('result_size'),
                        "start": start,
                        "limit": limit,
                        "data": seen_with_resp.get('subscribers')}
            return {'subscribers': response}
        except Exception as error:
            raise error

    @staticmethod
    def pairings(imei, start, limit):
        try:
            pairings_url = requests.get('{base}/{version}/imei/{imei}/pairings?limit={limit}&offset={offset}'
                                         .format(base=Root, version=version, imei=imei, limit=limit,
                                                 offset=start))  # dirbs core imei api call
            pairings_resp = pairings_url.json()
            response = {"count": pairings_resp.get('_keys').get('result_size'),
                        "start": start,
                        "limit": limit,
                        "data": pairings_resp.get('pairs')}
            return {'pairs': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize(response, status_response, status_type):
        try:
            if status_type == "basic":
                response['brand'] = status_response['brand_name']
                response['model_name'] = status_response['model_name']
            else:
                response['brand'] = status_response['brand_name']
                response['model_name'] = status_response['model_name']
                response['model_number'] = status_response['marketing_name']
                response['device_type'] = status_response['gsma_device_type']
                response['manufacturer'] = status_response['manufacturer']
                response['operating_system'] = status_response.get('operating_system')
                response['radio_access_technology'] = status_response['bands']
            return {'gsma': response}
        except Exception as error:
            raise error

