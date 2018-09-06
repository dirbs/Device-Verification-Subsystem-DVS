###################################################
#                                                 #
# Copyright (c) 2018 Qualcomm Technologies, Inc.  #
#                                                 #
# All rights reserved.                            #
#                                                 #
###################################################

import os

from app import report_dir
from ..resources.common import CommonResources
from .bulk_summary import BulkSummary

import pandas as pd
import uuid

class DrsBulkSummary:

    # generate compliant report and count non compliant IMEIs
    @staticmethod
    def generate_compliant_report(records):
        non_compliant = 0
        compliant = 0
        provisionally_compliant = 0
        provisionally_non_compliant = 0
        complaint_report = []
        for key in records:
            status = CommonResources.compliance_status(resp=key, status_type="bulk", imei=key['imei_norm'])
            status['stolen_status'] = "Pending Stolen Verification" if key['stolen_status']['provisional_only'] else "Not Stolen" if key['stolen_status']['provisional_only'] is None else "Stolen"
            status['seen_on_network'] = key['realtime_checks']['ever_observed_on_network']
            complaint_report.append(status)
            if "Provisionally Compliant" in status['status']:
                provisionally_compliant += 1
            elif "Provisionally non compliant" in status['status']:
                provisionally_non_compliant += 1
            elif status['status']=="Compliant (Active)" or status['status']=="Compliant (Inactive)":
                compliant += 1
            elif status['status']=="Non compliant":
                non_compliant += 1

        complaint_report = pd.DataFrame(complaint_report)  # dataframe of compliant report
        report_name = 'compliant_report' + str(uuid.uuid4()) + '.tsv'
        complaint_report.to_csv(os.path.join(report_dir, report_name), sep='\t')  # writing non compliant statuses to .tsv file
        data = {
            "non_compliant": non_compliant,
            "compliant": compliant,
            "provisionally_non_compliant": provisionally_non_compliant,
            "provisionally_compliant": provisionally_compliant,
            "filename": report_name
        }
        return data

    @staticmethod
    def build_summary(records):
        try:
            response = {}
            if records:
                result = pd.DataFrame(records)  # main dataframe for results

                stolen_list = pd.DataFrame(list(result['stolen_status']))   # dataframe for stolen status
                pending_stolen_count = len(stolen_list.loc[stolen_list['provisional_only']==True])

                stolen = len(stolen_list.loc[stolen_list['provisional_only']==False])

                count_per_condition = {}

                realtime = pd.DataFrame(list(result['realtime_checks']))  # dataframe of realtime checks
                seen_on_network = len(realtime.loc[realtime['ever_observed_on_network']==True])

                blocking_condition = pd.DataFrame(i['blocking_conditions'] for i in result['classification_state'] if i['blocking_conditions'])  # dataframe for blocking conditions

                info_condition = pd.DataFrame(i['informative_conditions'] for i in result['classification_state'] if i['informative_conditions'])  # dataframe for informative conditions

                #  IMEI count per blocking condition
                count_per_condition, block = BulkSummary.count_condition(count=count_per_condition, conditions=blocking_condition)

                # IMEI count per informative condition
                count_per_condition, info = BulkSummary.count_condition(count=count_per_condition, conditions=info_condition)

                # processing compliant status for all IMEIs
                data = DrsBulkSummary.generate_compliant_report(records)

                # summary for bulk verify IMEI
                response['provisional_stolen'] = pending_stolen_count
                response['verified_imei'] = len(records)
                response['count_per_condition'] = count_per_condition
                response['non_complaint'] = data['non_compliant']
                response['complaint'] = data['compliant']
                response['provisional_non_compliant'] = data['provisionally_non_compliant']
                response['provisional_compliant'] = data['provisionally_compliant']
                response['seen_on_network'] = seen_on_network
                response['stolen'] = stolen
                response['compliant_report_name'] = data['filename']

            return response
        except Exception as e:
            raise e
