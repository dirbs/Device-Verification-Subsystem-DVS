import os

from app import GlobalConfig, task_dir, report_dir, AllowedFiles

from ..assets.error_handling import *
from ..assets.responses import responses, mime_types
from ..helpers.bulk_summary import BulkSummary

from flask import request, send_from_directory


class BulkCheck:

    @staticmethod
    def summary():
        try:
            task_file = open(os.path.join(task_dir, 'task_ids.txt'), 'a+')
            file = request.files.get('file')
            if file:
                if file.filename != '':
                        if file and '.' in file.filename and \
                                file.filename.rsplit('.', 1)[1].lower() in AllowedFiles:  # validate file type
                            imeis = list(set(line.decode('ascii', errors='ignore') for line in (l.strip() for l in file) if line))
                            if imeis and int(GlobalConfig['MinFileContent']) < len(imeis) < int(GlobalConfig['MaxFileContent']):  # validate file content length
                                response = BulkSummary.get_summary.apply_async((imeis, "file"))
                                data = {
                                    "message": "You can track your request using this id",
                                    "task_id": response.id
                                }
                                task_file.write(response.id+'\n')
                                return Response(json.dumps(data), status=200, mimetype='application/json')

                            else:
                                return custom_response("File contains incorrect/no content.", status=responses.get('bad_request'), mimetype=mime_types.get('json'))
                        else:
                            return custom_response("System only accepts tsv/txt files.", responses.get('bad_request'), mime_types.get('json'))
                else:
                    return custom_response('No file selected.', responses.get('bad_request'), mime_types.get('json'))
            else:  # check for tac if file not uploaded
                tac = request.form.get('tac')
                if tac:
                    if tac.isdigit() and len(tac) == int(GlobalConfig['TacLength']):
                        imei = tac + str(GlobalConfig['MinImeiRange'])
                        imei_list = [str(int(imei) + x) for x in range(int(GlobalConfig['MaxImeiRange']))]
                        response = BulkSummary.get_summary.apply_async((imei_list, "tac"))
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
                task = BulkSummary.get_summary.AsyncResult(task_id)
                if task.state == 'SUCCESS' and task.get():
                    response = {
                        "state": task.state,
                        "result": task.get()
                    }
                elif task.state == 'PENDING':
                    # job is in progress yet
                    response = {
                        'state': task.state
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

