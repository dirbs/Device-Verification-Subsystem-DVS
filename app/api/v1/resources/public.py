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

import urllib.request
import urllib.parse
import requests
from flask_apispec import use_kwargs, MethodResource, doc
from flask_babel import _

from ..helpers.common import CommonResources
from ..handlers.error_handling import *
from ..handlers.codes import RESPONSES, MIME_TYPES
from ..schema.system_schemas import BasicStatusSchema, SMSSchema
from ..models.request import *


class BasicStatus(MethodResource):
    """Flask resource for IMEI basic status"""

    @doc(description="Get Basic details of IMEI", tags=['basicstatus'])
    @use_kwargs(BasicStatusSchema().fields_dict, locations=['query'])
    def get(self, **args):
        """Return IMEI basic status."""

        try:
            captcha_uri = 'https://www.google.com/recaptcha/api/siteverify'

            recaptcha_response = args.get('token')

            private_recaptcha = app.config['dev_config']['secret_keys']['web'] \
                if args.get('source') == "web" else app.config['dev_config']['secret_keys']['iOS'] \
                if args.get('source') == "ios" else app.config['dev_config']['secret_keys']['android']

            params = urllib.parse.urlencode({
                        'secret': private_recaptcha,
                        'response': recaptcha_response
                    }).encode("utf-8")

            data = urllib.request.urlopen(captcha_uri, params).read().decode("utf-8")
            result = json.loads(data)

            success = result.get('success', None)

            if success:
                tac = args['imei'][:app.config['system_config']['global']['TacLength']]  # slice TAC from IMEI
                status = CommonResources.get_imei(imei=args.get('imei'))  # get imei response
                if status:
                    compliance = CommonResources.compliance_status(status, "basic")  # get compliance status
                    gsma_data = CommonResources.get_tac(tac)  # get gsma data from tac
                    registration = CommonResources.get_reg(args.get('imei'))
                    gsma = CommonResources.serialize_gsma_data(tac_resp=gsma_data, reg_resp=registration,
                                                               status_type="basic")
                    response = dict(compliance, **gsma, **{'imei': status.get('imei_norm')})  # merge RESPONSES
                    return Response(json.dumps(response), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
                else:
                    return custom_response(_("Failed to retrieve IMEI status from core system."),
                                           RESPONSES.get('SERVICE_UNAVAILABLE'), MIME_TYPES.get('JSON'))
            else:
                return custom_response(_("ReCaptcha Failed!"), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving basic status.")
            app.log_exception(e)
            return custom_response(_("Failed to retrieve basic status."), RESPONSES.get('SERVICE_UNAVAILABLE'),
                                   MIME_TYPES.get('JSON'))


class PublicSMS(MethodResource):
    """Flask resource for SMS."""

    @doc(description="SMS API", tags=['sms'])
    @use_kwargs(SMSSchema().fields_dict, locations=['query'])
    def get(self, **args):
        """Return IMEI compliant status."""
        try:
            status = CommonResources.get_imei(imei=args.get('imei'))  # get imei response
            if status:
                compliance = CommonResources.compliance_status(status, "basic")  # get compliance status
                if "non compliant" in compliance['compliant']['status'].lower():
                    message = "STATUS: {status}, Block Date: {date}".format(date=compliance['compliant']['block_date'],
                                                                            status=compliance['compliant']['status'])
                else:
                    message = "STATUS: {status}".format(status=compliance['compliant']['status'])
                return Response(message, status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('TEXT'))
            else:
                return Response(_("Failed to retrieve IMEI response from core system."),
                                status=RESPONSES.get('SERVICE_UNAVAILABLE'), mimetype=MIME_TYPES.get('TEXT'))
        except Exception:
            app.logger.info("Error occurred while retrieving sms status.")
            return Response(_("Failed to retrieve sms status."), status=RESPONSES.get('SERVICE_UNAVAILABLE'),
                            mimetype=MIME_TYPES.get('TEXT'))


class BaseRoute(MethodResource):
    """Flask resource to check system's connection with DIRBS core."""

    @doc(description="Base Route to check connection with core", tags=['base'])
    def get(self):
        """Checks system's connection with DIRBS core."""

        try:
            resp = requests.get('{base}/{version}/version'.format(
                base=app.config['dev_config']['dirbs_core']['BaseUrl'],
                version=app.config['dev_config']['dirbs_core']['Version']))  # dirbs core imei api call
            if resp.status_code == 200:
                data = {
                    "message": _("CORE connected successfully.")
                }
            else:
                data = {
                    "message": _("CORE connection failed.")
                }
        except requests.ConnectionError:
            data = {
                "message": _("CORE connection failed.")
            }
        try:
            Request.query.all()
            data['db_status'] = _("Database connected successfully")
        except:
            data['db_status'] = _("Database connection failed")

        return Response(json.dumps(data), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
