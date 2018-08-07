import os
import re
from app import Root, report_dir, version, session, celery, GlobalConfig
from ..resources.common import CommonResources
from ..assets.error_handling import *

from threading import Thread

import pandas as pd
import uuid

class BulkSummary:

    # count per condition classification state
    @staticmethod
    def count_condition(conditions, count):
        condition = []
        for c in conditions.transpose():
            cond = {}
            for i in conditions.transpose()[c]:
                cond[i['condition_name']] = i['condition_met']  # serialize conditions in list of dictionaries
            condition.append(cond)
        condition = pd.DataFrame(condition)
        for key in condition:  # iterate over list
            count[key] = len(condition[condition[key]])  # count meeting conditions
        return count, condition

    # count IMEIs meeting no condition
    @staticmethod
    def no_condition_count(all_conditions):
        no_conditions = 0
        for key in all_conditions:
            if (~all_conditions[key]).all():
                no_conditions += 1
        return no_conditions

    # generate compliant report and count non compliant IMEIs
    @staticmethod
    def generate_compliant_report(records):
        non_complaint = 0
        complaint_report = []
        for key in records:
            status = CommonResources.compliance_status(resp=key, status_type="bulk", imei=key['imei_norm'])
            if status['status'] != 'Compliant (Active)' and status['status'] != 'Provisionally Compliant' and status['status'] != 'Compliant (Inactive)':
                complaint_report.append(status)
                non_complaint += 1
        complaint_report = pd.DataFrame(complaint_report)  # dataframe of compliant report
        report_name = "report not generated."
        if non_complaint != 0:
            report_name = 'compliant_report' + str(uuid.uuid4()) + '.tsv'
            complaint_report.to_csv(os.path.join(report_dir, report_name),
                                    sep='\t')  # writing non compliant statuses to .tsv file
        return non_complaint, report_name, complaint_report

    # get records from core v2
    @staticmethod
    def get_records(imeis, records, unprocessed_imeis):
        try:
            for imei in range(len(imeis)):  # queue not empty
                try:
                    imei = imeis.pop(-1)  # pop the last item from queue
                    batch_req = {
                        "imeis": imei
                    }
                    headers = {'content-type': 'application/json', 'charset': 'utf-8'}
                    imei_response = session.post('{}/{}/imei-batch'.format(Root, version), data=json.dumps(batch_req), headers=headers)  # dirbs core IMEI api call
                    if imei_response.status_code == 200:
                        imei_response = imei_response.json()
                        records.extend(imei_response['results'])
                except ConnectionError:
                    unprocessed_imeis.append(len(imei))  # in case of connection error append imei at first index
                    pass
        except Exception as error:
            raise error

    @staticmethod
    def start_threads(imeis_list, invalid_imeis):
        response = {}
        threads = []
        records = []
        unprocessed_imeis = []
        for imei in imeis_list:
            threads.append(Thread(target=BulkSummary.get_records, args=(imei, records, unprocessed_imeis)))

        # start threads for all imei chunks
        for x in threads:
            x.start()

        # stop all threads on completion
        for t in threads:
            t.join()

        # start thread for summary generation
        summary = Thread(target=BulkSummary.build_summary, args=(response, records, invalid_imeis, unprocessed_imeis))
        summary.start()
        summary.join()

        return response

    @staticmethod
    @celery.task
    def get_summary(imeis_list, input_type):
        try:
            invalid_imeis = 0
            filtered_list = []
            if input_type=="file":
                for imei in imeis_list:
                    if re.match(r'^[a-fA-F0-9]{14,16}$', imei) is None:
                            invalid_imeis += 1
                    else:
                        filtered_list.append(imei)

                imeis_list = filtered_list
            imeis_list = list(imeis_list[i:i + GlobalConfig['ChunkSize']] for i in range(0, len(imeis_list), GlobalConfig['ChunkSize']))  # make 100 chunks for 1 million imeis
            imeis_chunks = []
            for imeis in imeis_list:
                imeis_chunks.append(list(imeis[i:i + 1000] for i in range(0, len(imeis), 1000)))
            response = BulkSummary.start_threads(imeis_list=imeis_chunks, invalid_imeis=invalid_imeis)
            return response

        except Exception as e:
            raise e

    @staticmethod
    def build_summary(response, records, invalid_imeis, unprocessed_imeis):
        try:
            if records:
                result = pd.DataFrame(records)  # main dataframe for results
                blocking_condition = pd.DataFrame(i['blocking_conditions'] for i in result['classification_state'])  # datafame for blocking conditions
                info_condition = pd.DataFrame(i['informative_conditions'] for i in result['classification_state'])  # datafame for informative conditions

                registration_list = pd.DataFrame(list(result['registration_status']))  # datafame for registratios status
                pending_reg_count = len(registration_list.loc[registration_list['provisional_only']==True])

                stolen_list = pd.DataFrame(list(result['stolen_status']))   # datafame for stolen status
                pending_stolen_count = len(stolen_list.loc[stolen_list['provisional_only']==True])

                count_per_condition = {}

                realtime = pd.DataFrame(list(result['realtime_checks']))  # dataframe of realtime checks

                #  IMEI count per blocking condition
                count_per_condition, block = BulkSummary.count_condition(count=count_per_condition, conditions=blocking_condition)

                # IMEI count per informative condition
                count_per_condition, info = BulkSummary.count_condition(count=count_per_condition, conditions=info_condition)

                all_conditions = pd.concat([block, info, realtime], axis=1).transpose()

                # count IMEIs which does not meeting any condition
                count_per_condition['no_condition'] = BulkSummary.no_condition_count(all_conditions)

                # processing compliant status for all IMEIs
                non_compliant, filename, report = BulkSummary.generate_compliant_report(records)

                # summary for bulk verify IMEI
                response['unprocessed_imeis'] = sum(unprocessed_imeis)
                response['invalid_imei'] = invalid_imeis
                response['pending_registration'] = pending_reg_count
                response['pending_stolen_verification'] = pending_stolen_count
                response['verified_imei'] = len(records)
                response['count_per_condition'] = count_per_condition
                response['non_complaint'] = non_compliant
                response['compliant_report_name'] = filename

            return response
        except Exception as e:
            raise e
