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

import os, re
import magic
from shutil import rmtree
import tempfile
from app import GlobalConfig, task_dir, report_dir, AllowedExt, AllowedTypes, celery

from ..assets.error_handling import *
from ..assets.responses import responses, mime_types
from ..helpers.bulk_summary import BulkSummary
from ..helpers.drs_bulk import DrsBulkSummary

from flask import request, send_from_directory


class BulkCheck:

    @staticmethod
    @celery.task
    def get_summary(imeis_list, invalid_imeis, system):
        try:
            threads = []
            records = []
            unprocessed_imeis = []
            retry_count = GlobalConfig.get('Retry')
            imeis_chunks = BulkSummary.chunked_data(imeis_list)
            records, invalid_imeis, unprocessed_imeis = BulkSummary.start_threads(imeis_list=imeis_chunks,
                                                                                  invalid_imeis=invalid_imeis,
                                                                                  thread_list=threads, records=records,
                                                                                  unprocessed_imeis=unprocessed_imeis,
                                                                                  retry=retry_count)
            # send records for summary generation
            if system=='drs':
                response = DrsBulkSummary.build_summary(records)
            else:
                response = BulkSummary.build_summary(records, invalid_imeis, unprocessed_imeis)

            return response
        except Exception as e:
            raise e

    @staticmethod
    def summary():
        try:
            invalid_imeis = 0
            filtered_list = []
            task_file = open(os.path.join(task_dir, 'task_ids.txt'), 'a+')
            file = request.files.get('file')
            if file:
                tempdir = tempfile.mkdtemp()
                filepath = os.path.join(tempdir, file.filename)
                file.save(filepath)
                try:
                    mimetype = magic.from_file(filepath, mime=True)
                    if file.filename != '':
                        if mimetype in AllowedTypes and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in AllowedExt:  # validate file type
                            file = open(filepath, 'r')
                            imeis = list(set(line.strip() for line in file.read().split('\n') if line))
                            if imeis and int(GlobalConfig['MinFileContent']) <= len(imeis) <= int(GlobalConfig['MaxFileContent']):  # validate file content length
                                for imei in imeis:
                                    if re.match(r'^[a-fA-F0-9]{14,16}$', imei) is None:
                                        invalid_imeis += 1
                                    else:
                                        filtered_list.append(imei)
                                imeis_list = filtered_list
                                if imeis_list:
                                    response = BulkCheck.get_summary.apply_async((imeis_list, invalid_imeis, 'dvs'))
                                    data = {
                                        "message": "You can track your request using this id",
                                        "task_id": response.id
                                    }
                                    task_file.write(response.id+'\n')
                                    return Response(json.dumps(data), status=200, mimetype='application/json')
                                else:
                                    return custom_response("File contains malformed content",
                                                           status=responses.get('bad_request'),
                                                           mimetype=mime_types.get('json'))
                            else:
                                return custom_response("File must have minimum "+str(GlobalConfig['MinFileContent'])+" or maximum "+str(GlobalConfig['MaxFileContent'])+" IMEIs.", status=responses.get('bad_request'), mimetype=mime_types.get('json'))
                        else:
                            return custom_response("System only accepts tsv/txt files.", responses.get('bad_request'), mime_types.get('json'))
                    else:
                        return custom_response('No file selected.', responses.get('bad_request'),
                                               mime_types.get('json'))
                finally:
                    rmtree(tempdir)

            else:  # check for tac if file not uploaded
                tac = request.form.get('tac')
                if tac:
                    if tac.isdigit() and len(tac) == int(GlobalConfig['TacLength']):
                        imei = tac + str(GlobalConfig['MinImeiRange'])
                        imei_list = [str(int(imei) + x) for x in range(int(GlobalConfig['MaxImeiRange']))]
                        response = BulkCheck.get_summary.apply_async((imei_list, invalid_imeis, 'dvs'))
                        data = {
                            "message": "You can track your request using this id",
                            "task_id": response.id
                        }
                        task_file.write(response.id+'\n')
                        return Response(json.dumps(data), status=200, mimetype='application/json')
                    else:
                        return custom_response("Invalid TAC, Enter 8 digit TAC.", responses.get('bad_request'), mime_types.get('json'))
                else:
                    return custom_response("Upload file or enter TAC.", status=responses.get('bad_request'), mimetype=mime_types.get('json'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving summary.")
            app.logger.exception(e)
            return custom_response("Failed to verify bulk imeis.", responses.get('service_unavailable'), mime_types.get('json'))

    @staticmethod
    def drs_summary():
        try:
            task_file = open(os.path.join(task_dir, 'task_ids.txt'), 'a+')
            file = request.files.get('file')
            if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in AllowedExt:  # validate file type
                imeis = list(set(line.decode('ascii', errors='ignore') for line in (l.strip() for l in file) if line))
                response = BulkCheck.get_summary.apply_async((imeis, "file", 'drs'))
                data = {
                    "message": "You can track your request using this id",
                    "task_id": response.id
                }
                task_file.write(response.id + '\n')
                return Response(json.dumps(data), status=200, mimetype='application/json')
            else:
                return custom_response("System only accepts tsv/txt files.", responses.get('bad_request'),
                                       mime_types.get('json'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving summary.")
            app.logger.exception(e)
            return custom_response("Failed to verify bulk imeis.", responses.get('service_unavailable'),
                                   mime_types.get('json'))

    @staticmethod
    def send_file(filename):
        try:
            return send_from_directory(directory=report_dir, filename=filename)  # returns file when user wnats to download non compliance report
        except Exception as e:
            app.logger.info("Error occurred while downloading non compliant report.")
            app.logger.exception(e)
            return custom_response("Compliant report not found.", responses.get('ok'), mime_types.get('json'))

    @staticmethod
    def check_status(task_id):
        with open(os.path.join(task_dir, 'task_ids.txt'), 'r') as f:
            if task_id in list(f.read().splitlines()):
                task = BulkCheck.get_summary.AsyncResult(task_id)
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

        return Response(json.dumps(response), status=200, mimetype='application/json')

