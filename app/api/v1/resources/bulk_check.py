import os
import requests
import json
import pandas as pd
from flask import request, send_from_directory, Response
from app import Root, GlobalConfig, UploadDir, AllowedFiles
from ..assets.error_handling import *

upload_folder = os.path.join(app.root_path, UploadDir)

class BulkCheck():

    def build_summary(self, imeis_list):
        records = []
        response = {}
        invalid_imeis = 0
        for imei in imeis_list:
            if len(str(imei)) in range(int(GlobalConfig['MinImeiLength']),
                                       int(GlobalConfig['MaxImeiLength'])):  # imei format validation
                tac = str(imei)[:8]  # slicing TAC from IMEI
                if tac.isdigit():  # TAC format validation
                    tac_response = requests.get(
                        '{}/coreapi/api/v1/tac/{}'.format(Root, tac)).json()  # dirbs core TAC api call
                    imei_response = requests.get(
                        '{}/coreapi/api/v1/imei/{}'.format(Root, imei)).json()  # dirbs core IMEI api call
                    full_status = dict(tac_response, **imei_response)
                    records.append(full_status)
                else:
                    invalid_imeis += 1  # increment invalid imei count in case of TAC validation failure
            else:
                invalid_imeis += 1  # increment invalid IMEI count in case of IMEI validation failure
        records = pd.DataFrame(records)  # dataframe of all dirbs core api responses
        verified_imeis = len(records[records['gsma'].notna()])  # verified IMEI count
        classification_states = pd.DataFrame(list(records['classification_state']))  # dataframe of classifcation states
        blocking_conditions = pd.DataFrame(list(classification_states['blocking_conditions']))  # dataframe of blocking conditions
        informative_condition = pd.DataFrame(list(classification_states['informative_conditions']))  # dataframe of informative conditions
        realtime_checks = pd.DataFrame(list(records['realtime_checks']))  # dataframe of realtime checks
        is_paired = pd.DataFrame(list(records['is_paired']))  # dataframe of is paired information
        all_conditions = pd.concat([blocking_conditions, informative_condition, realtime_checks, is_paired], axis=1).transpose()

        #  IMEI count per blocking condition
        count_per_condition = {}
        for key in blocking_conditions:
            count_per_condition[key] = len(blocking_conditions[blocking_conditions[key]])

        # count IMEIs which does not meeting any condition
        no_conditions = 0
        for key in all_conditions:
            if (~all_conditions[key]).all():
                no_conditions += 1
        count_per_condition['no_condition'] = no_conditions

        # IMEI count per informative condition
        if not informative_condition.empty:
            for key in informative_condition:
                count_per_condition[key] = len(informative_condition[informative_condition[key]])

        # processing compliant status for all IMEIs
        compliant = blocking_conditions.transpose()

        non_complaint = 0
        complaint_report = []
        imeis = list(records['imei_norm'])
        for key in compliant:
            if compliant[key].any():
                complaint_status = {}
                complaint_status['imei'] = imeis[key]
                complaint_status['status'] = "Non complaint"
                complaint_status['reasons'] = compliant.index[compliant[key]].tolist()
                complaint_status['block_date'] = GlobalConfig['BlockDate']
                complaint_report.append(complaint_status)
                non_complaint += 1
        complaint_report = pd.DataFrame(complaint_report)  # dataframe of compliant report
        complaint_report.to_csv(os.path.join(upload_folder, "summary.tsv"),
                                sep='\t')  # writing non compliant statuses to .tsv file

        # summary for bulk verify IMEI
        response['invalid_imei'] = invalid_imeis
        response['verified_imei'] = verified_imeis
        response['count_per_condition'] = count_per_condition
        response['non_complaint'] = non_complaint
        return response

    def get(self):
        try:
            indicator = request.form.get('indicator')
            if indicator=="True":
                if 'file' not in request.files: #return not found response if file not uploaded
                    return not_found()

                file = request.files.get('file') # request file

                if file.filename == '':
                    return custom_response("File not found", 404, 'application/json')

                if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in AllowedFiles: # input file type validation
                    imei_df = pd.read_csv(file, delimiter='\t', encoding='utf-8', header=None) # load file to dataframe
                    if not imei_df.empty and imei_df.shape[0] < int(GlobalConfig['MaxFileContent']): # input file content validation
                        filtered_imeis = imei_df.T.drop_duplicates().T.values.tolist()[0] # drop dupliacte IMEIs from list
                        response = self.build_summary(filtered_imeis)
                        return Response(json.dumps(response), status=200, mimetype='application/json')
                else:
                    return custom_response("Bad file format", 400, 'application/json')
            else:
                tac = request.form.get('tac')
                if tac.isdigit() and len(tac)==8:
                    tac = tac+str(GlobalConfig['MinImeiRange'])
                    imei_list = [int(tac)+x for x in range(int(GlobalConfig['MaxImeiRange']))]
                    response = self.build_summary(imei_list)
                    return Response(json.dumps(response), status=200, mimetype='application/json')
                else:
                    return custom_response("Invalid TAC", 400, 'application/json')
        except Exception as e:
            print(e)

    def send_file(self):
        try:
            return send_from_directory(directory=upload_folder, filename='summary.tsv') # returns file when user wnats to download non compliance report
        except Exception as e:
            print(e)