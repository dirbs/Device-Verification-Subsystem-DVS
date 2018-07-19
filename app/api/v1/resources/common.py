import requests
from app import GlobalConfig, Root, version
from ..assets.responses import responses


class CommonResources:

    @staticmethod
    def get_complaince_status(blocking_conditions, seen_with):
        try:
            response = dict()
            response['complaince_status'] = "Non compliant" if any(blocking_conditions[key] for key in blocking_conditions) else "Compliant (Active)" if seen_with else "Compliant (Inactive)"
            if response['complaince_status'] == "Non compliant":
                response['inactivity_reasons'] = [key.capitalize() for key in blocking_conditions if blocking_conditions[key]]
                response['link_to_help'] = GlobalConfig['HelpUrl']
                response['block_date'] = GlobalConfig['BlockDate']
            return response
        except Exception as e:
            raise e

    @staticmethod
    def get_imei(imei, seen_with):
        imei_response = requests.get('{base}/{version}/imei/{imei}?include_seen_with={seen_with}'.format(base=Root,
                                                                                                         version=version,
                                                                                                         imei=imei,
                                                                                                         seen_with=seen_with))  # dirbs core imei api call
        if imei_response.status_code == 200:
            return imei_response.json()
        else:
            return {}

    @staticmethod
    def get_tac(tac):
        tac_response = requests.get('{}/{}/tac/{}'.format(Root, version, tac))  # dirbs core tac api call
        if tac_response.status_code == 200:
            return tac_response.json()
        else:
            return {"gsma": None, "tac": tac}

    @staticmethod
    def get_status(imei, seen_with, tac):
        imei_response = CommonResources.get_imei(imei, seen_with)
        tac_response = CommonResources.get_tac(tac)
        if imei_response:
            return {"response": dict(imei_response, **tac_response), "message": "success", "status": responses.get('ok')}
        else:
            return {"response": {}, "message": "Connection error, Please try again later.", "status": responses.get('timeout')}

    @staticmethod
    def serialize(status_response, status_type):
        response = dict()
        if status_type == "basic":
            response['imei'] = status_response['imei_norm']
            response['brand'] = status_response['gsma']['brand_name']
            response['model_name'] = status_response['gsma']['model_name']
        else:
            response['imei'] = status_response['imei_norm']
            response['brand'] = status_response['gsma']['brand_name']
            response['model_name'] = status_response['gsma']['model_name']
            response['model_number'] = status_response['gsma']['marketing_name']
            response['device_type'] = status_response['gsma']['device_type']
            response['manufacturer'] = status_response['gsma']['manufacturer']
            response['operating_system'] = status_response['gsma']['operating_system']
            response['radio_access_technology'] = status_response['gsma']['bands']
            response['classification_state'] = status_response['classification_state']
        return response

