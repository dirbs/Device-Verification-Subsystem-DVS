import os
import requests
import json
import pandas as pd
from flask import request, send_from_directory, jsonify, Response
from app import config
from ..assets.error_handling import *

dirbs = config.get("Development", "dirbs_core")
allowed_ext = config.get("Development", "allowed_extensions")
upload_folder = os.path.join(app.root_path, config.get("Development", "upload_folder"))

class BulkCheck():

    def get(self):
        try:
            if 'file' not in request.files:
                return not_found()

            file = request.files['file']

            if file.filename == '':
                return custom_error_handeling("File not found", 404, 'application/json')

            if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_ext:
                records = []
                imei_df = pd.read_csv(file, delimiter='\t', encoding='utf-8', header=None)
                filtered_imeis = imei_df.T.drop_duplicates()
                print(filtered_imeis.T.values.tolist()[0])
                # with open(os.path.join(upload_folder, "summary.tsv"), 'a') as summary:
                for imei in filtered_imeis.T.values.tolist()[0]:
                    # print(type(imei), imei)
                    if len(str(imei)) in range(14, 16):
                        tac = str(imei)[:8]
                        if tac.isdigit():
                            tac_response = requests.get(dirbs + '/coreapi/api/v1/tac/{}'.format(tac)).json()
                            imei_response = requests.get(dirbs + '/coreapi/api/v1/imei/{}'.format(imei)).json()
                            full_status = dict(tac_response, **imei_response)
                            print(full_status)
                            records.append(full_status)
                # records = pd.DataFrame(records)
                # realtime_checks = pd.DataFrame(list(records['realtime_checks']))
                # print("valid IMEIs", len(realtime_checks[realtime_checks['gsma_not_found']==False]))
                # classification_states = pd.DataFrame(list(records['classification_state']))
                # print("duplicates", len(classification_states[classification_states['blocking_conditions']['duplicates']==False]))
                # summary.close()
                # return send_from_directory(directory=upload_folder, filename='summary.tsv')
                return Response(json.dumps(records), status=200, mimetype='application/json')
                # return None
            else:
                return custom_error_handeling("Bad file format", 400, 'application/json')
        except Exception as e:
            print(e)
