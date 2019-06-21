"""
 SPDX-License-Identifier: BSD-4-Clause-Clear

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
 * All advertising materials mentioning features or use of this software, or any deployment of this software, or
   documentation accompanying any distribution of this software, must display the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
   products derived from this software without specific prior written permission.

 SPDX-License-Identifier: ZLIB-ACKNOWLEDGEMENT

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable
 for any damages arising from the use of this software.

 Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter
 it and redistribute it freely, subject to the following restrictions:

 * The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If
   you use this software in a product, an acknowledgment is required by displaying the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
 * This notice may not be removed or altered from any source distribution.

 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

import os
import re
import magic
import tempfile
from shutil import rmtree
from flask_restful import request
from flask_apispec import MethodResource, doc, use_kwargs
from flask_babel import _
from datetime import datetime

from ..handlers.error_handling import *
from ..handlers.codes import RESPONSES, MIME_TYPES
from ..helpers.tasks import CeleryTasks
from ..schema.system_schemas import BulkSchema
from ..models.request import *
from ..models.summary import *


class AdminBulk(MethodResource):
    """Flask resource for DVS bulk request."""

    @doc(description="Verify Bulk IMEIs via file/tac request", tags=['bulk'])
    @use_kwargs(BulkSchema().fields_dict, locations=['form'])
    def post(self, **args):
        """Start processing DVS bulk request in background (calls celery task)."""
        try:
            args['file'] = request.files.get('file')
            if args.get('file') is not None and args.get('tac') is not None:
                return custom_response(_("Please select either file or tac you cannot select both."), status=RESPONSES.get('BAD_REQUEST'), mimetype=MIME_TYPES.get('JSON'))
            else:
                invalid_imeis = 0
                filtered_list = []
                file = args.get('file')
                if file:
                    tempdir = tempfile.mkdtemp()
                    filename = file.filename
                    filepath = os.path.join(tempdir, file.filename)
                    file.save(filepath)
                    try:
                        mimetype = magic.from_file(filepath, mime=True)
                        if filename != '':
                            if mimetype in app.config['system_config']['allowed_file_types']['AllowedTypes'] and '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['system_config']['allowed_file_types']['AllowedExt']:  # validate file type
                                file = open(filepath, encoding="utf8", errors='ignore')
                                imeis = list(set(line.strip() for line in file.read().split('\n') if line))
                                if imeis and int(app.config['system_config']['global']['MinFileContent']) <= len(imeis) <= int(app.config['system_config']['global']['MaxFileContent']):  # validate file content length
                                    for imei in imeis:
                                        if re.match(r'^[a-fA-F0-9]{14,16}$', imei) is None:
                                            invalid_imeis += 1
                                        else:
                                            filtered_list.append(imei)
                                    imeis_list = filtered_list
                                    if imeis_list:
                                        response = (CeleryTasks.get_summary.s(imeis_list, invalid_imeis) |
                                                    CeleryTasks.log_results.s(input=str(filename))).apply_async()
                                        summary_data = {
                                            "tracking_id": response.parent.id,
                                            "input": filename,
                                            "input_type": "file",
                                            "status": response.state
                                        }
                                        summary_record = Summary.create(summary_data)
                                        request_data = {
                                            "username": request.form.get('username'),
                                            "user_id": request.form.get('user_id'),
                                            "summary_id": summary_record
                                        }
                                        Request.create(request_data)
                                        data = {
                                            "message": _("You can track your request using this id"),
                                            "task_id": response.parent.id
                                        }
                                        return Response(json.dumps(data), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
                                    else:
                                        return custom_response(_("File contains malformed content."),
                                                               status=RESPONSES.get('BAD_REQUEST'),
                                                               mimetype=MIME_TYPES.get('JSON'))
                                else:
                                    return custom_response(_("File must have minimum %(min)s or maximum %(max)s IMEIs.", min=str(app.config['system_config']['global']['MinFileContent']), max=str(app.config['system_config']['global']['MaxFileContent'])), status=RESPONSES.get('bad_request'), mimetype=MIME_TYPES.get('json'))
                            else:
                                return custom_response(_("System only accepts tsv/txt files."), RESPONSES.get('BAD_REQUEST'), MIME_TYPES.get('JSON'))
                        else:
                            return custom_response(_('No file selected.'), RESPONSES.get('BAD_REQUEST'),
                                                   MIME_TYPES.get('JSON'))
                    finally:
                        rmtree(tempdir)

                else:  # check for tac if file not uploaded
                    tac = request.form.get('tac')
                    if tac:
                        if tac.isdigit() and len(tac) == int(app.config['system_config']['global']['TacLength']):
                            result = Summary.find_by_input(tac)
                            if result is not None:
                                d0 = datetime.today().date()
                                d1 = result['start_time'].date()
                                delta = d0 - d1
                                retention_time = app.config['system_config']['global']['RetentionTime']
                                tracking_id = result['tracking_id']
                                request_data = {
                                    "username": request.form.get('username'),
                                    "user_id": request.form.get('user_id'),
                                    "summary_id": result['id']
                                }
                                Request.create(request_data)
                                if result['status']=="PENDING" and delta.days < retention_time:
                                    data = {
                                        "message": _("You're request is already in process cannot process another request with same data. Track using this id,"),
                                        "task_id": tracking_id
                                    }
                                    return Response(json.dumps(data), status=RESPONSES.get('OK'),
                                                    mimetype=MIME_TYPES.get('JSON'))
                                elif result['status']=="SUCCESS" and delta.days < retention_time:
                                    data = {
                                        "message": _("You're request is completed. Track using this id,"),
                                        "task_id": tracking_id
                                    }
                                    return Response(json.dumps(data), status=RESPONSES.get('OK'),
                                                    mimetype=MIME_TYPES.get('JSON'))
                                else:
                                    imei = tac + str(app.config['system_config']['global']['MinImeiRange'])
                                    imei_list = [str(int(imei) + x) for x in
                                                 range(int(app.config['system_config']['global']['MaxImeiRange']))]
                                    response = (CeleryTasks.get_summary.subtask(args=(imei_list, invalid_imeis), task_id=tracking_id) |
                                                CeleryTasks.log_results.s(input=tac)).apply_async()
                                    summary_data = {
                                        "tracking_id": tracking_id,
                                        "input": tac,
                                        "status": response.state
                                    }
                                    Summary.update_failed_task_to_pending(summary_data)
                                    data = {
                                        "message": _("You can track your request using this id"),
                                        "task_id": tracking_id
                                    }
                                    return Response(json.dumps(data), status=RESPONSES.get('OK'),
                                                    mimetype=MIME_TYPES.get('JSON'))
                            else:
                                imei = tac + str(app.config['system_config']['global']['MinImeiRange'])
                                imei_list = [str(int(imei) + x) for x in range(int(app.config['system_config']['global']['MaxImeiRange']))]
                                response = (CeleryTasks.get_summary.s(imei_list, invalid_imeis) |
                                            CeleryTasks.log_results.s(input=tac)).apply_async()
                                summary_data = {
                                    "tracking_id": response.parent.id,
                                    "input": tac,
                                    "input_type": "tac",
                                    "status": response.state
                                }
                                summary_record = Summary.create(summary_data)
                                request_data = {
                                    "username": request.form.get('username'),
                                    "user_id": request.form.get('user_id'),
                                    "summary_id": summary_record
                                }
                                Request.create(request_data)
                                data = {
                                    "message": _("You can track your request using this id"),
                                    "task_id": response.parent.id
                                }
                                return Response(json.dumps(data), status=RESPONSES.get('OK'), mimetype=MIME_TYPES.get('JSON'))
                        else:
                            return custom_response(_("Invalid TAC, Enter 8 digit TAC."), RESPONSES.get('BAD_REQUEST'), MIME_TYPES.get('JSON'))
                    else:
                        return custom_response(_("Upload file or enter TAC."), status=RESPONSES.get('BAD_REQUEST'), mimetype=MIME_TYPES.get('JSON'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving summary.")
            app.logger.exception(e)
            return custom_response(_("Failed to verify bulk imeis."), RESPONSES.get('SERVICE_UNAVAILABLE'), MIME_TYPES.get('JSON'))


