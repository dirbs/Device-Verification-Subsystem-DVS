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
from app import task_dir, AllowedExt

from ..handlers.error_handling import *
from ..handlers.codes import RESPONSES, MIME_TYPES
from ..helpers.bulk_common import BulkCommonResources

from flask_restful import Resource, request


class AdminBulkDRS(Resource):

    @staticmethod
    def post():
        try:
            task_file = open(os.path.join(task_dir, 'task_ids.txt'), 'a+')
            file = request.files.get('file')
            if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in AllowedExt:  # validate file type
                imeis = list(set(line.decode('ascii', errors='ignore') for line in (l.strip() for l in file) if line))
                print(imeis)
                response = BulkCommonResources.get_summary.apply_async((imeis, None, 'drs'))
                data = {
                    "message": "You can track your request using this id",
                    "task_id": response.id
                }
                task_file.write(response.id + '\n')
                return Response(json.dumps(data), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
            else:
                return custom_response("System only accepts tsv/txt files.", RESPONSES.get('BAD_REQUEST'),
                                       MIME_TYPES.get('JSON'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving summary.")
            app.logger.exception(e)
            return custom_response("Failed to verify bulk imeis.", RESPONSES.get('SERVICE_UNAVAILABLE'),
                                   MIME_TYPES.get('JSON'))
