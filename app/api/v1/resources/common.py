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

from ..handlers.error_handling import *
from ..handlers.codes import RESPONSES, MIME_TYPES
from ..models.summary import Summary
from ..models.request import Request

from flask import send_from_directory
from flask_apispec import MethodResource, doc
from flask_babel import _


class AdminDownloadFile(MethodResource):
    """Flask resource for downloading report."""

    @doc(description="Download IMEIs report", tags=['bulk'])
    def post(self, filename):
        """Sends downloadable report."""
        try:
            # returns file when user wants to download non compliance report
            return send_from_directory(directory=app.config['dev_config']['UPLOADS']['report_dir'], filename=filename)
        except Exception as e:
            app.logger.info("Error occurred while downloading non compliant report.")
            app.logger.exception(e)
            return custom_response(_("Compliant report not found."), RESPONSES.get('OK'), MIME_TYPES.get('JSON'))


class AdminCheckBulkStatus(MethodResource):
    """Flask resource to check bulk processing status."""

    @doc(description="Check bulk request status", tags=['bulk'])
    def post(self, task_id):
        """Returns bulk processing status and summary if processing is completed."""
        try:
            result = Summary.find_by_trackingid(task_id)
            if result is None:
                response = {
                    "state": _("task not found.")
                }
            else:
                if result['status'] == 'PENDING':
                    # job is in progress yet
                    response = {
                        'state': _('PENDING')
                    }
                elif result['status'] == 'SUCCESS':
                    response = {
                        "state": _(result['status']),
                        "result": result['response']
                    }
                else:
                    # something went wrong in the background job
                    response = {
                        'state': _('Processing Failed.')
                    }
            return Response(json.dumps(response), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving status.")
            app.logger.exception(e)
            return Response(MESSAGES.get('INTERNAL_SERVER_ERROR'), RESPONSES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('JSON'))


@doc(description="Base Route", tags=['base'])
@app.route('/', methods=['GET'])
def index():
    """Flask base route."""
    data = {
        'message': _('Welcome to DVS')
    }

    response = Response(json.dumps(data), status=200, mimetype='application/json')
    return response


class GetRequests(MethodResource):
    """Flask resource for downloading report."""

    @doc(description="Get all bulk processes requested by user.", tags=['bulk'])
    def get(self, user_id):
        """Sends downloadable report."""
        try:
            resp = Request.find_requests(user_id)
            if resp:
                return Response(json.dumps(resp), status=RESPONSES.get("OK"), mimetype='application/json')
            else:
                data = {
                    "message": _("No requests recorded for this user."),
                    "user_id": user_id
                }
                return Response(json.dumps(data), status=RESPONSES.get("NOT_FOUND"), mimetype=MIME_TYPES.get("JSON"))
        except Exception as e:
            app.logger.info("Error occurred while retrieving user requests.")
            app.logger.exception(e)
            return Response(MESSAGES.get('INTERNAL_SERVER_ERROR'), RESPONSES.get('INTERNAL_SERVER_ERROR'),
                            mimetype=MIME_TYPES.get('JSON'))

