"""
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
    The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
    Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
    This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

from app import app
import requests
from flask_babel import _


class CommonResources:
    """Common resources used by APIs in DVS."""

    @staticmethod
    def populate_reasons(blocking, reasons_list):
        """Return reasons for IMEI to be non compliant."""

        try:
            voilating_conditions = [key['condition_name'] for key in blocking if key['condition_met']]
            for condition in app.config['conditions']['conditions']:
                if condition['name'] in voilating_conditions:
                    reasons_list.append(condition['reason'])
            return reasons_list
        except Exception as error:
            raise error

    @staticmethod
    def populate_status(resp, status, status_type, blocking_condition=None, reason_list=None, imei=None, block_date=None, seen_with=None):
        """Return compliant status of an IMEI."""

        try:
            if status == 'Compliant' or status == 'Provisionally Compliant':
                if seen_with:
                    resp['status'] = _(status + ' (Active)')
                else:
                    resp['status'] = _(status + ' (Inactive)')

                if status_type == "bulk":
                    return resp
                else:
                    return {"compliant": resp}
            else:
                resp['status'] = _(status)
                resp['block_date'] = _(block_date)
                if status_type == "basic":
                    resp['inactivity_reasons'] = CommonResources.populate_reasons(blocking_condition, reason_list)
                    resp['link_to_help'] = app.config['system_config']['global']['HelpUrl']
                elif status_type == "bulk":
                    resp['imei'] = imei
                    resp['inactivity_reasons'] = CommonResources.populate_reasons(blocking_condition, reason_list)
                    return resp
                return {"compliant": resp}
        except Exception as error:
            raise error

    @staticmethod
    def compliance_status(resp, status_type, imei=None):
        """Evaluate IMEIs to be compliant/non complaint."""

        try:
            status = {}
            seen_with = resp['realtime_checks']['ever_observed_on_network']
            blocking_conditions = resp['classification_state']['blocking_conditions']
            stolen_status = resp['stolen_status']['provisional_only']
            reg_status = resp['registration_status']['provisional_only']
            block_date = resp.get('block_date', 'N/A')

            if reg_status:  # device's registration request is pending
                if stolen_status:  # device's stolen request pending
                    status = CommonResources.populate_status(status, 'Provisionally non compliant', status_type, blocking_conditions, [_('Your device stolen report is pending')], imei=imei, block_date=block_date)
                elif stolen_status is False:  # device is stolen
                    status = CommonResources.populate_status(status, 'Non compliant', status_type, blocking_conditions, [_('Your device is stolen')], imei=imei, block_date=block_date)
                else:  # device is not stolen
                    status = CommonResources.populate_status(status, 'Provisionally Compliant', status_type)
            elif reg_status is None:  # device is not registered
                status = CommonResources.populate_status(status, 'Non compliant', status_type, blocking_conditions, [_('Your device is not registered')], imei=imei, block_date=block_date)
            else:  # device is registered
                if stolen_status:  # stolen request is pending
                    status = CommonResources.populate_status(status, 'Provisionally non compliant', status_type, blocking_conditions, [_('Your device stolen report is pending')], imei=imei, block_date=block_date)
                elif stolen_status is None:  # device is not stolen
                    status = CommonResources.populate_status(status, 'Compliant', status_type, seen_with=seen_with)
                else:  # stolen device
                    status = CommonResources.populate_status(status, 'Non compliant', status_type, blocking_conditions, [_('Your device is stolen')], imei=imei, block_date=block_date)
            return status
        except Exception as error:
            raise error

    @staticmethod
    def get_imei(imei):
        """Return IMEI response obtained from DIRBS core."""

        imei_url = requests.get('{base}/{version}/imei/{imei}'.format(base=app.config['dev_config']['dirbs_core']['BaseUrl'], version=app.config['dev_config']['dirbs_core']['Version'], imei=imei))  # dirbs core imei api call
        try:
            if imei_url.status_code == 200:
                response = imei_url.json()
                return response
            else:
                return None
        except Exception as error:
            raise error

    @staticmethod
    def get_tac(tac):
        """Return TAC response obtained from DIRBS core."""

        try:
            tac_response = requests.get('{}/{}/tac/{}'.format(app.config['dev_config']['dirbs_core']['BaseUrl'], app.config['dev_config']['dirbs_core']['Version'], tac))  # dirbs core tac api call
            if tac_response.status_code == 200:
                resp = tac_response.json()
                return resp
            return {"gsma": None}
        except Exception as error:
            raise error

    @staticmethod
    def get_reg(imei):
        """Return registration information obtained from DIRBS core."""

        try:
            reg_response = requests.get('{base}/{version}/imei/{imei}/info'.format(base=app.config['dev_config']['dirbs_core']['BaseUrl'], version=app.config['dev_config']['dirbs_core']['Version'], imei=imei))
            if reg_response.status_code == 200:
                resp = reg_response.json()
                return resp
            return {}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_gsma_data(tac_resp, reg_resp, status_type):
        """Return serialized device details"""

        response = dict()
        if tac_resp['gsma'] and reg_resp:
            response = CommonResources.serialize(response, tac_resp['gsma'], reg_resp, status_type)
            return response
        elif reg_resp and not tac_resp['gsma']:
            response = CommonResources.serialize_reg(response, reg_resp, status_type)
            return response
        elif tac_resp['gsma'] and not reg_resp:
            response = CommonResources.serialize_gsma(response, tac_resp['gsma'], status_type)
            return response
        else:
            return {"gsma":None}

    @staticmethod
    def get_status(status, status_type):
        """Serialize stolen/registration status"""

        if status_type == "stolen":
            if status['provisional_only']:
                return _("Pending report verification")
            elif status['provisional_only'] is None:
                return _("No report")
            else:
                return _("Verified lost")
        else:
            if status['provisional_only']:
                return _("Pending Registration")
            elif status['provisional_only'] is None:
                return _("Not registered")
            else:
                return _("Registered")

    @staticmethod
    def subscribers(imei, start, limit):
        """Return subscriber's details."""
        try:
            seen_with_url = requests.get('{base}/{version}/imei/{imei}/subscribers?limit={limit}&offset={offset}'
                                         .format(base=app.config['dev_config']['dirbs_core']['BaseUrl'], version=app.config['dev_config']['dirbs_core']['Version'], imei=imei, limit=limit, offset=start))  # dirbs core imei api call
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
        """Return pairings information."""
        try:
            pairings_url = requests.get('{base}/{version}/imei/{imei}/pairings?limit={limit}&offset={offset}'
                                         .format(base=app.config['dev_config']['dirbs_core']['BaseUrl'], version=app.config['dev_config']['dirbs_core']['Version'], imei=imei, limit=limit,
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
        """Serialize device details from GSMA/registration data."""
        try:
            if status_type == "basic":
                response['brand'] = reg_resp.get('brand_name') if reg_resp.get('brand_name') else gsma_resp.get('brand_name')
                response['model_name'] = reg_resp.get('model') if reg_resp.get('model') else gsma_resp.get('model_name')
            else:
                response['brand'] = reg_resp.get('brand_name') if reg_resp.get('brand_name') else gsma_resp.get('brand_name')
                response['model_name'] = reg_resp.get('model') if reg_resp.get('model') else gsma_resp.get('model_name')
                response['model_number'] = reg_resp.get('model_number') if reg_resp.get('model_number') else gsma_resp.get('marketing_name')
                response['device_type'] = reg_resp.get('device_type') if reg_resp.get('device_type') else gsma_resp.get('device_type')
                response['operating_system'] = reg_resp.get('operating_system') if reg_resp.get('operating_system') else gsma_resp.get('operating_system')
                response['radio_access_technology'] = reg_resp.get('radio_interface') if reg_resp.get('radio_interface') else gsma_resp.get('bands')
                response['manufacturer'] = reg_resp.get('manufacturer') if reg_resp.get('manufacturer') else gsma_resp.get('manufacturer')
            return {'gsma': response}
        except Exception as error:
            raise error

    @staticmethod
    def serialize_reg(response, reg_resp, status_type):
        """Serialize device details from registration data."""
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
        """Serialize device details from GSMA data."""

        try:
            if status_type == "basic":
                response['brand'] = gsma_resp.get('brand_name')
                response['model_name'] = gsma_resp.get('model_name')
            else:
                response['brand'] = gsma_resp.get('brand_name')
                response['model_name'] = gsma_resp.get('model_name')
                response['model_number'] = gsma_resp.get('marketing_name')
                response['device_type'] = gsma_resp.get('device_type')
                response['manufacturer'] = gsma_resp.get('manufacturer')
                response['operating_system'] = gsma_resp.get('operating_system')
                response['radio_access_technology'] = gsma_resp.get('bands')
            return {'gsma': response}
        except Exception as error:
            raise error



