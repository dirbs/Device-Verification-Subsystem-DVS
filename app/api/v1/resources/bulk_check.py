import os

import pandas as pd
import requests
from flask import request, send_from_directory

from app import Root, GlobalConfig, UploadDir, AllowedFiles, version
from ..assets.error_handling import *
from ..assets.responses import responses, mime_types

upload_folder = os.path.join(app.root_path, UploadDir)


class BulkCheck:

    @staticmethod
    def build_summary(imeis_list):
        try:
            records = []
            response = {}
            invalid_imeis = 0
            for imei in imeis_list:
                if len(str(imei)) in range(int(GlobalConfig.get('MinImeiLength')),
                                           int(GlobalConfig.get('MaxImeiLength'))):  # imei format validation
                    tac = str(imei)[:GlobalConfig.get('TacLength')]  # slicing TAC from IMEI
                    if tac.isdigit():  # TAC format validation
                        tac_response = requests.get(
                            '{}/{}/tac/{}'.format(Root, version, tac)).json()  # dirbs core TAC api call
                        imei_response = requests.get(
                            '{}/{}/imei/{}'.format(Root, version, imei)).json()  # dirbs core IMEI api call
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
                    complaint_status = dict()
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
        except Exception as e:
            raise e

    @staticmethod
    def get():
        try:
            file = request.files.get('file')
            if file:
                if file.filename != '':
                        if file and '.' in file.filename and \
                                file.filename.rsplit('.', 1)[1].lower() in AllowedFiles:  # input file type validation
                            imei_df = pd.read_csv(file, delimiter='\t', encoding='utf-8',
                                                  header=None)  # load file to dataframe
                            if not imei_df.empty and \
                                    int(GlobalConfig['MinFileContent']) < imei_df.shape[1] < int(GlobalConfig['MaxFileContent']):  # input file content validation
                                filtered_imeis = imei_df.T.drop_duplicates().T.values.tolist()[0]  # drop duplicate IMEIs from list
                                response = BulkCheck.build_summary(filtered_imeis)
                                return Response(json.dumps(response), status=responses.get('ok'), mimetype=mime_types.get('json'))
                        else:
                            return custom_response("Bad file format", responses.get('bad_request'), mime_types.get('json'))
                else:
                    return custom_response('No file selected.', responses.get('bad_request'), mime_types.get('json'))
            else:  # check for tac if file not uploaded
                tac = request.form.get('tac')
                if tac:
                    if tac.isdigit() and len(tac) == int(GlobalConfig['TacLength']):
                        tac = tac + str(GlobalConfig['MinImeiRange'])
                        imei_list = [int(tac) + x for x in range(int(GlobalConfig['MaxImeiRange']))]
                        print(imei_list)
                        response = BulkCheck.build_summary(imei_list)
                        return Response(json.dumps(response), status=200, mimetype='application/json')
                    else:
                        return custom_response("Invalid TAC", responses.get('bad_request'), mime_types.get('json'))
                else:
                    return custom_response("Upload file or enter TAC.", status=responses.get('bad_request'), mimetype=mime_types.get('json'))
        except Exception as e:
            app.logger.info("Error occurred while retrieving summary.")
            app.logger.exception(e)
            return custom_response("Failed to verify bulk imeis.", responses.get('service_unavailable'), mime_types.get('json'))

    @staticmethod
    def send_file():
        try:
            return send_from_directory(directory=upload_folder, filename='summary.tsv')  # returns file when user wnats to download non compliance report
        except Exception as e:
            app.logger.info("Error occurred while downloading non compliant report.")
            app.logger.exception(e)
            return custom_response("Failed to verify bulk imeis.", responses.get('service_unavailable'), mime_types.get('json'))
