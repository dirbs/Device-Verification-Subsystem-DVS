#######################################################################################################################
#                                                                                                                     #
# Copyright (c) 2018 Qualcomm Technologies, Inc.                                                                      #
#                                                                                                                     #
# All rights reserved.                                                                                                #
#                                                                                                                     #
# Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the      #
# limitations in the disclaimer below) provided that the following conditions are met:                                #
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following  #
#   disclaimer.                                                                                                       #
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the         #
#   following disclaimer in the documentation and/or other materials provided with the distribution.                  #
# * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or       #
#   promote products derived from this software without specific prior written permission.                            #
#                                                                                                                     #
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED  #
# BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED #
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT      #
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR   #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,      #
# DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,      #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,   #
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                                  #
#                                                                                                                     #
#######################################################################################################################

import os
from app import task_dir, report_dir

from ..handlers.error_handling import *
from ..handlers.codes import RESPONSES, MIME_TYPES
from ..helpers.bulk_common import BulkCommonResources

from flask import send_from_directory
from flask_apispec import MethodResource, doc


class AdminDownloadFile(MethodResource):

    @doc(description="Download IMEIs report", tags=['bulk'])
    def post(self, filename):
        try:
            return send_from_directory(directory=report_dir, filename=filename)  # returns file when user wnats to download non compliance report
        except Exception as e:
            app.logger.info("Error occurred while downloading non compliant report.")
            app.logger.exception(e)
            return custom_response("Compliant report not found.", RESPONSES.get('OK'), MIME_TYPES.get('JSON'))


class AdminCheckBulkStatus(MethodResource):

    @doc(description="Check bulk request status", tags=['bulk'])
    def post(self, task_id):
        with open(os.path.join(task_dir, 'task_ids.txt'), 'r') as f:
            if task_id in list(f.read().splitlines()):
                task = BulkCommonResources.get_summary.AsyncResult(task_id)
                if task.state == 'PENDING':
                    # job is in progress yet
                    response = {
                        'state': 'PENDING'
                    }
                elif task.state == 'SUCCESS' and task.get():
                    response = {
                        "state": task.state,
                        "result": task.get()
                    }
                else:
                    # something went wrong in the background job
                    response = {
                        'state': 'Processing Failed.'
                    }
            else:
                response = {
                    "state": "task not found."
                }

        return Response(json.dumps(response), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))


@doc(description="Base Route", tags=['base'])
@app.route('/', methods=['GET'])
def index():
    data = {
        'message': 'Welcome to DVS'
    }

    response = Response(json.dumps(data), status=200, mimetype='application/json')
    return response

