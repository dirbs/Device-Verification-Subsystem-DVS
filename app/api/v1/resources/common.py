import requests
from app import GlobalConfig, Root, version, conditions


class CommonResources:

    @staticmethod
    def populate_reasons(blocking, reasons_list):
        try:
            voilating_conditions = [key['condition_name'] for key in blocking if key['condition_met']]
            for condition in conditions['conditions']:
                if condition['name'] in voilating_conditions:
                    reasons_list.append(condition['reason'])
            return reasons_list
        except Exception as error:
            raise error

    @staticmethod
    def populate_status(resp, status, status_type, blocking_condition=None, reason_list=None, imei=None, block_date=None, seen_with=None):
        try:
            if status == 'Compliant' or status == 'Provisionally Compliant':
                if seen_with:
                    resp['status'] = status + ' (Active)'
                else:
                    resp['status'] = status + ' (Inactive)'

                if status_type == "bulk":
                    return resp
                else:
                    return {"compliant": resp}
            else:
                resp['status'] = status
                resp['block_date'] = block_date
                if status_type == "basic":
                    resp['inactivity_reasons'] = CommonResources.populate_reasons(blocking_condition, reason_list)
                    resp['link_to_help'] = GlobalConfig['HelpUrl']
                elif status_type == "bulk":
                    resp['imei'] = imei
                    resp['inactivity_reasons'] = CommonResources.populate_reasons(blocking_condition, reason_list)
                    return resp
                return {"compliant": resp}
        except Exception as error:
            raise error



    @staticmethod
    def compliance_status(resp, status_type, imei=None):
        try:
            status = {}
            seen_with = resp['realtime_checks']['ever_observed_on_network']
            blocking_conditions = resp['classification_state']['blocking_conditions']
            stolen_status = resp['stolen_status']['provisional_only']
            reg_status = resp['registration_status']['provisional_only']
            block_date = resp.get('block_date', 'N/A')

            if reg_status:  # device's registration request is pending
                if stolen_status:  # device's stolen request pending
                    status = CommonResources.populate_status(status, 'Provisionally non compliant', status_type, blocking_conditions, ['Your device is stolen report is pending'], imei=imei, block_date=block_date)
                elif stolen_status is False:  # device is stolen
                    status = CommonResources.populate_status(status, 'Non compliant', status_type, blocking_conditions, ['Your device is stolen'], imei=imei, block_date=block_date)
                else:  # device is not stolen
                    status = CommonResources.populate_status(status, 'Provisionally Compliant', status_type)
            elif reg_status is None:  # device is not registered
                status = CommonResources.populate_status(status, 'Non compliant', status_type, blocking_conditions, ['Your device is not registered'], imei=imei, block_date=block_date)
            else:  # device is registered
                if stolen_status:  # stolen request is pending
                    status = CommonResources.populate_status(status, 'Provisionally non compliant', status_type, blocking_conditions, ['Your device stolen report is pending'], imei=imei, block_date=block_date)
                elif stolen_status is None:  # device is not stolen
                    status = CommonResources.populate_status(status, 'Compliant', status_type, seen_with=seen_with)
                else:  # stolen device
                    status = CommonResources.populate_status(status, 'Non compliant', status_type, blocking_conditions, ['Your device is stolen'], imei=imei, block_date=block_date)
            return status
        except Exception as error:
            raise error

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
                resp = tac_response.json()
                if resp['gsma'] and resp['registration']:
                    response = CommonResources.serialize(response, resp['gsma'], resp['registration'], status_type)
                    return response
                elif resp['registration'] and resp['gsma'] is None:
                    response = CommonResources.serialize_reg(response, resp['registration'], status_type)
                    return response
                elif resp['gsma'] and resp['registration'] is None:
                    response = CommonResources.serialize_gsma(response, resp['gsma'], status_type)
                    return response
            return {"gsma": None}
        except Exception as error:
            raise error

    @staticmethod
    def get_status(status, status_type):
        if status_type == "stolen":
            if status['provisional_only']:
                return "Pending report verification"
            elif status['provisional_only'] is None:
                return "No report"
            else:
                return "Verified lost"
        else:
            if status['provisional_only']:
                return "Pending Registration."
            elif status['provisional_only'] is None:
                return "Not registered"
            else:
                return "Registered"


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
    def serialize(response, gsma_resp, reg_resp, status_type):
        try:
            if status_type == "basic":
                response['brand'] = reg_resp.get('brand_name') if reg_resp.get('brand_name') else gsma_resp.get('brand_name')
                response['model_name'] = reg_resp.get('model') if reg_resp.get('model') else gsma_resp.get('model_name')
            else:
                response['brand'] = reg_resp.get('brand_name') if reg_resp.get('brand_name') else gsma_resp.get('brand_name')
                response['model_name'] = reg_resp.get('model') if reg_resp.get('model') else gsma_resp.get('model_name')
                response['model_number'] = reg_resp.get('model_number') if reg_resp.get('model_number') else gsma_resp.get('marketing_name')
                response['device_type'] = reg_resp.get('device_type') if reg_resp.get('device_type') else gsma_resp.get('gsma_device_type')
                response['operating_system'] = reg_resp.get('operating_system') if reg_resp.get('operating_system') else gsma_resp.get('operating_system')
                response['radio_access_technology'] = reg_resp.get('radio_interface') if reg_resp.get('radio_interface') else gsma_resp.get('bands')
                response['manufacturer'] = reg_resp.get('manufacturer') if reg_resp.get('manufacturer') else gsma_resp.get('manufacturer')
            return {'gsma': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_reg(response, reg_resp, status_type):
        try:
            if status_type == "basic":
                response['brand'] = reg_resp.get('brand_name')
                response['model_name'] = reg_resp.get('model')
            else:
                response['brand'] = reg_resp.get('brand_name')
                response['model_name'] = reg_resp.get('model')
                response['model_number'] = reg_resp.get('model_number')
                response['device_type'] = reg_resp.get('device_type')
                response['manufacturer'] = reg_resp.get('manufacturer')
                response['operating_system'] = reg_resp.get('operating_system')
                response['radio_access_technology'] = reg_resp.get('radio_interface')
            return {'gsma': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_gsma(response, gsma_resp, status_type):
        try:
            if status_type == "basic":
                response['brand'] = gsma_resp.get('brand_name')
                response['model_name'] = gsma_resp.get('model_name')
            else:
                response['brand'] = gsma_resp.get('brand_name')
                response['model_name'] = gsma_resp.get('model_name')
                response['model_number'] = gsma_resp.get('marketing_name')
                response['device_type'] = gsma_resp.get('gsma_device_type')
                response['manufacturer'] = gsma_resp.get('manufacturer')
                response['operating_system'] = gsma_resp.get('operating_system')
                response['radio_access_technology'] = gsma_resp.get('bands')
            return {'gsma': response}
        except Exception as error:
            raise error



