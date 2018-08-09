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
    def populate_status(resp, status, status_type, blocking_condition=None, reason_list=None, imei=None, block_date=None):
        try:
            if status == 'Compliant (Active)' or status == 'Provisionally Compliant' or status == 'Compliant (Inactive)':
                resp['status'] = status
                if status_type=="bulk":
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

            if seen_with:  # checks if IMEI has ever been seen on network
                if any(key['condition_met'] for key in
                       blocking_conditions):  # checks if IMEI meeting any blocking condition
                    status = CommonResources.populate_status(status, 'Non Compliant', status_type, blocking_conditions, [], imei=imei, block_date=block_date)
                elif stolen_status:  # device's stolen request is pending
                    status = CommonResources.populate_status(status, 'Provisionally Non Compliant', status_type, blocking_conditions, ['Your device stolen report is pending'], imei=imei, block_date=block_date)
                elif stolen_status is None:  # device is not stolen
                    status = CommonResources.populate_status(status, 'Compliant (Active)', status_type)
                else:  # device is stolen
                    status = CommonResources.populate_status(status, 'Non Compliant', status_type, blocking_conditions, ['Your device has been stolen'], imei=imei, block_date=block_date)
            else:
                if reg_status:  # device's registration request is pending
                    if stolen_status:  # device's stolen request pending
                        status = CommonResources.populate_status(status, 'Provisionally Non Compliant', status_type, blocking_conditions, ['Your device is stolen report is pending'], imei=imei, block_date=block_date)
                    elif stolen_status is False:  # device is stolen
                        status = CommonResources.populate_status(status, 'Non Compliant', status_type, blocking_conditions, ['Your device is stolen'], imei=imei, block_date=block_date)
                    else:  # device is not stolen
                        status = CommonResources.populate_status(status, 'Provisionally Compliant', status_type)
                elif reg_status is None:  # device is not registered
                    status = CommonResources.populate_status(status, 'Non Compliant', status_type, blocking_conditions, ['Your device is not registered'], imei=imei, block_date=block_date)
                else:  # device is registered
                    if stolen_status:  # stolen request is pending
                        status = CommonResources.populate_status(status, 'Provisionally Non Compliant', status_type, blocking_conditions, ['Your device stolen report is pending'], imei=imei, block_date=block_date)
                    elif stolen_status is None:  # device is not stolen
                        status = CommonResources.populate_status(status, 'Compliant (Inactive)', status_type)
                    else:  # stolen device
                        status = CommonResources.populate_status(status, 'Non Compliant', status_type, blocking_conditions, ['Your device is stolen'], imei=imei, block_date=block_date)
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

