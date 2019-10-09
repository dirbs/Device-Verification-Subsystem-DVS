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

from flask_apispec import use_kwargs, MethodResource, doc
from flask_babel import _

from ..helpers.common import CommonResources
from ..handlers.error_handling import *
from ..handlers.codes import RESPONSES, MIME_TYPES
from ..schema.system_schemas import FullStatusSchema


class FullStatus(MethodResource):
    """Flask resource for IMEI full status"""

    @doc(description="Get complete information related to an IMEI", tags=['fullstatus'])
    @use_kwargs(FullStatusSchema().fields_dict, locations=['json'])
    def post(self, **args):
        """Return full status of IMEI."""
        try:
            response = dict()
            imei = args.get('imei')
            tac = imei[:app.config['system_config']['global']['TacLength']]  # slice TAC from IMEI
            paginate_sub = args.get('subscribers')
            paginate_pairs = args.get('pairs')
            status = CommonResources.get_imei(imei=args.get('imei'))  # get imei response from core
            if status:
                gsma_data = CommonResources.get_tac(tac)  # get gsma data from tac
                registration = CommonResources.get_reg(imei)
                gsma = CommonResources.serialize_gsma_data(tac_resp=gsma_data, reg_resp=registration,
                                                           status_type="full")
                subscribers = CommonResources.subscribers(imei, paginate_sub.get('start', 1),
                                                          paginate_sub.get('limit', 10))  # get subscribers data
                pairings = CommonResources.pairings(imei, paginate_pairs.get('start', 1),
                                                    paginate_pairs.get('limit', 10))  # get pairing data
                response['imei'] = status.get('imei_norm')
                response['classification_state'] = status['classification_state']
                response['registration_status'] = CommonResources.get_status(status['registration_status'],
                                                                             "registration")
                response['stolen_status'] = CommonResources.get_status(status['stolen_status'], "stolen")
                compliance = CommonResources.compliance_status(status, "full")  # get compliance status
                response = dict(response, **gsma, **subscribers, **pairings, **compliance)
                return Response(json.dumps(response), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
            else:
                return custom_response(_("Failed to retrieve IMEI response from core system."),
                                       RESPONSES.get('SERVICE_UNAVAILABLE'), mimetype=MIME_TYPES.get('JSON'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving full status.")
            app.logger.exception(e)
            return custom_response(_("Failed to retrieve full status."), RESPONSES.get('SERVICE_UNAVAILABLE'),
                                   mimetype=MIME_TYPES.get('JSON'))
