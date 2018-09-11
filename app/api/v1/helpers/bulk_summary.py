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

from app import Root, report_dir, version, session, GlobalConfig
from requests import ConnectionError
from ..resources.common import CommonResources
from ..assets.error_handling import *

from threading import Thread
from math import ceil

import pandas as pd
import uuid

class BulkSummary:

    # count per condition classification state
    @staticmethod
    def count_condition(conditions, count):
        condition = []
        transponsed = conditions.transpose()
        for c in transponsed:
            cond = {}
            for i in transponsed[c]:
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
            if "Compliant" not in status['status']:
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
            for imei in range(len(imeis)):
                imei = imeis.pop(-1)  # pop the last item from queue
                try:
                    if imei:
                        batch_req = {
                            "imeis": imei
                        }
                        headers = {'content-type': 'application/json', 'charset': 'utf-8'}
                        imei_response = session.post('{}/{}/imei-batch'.format(Root, version), data=json.dumps(batch_req), headers=headers)  # dirbs core batch api call
                        if imei_response.status_code == 200:
                            imei_response = imei_response.json()
                            records.extend(imei_response['results'])
                        print(len(records))
                    else:
                        continue
                except ConnectionError as e:
                    unprocessed_imeis.append(len(imei))  # in case of connection error append imei count to unprocessed IMEIs list
                    app.logger.exception(e)
        except Exception as error:
            raise error

    @staticmethod
    def start_threads(imeis_list, invalid_imeis):
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

        return records, invalid_imeis, unprocessed_imeis

    @staticmethod
    def chunked_data(imeis_list):
        chunksize = int(ceil(len(imeis_list) / GlobalConfig['NoOfThreads']))
        imeis_list = list(imeis_list[i:i + chunksize] for i in range(0, len(imeis_list), chunksize))  # make 100 chunks for 1 million imeis
        imeis_chunks = []
        for imeis in imeis_list:
            imeis_chunks.append(list(imeis[i:i + GlobalConfig['ImeiBatchSize']] for i in range(0, len(imeis), GlobalConfig['ImeiBatchSize'])))
        return imeis_chunks

    @staticmethod
    def build_summary(records, invalid_imeis, unprocessed_imeis):
        try:
            response = {}
            if records:
                result = pd.DataFrame(records)  # main dataframe for results

                registration_list = pd.DataFrame(list(result['registration_status']))  # dataframe for registration status
                pending_reg_count = len(registration_list.loc[registration_list['provisional_only']==True])

                stolen_list = pd.DataFrame(list(result['stolen_status']))   # dataframe for stolen status
                pending_stolen_count = len(stolen_list.loc[stolen_list['provisional_only']==True])

                count_per_condition = {}

                realtime = pd.DataFrame(list(result['realtime_checks']))  # dataframe of realtime checks

                classification_states = pd.DataFrame(list(result['classification_state']))  # dataframe of classifcation states

                blocking_condition = pd.DataFrame(list(classification_states['blocking_conditions']))  # dataframe of blocking conditions

                info_condition = pd.DataFrame(list(classification_states['informative_conditions']))  # dataframe for informative conditions

                #  IMEI count per blocking condition
                count_per_condition, block = BulkSummary.count_condition(count=count_per_condition, conditions=blocking_condition)

                # IMEI count per informative condition
                count_per_condition, info = BulkSummary.count_condition(count=count_per_condition, conditions=info_condition)

                all_conditions = pd.concat([block, info, realtime], axis=1).transpose()  # concatenate dataframes for all conditions

                # count IMEIs which does not meeting any condition
                no_condition = BulkSummary.no_condition_count(all_conditions)

                # processing compliant status for all IMEIs
                non_compliant, filename, report = BulkSummary.generate_compliant_report(records)

                # summary for bulk verify IMEI
                response['unprocessed_imeis'] = sum(unprocessed_imeis)
                response['invalid_imei'] = invalid_imeis
                response['pending_registration'] = pending_reg_count
                response['pending_stolen_verification'] = pending_stolen_count
                response['verified_imei'] = len(records)
                response['count_per_condition'] = count_per_condition
                response['no_condition'] = no_condition
                response['non_complaint'] = non_compliant
                response['compliant_report_name'] = filename

            return response
        except Exception as e:
            raise e
