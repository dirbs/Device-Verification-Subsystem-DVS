import os
import re
from app import Root, GlobalConfig, UploadDir, version, session, celery
from ..assets.error_handling import *

from threading import Thread
import pandas as pd
import uuid

upload_folder = os.path.join(app.root_path, UploadDir)


class BulkSummary:
    @staticmethod
    def count_per_blocking_condition(blocking_conditions):
        count_per_condition = {}
        for key in blocking_conditions:
            count_per_condition[key] = len(blocking_conditions[blocking_conditions[key]])
        return count_per_condition

    @staticmethod
    def no_condition_count(all_conditions):
        no_conditions = 0
        for key in all_conditions:
            if (~all_conditions[key]).all():
                no_conditions += 1
        return no_conditions

    @staticmethod
    def count_per_info_condition(count_per_condition, informative_condition):
        if not informative_condition.empty:
            for key in informative_condition:
                count_per_condition[key] = len(informative_condition[informative_condition[key]])
        return count_per_condition

    @staticmethod
    def generate_compliant_report(blocking_conditions, records):
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
        report_name = "report not generated."
        if non_complaint != 0:
            report_name = 'compliant_report'+str(uuid.uuid4())+'.tsv'
            complaint_report.to_csv(os.path.join(upload_folder, report_name),
                                    sep='\t')  # writing non compliant statuses to .tsv file
        return non_complaint, report_name

    @staticmethod
    def get_records(imeis, tac_response, records, invalid_imeis):
        for imei in imeis:
            if len(str(imei)) in range(int(GlobalConfig.get('MinImeiLength')),
                                       int(GlobalConfig.get('MaxImeiLength'))) \
                    and re.match(r'^[a-fA-F0-9]{14,16}$', str(imei)) is not None:  # imei format validation
                imei_response = session.get('{}/{}/imei/{}'.format(Root, version, imei))  # dirbs core IMEI api call
                if imei_response.status_code == 200:
                    imei_response = imei_response.json()
                    full_status = dict(tac_response, **imei_response)
                    records.append(full_status)
            else:
                invalid_imeis[0] = invalid_imeis[0] + 1  # increment invalid IMEI count in case of IMEI validation failure

        return {"records": records, "invalid_imeis": invalid_imeis[0]}

    @staticmethod
    def get_imei_records(imeis, records, invalid_imeis):
        for imei in imeis:
            if len(str(imei)) in range(int(GlobalConfig.get('MinImeiLength')),
                                       int(GlobalConfig.get('MaxImeiLength'))) \
                    and re.match(r'^[a-fA-F0-9]{14,16}$', str(imei)) is not None:  # imei format validation
                tac = str(imei)[:GlobalConfig.get('TacLength')]  # slicing TAC from IMEI
                if tac.isdigit():
                    tac_response = session.get('{}/{}/tac/{}'.format(Root, version, tac))  # dirbs core TAC api call
                    imei_response = session.get('{}/{}/imei/{}'.format(Root, version, imei))  # dirbs core IMEI api call
                    if tac_response.status_code == 200 and imei_response.status_code == 200:
                        tac_response = tac_response.json()
                        imei_response = imei_response.json()
                        full_status = dict(tac_response, **imei_response)
                        records.append(full_status)
                else:
                    imei_response = session.get('{}/{}/imei/{}'.format(Root, version, imei))  # dirbs core IMEI api call
                    tac_response = {"gsma": None, "tac": tac}
                    if imei_response.status_code == 200:
                        imei_response = imei_response.json()
                        full_status = dict(tac_response, **imei_response)
                        records.append(full_status)
            else:
                invalid_imeis[0] = invalid_imeis[0] + 1  # increment invalid IMEI count in case of IMEI validation failure
        return records, invalid_imeis[0]

    @staticmethod
    def start_threads(imeis_list, type, tac_response=None):
        response = {}
        threads = []
        records = []
        invalid_imeis = [0]
        if type == "tac":
            for imei in imeis_list:
                threads.append(Thread(target=BulkSummary.get_records, args=(imei, tac_response, records, invalid_imeis)))
        else:
            for imei in imeis_list:
                threads.append(Thread(target=BulkSummary.get_imei_records, args=(imei, records, invalid_imeis)))

        for x in threads:
            x.start()

        for t in threads:
            t.join()

        summary = Thread(target=BulkSummary.build_summary, args=(response, records, invalid_imeis))
        summary.start()
        summary.join()

        return response

    @staticmethod
    @celery.task
    def get_summary(imeis_list, type, tac=None):
        try:
            imeis_list = list(imeis_list[i:i + 1000] for i in range(0, len(imeis_list), 1000))
            if type == "tac":
                tac_response = session.get('{}/{}/tac/{}'.format(Root, version, tac))  # dirbs core TAC api call
                if tac_response.status_code != 200:
                    tac_response = {"gsma": None, "tac": tac}
                else:
                    tac_response = tac_response.json()

                response = BulkSummary.start_threads(imeis_list=imeis_list, tac_response=tac_response, type=type)

                return response

            else:
                response = BulkSummary.start_threads(imeis_list=imeis_list, type=type)

                return response

        except Exception as e:
            raise e


    @staticmethod
    def build_summary(response, records, invalid_imeis):  # TODO: implement bulk check through core's bulk api
        try:
            records = pd.DataFrame(records)  # dataframe of all dirbs core api responses
            verified_imeis = len(records[records['gsma'].notna()])  # verified IMEI count
            classification_states = pd.DataFrame(list(records['classification_state']))  # dataframe of classifcation states
            blocking_conditions = pd.DataFrame(list(classification_states['blocking_conditions']))  # dataframe of blocking conditions
            informative_condition = pd.DataFrame(list(classification_states['informative_conditions']))  # dataframe of informative conditions
            realtime_checks = pd.DataFrame(list(records['realtime_checks']))  # dataframe of realtime checks
            is_paired = pd.DataFrame(list(records['is_paired']))  # dataframe of is paired information
            all_conditions = pd.concat([blocking_conditions, informative_condition, realtime_checks, is_paired], axis=1).transpose()

            #  IMEI count per blocking condition
            count_per_condition = BulkSummary.count_per_blocking_condition(blocking_conditions)

            # count IMEIs which does not meeting any condition
            count_per_condition['no_condition'] = BulkSummary.no_condition_count(all_conditions)

            # IMEI count per informative condition
            count_per_condition = BulkSummary.count_per_info_condition(count_per_condition, informative_condition)

            # processing compliant status for all IMEIs
            non_compliant, filename = BulkSummary.generate_compliant_report(blocking_conditions, records)

            # summary for bulk verify IMEI
            response['invalid_imei'] = invalid_imeis[0]
            response['verified_imei'] = verified_imeis
            response['count_per_condition'] = count_per_condition
            response['non_complaint'] = non_compliant
            response['compliant_report_name'] = filename

            return response
        except Exception as e:
            raise e
