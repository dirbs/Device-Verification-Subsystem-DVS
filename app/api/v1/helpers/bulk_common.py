"""
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
    The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
    Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
    This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

import os
from app import session
from requests import ConnectionError
from app.api.v1.handlers.error_handling import *
from ..helpers.common import CommonResources

from threading import Thread
from math import ceil

import pandas as pd
import uuid


class BulkCommonResources:
    """Common resources for bulk request."""

    @staticmethod
    def chunked_data(imeis_list):
        """Divide IMEIs into batches of 1000 and chunks for multi threading."""
        try:
            if imeis_list:
                imeis_list = list(imeis_list[i:i + app.config['system_config']['global']['ImeiBatchSize']] for i in
                                  range(0, len(imeis_list), app.config['system_config']['global']['ImeiBatchSize']))
                chunksize = int(ceil(len(imeis_list) / app.config['system_config']['global']['NoOfThreads']))
                imeis_list = list(imeis_list[i:i + chunksize] for i in range(0, len(imeis_list), chunksize))
                return imeis_list
            return imeis_list
        except Exception as e:
            app.logger.info("Error occurred while making chunks of data.")
            app.logger.exception(e)
            raise e

    @staticmethod
    def start_threads(imeis_list, invalid_imeis):
        """Process IMEIs simultaneously by starting multiple threads at a time."""
        try:
            thread_list = []
            records = []
            unprocessed_imeis = []
            for imei in imeis_list:
                thread_list.append(Thread(target=BulkCommonResources.get_records, args=(imei, records, unprocessed_imeis)))

            # start threads for all imei chunks
            for x in thread_list:
                x.start()

            # stop all threads on completion
            for t in thread_list:
                t.join()

            if len(unprocessed_imeis)>0:
                records, unprocessed_imeis = BulkCommonResources.retry(records, unprocessed_imeis)

            return records, invalid_imeis, unprocessed_imeis
        except Exception as e:
            app.logger.info("Error occurred while multi threading.")
            app.logger.exception(e)
            raise e

    # get records from core system
    @staticmethod
    def get_records(imeis, records, unprocessed_imeis):
        """Compile IMEIs batch responses from DIRBS core system."""
        try:
            while imeis:
                imei = imeis.pop(-1)  # pop the last item from queue
                try:
                    if imei:
                        batch_req = {
                            "imeis": imei
                        }
                        headers = {'content-type': 'application/json', 'charset': 'utf-8', 'keep_alive': 'false'}
                        imei_response = session.post('{}/{}/imei-batch'.format(app.config['dev_config']['dirbs_core']['BaseUrl'], app.config['dev_config']['dirbs_core']['Version']),
                                                     data=json.dumps(batch_req),
                                                     headers=headers)  # dirbs core batch api call
                        if imei_response.status_code == 200:
                            imei_response = imei_response.json()
                            records.extend(imei_response['results'])
                        else:
                            app.logger.info("imei batch failed due to status other than 200")
                            unprocessed_imeis.append(imei)  # in case of connection error append imei count to unprocessed IMEIs list
                    else:
                        continue
                except (ConnectionError, Exception) as e:
                    unprocessed_imeis.append(imei)  # in case of connection error append imei count to unprocessed IMEIs list
                    app.logger.exception(e)
        except Exception as error:
            raise error

    @staticmethod
    def retry(records, unprocessed_imeis):
        """Retry failed IMEI batches."""
        try:
            retry = app.config['system_config']['global'].get('retry')

            while retry and len(unprocessed_imeis) > 0:
                threads = []
                retry = retry - 1
                imeis_list = unprocessed_imeis
                unprocessed_imeis = []
                chunksize = int(ceil(len(imeis_list) / app.config['system_config']['global']['NoOfThreads']))
                imeis_list = list(imeis_list[i:i + chunksize] for i in
                                  range(0, len(imeis_list), chunksize))  # make 100 chunks for 1 million imeis
                for imeis in imeis_list:
                    threads.append(Thread(target=BulkCommonResources.get_records, args=(imeis, records, unprocessed_imeis)))
                for x in threads:
                    x.start()

                for t in threads:
                    t.join()

            return records, unprocessed_imeis
        except Exception as e:
            app.logger.info("Error occurred while retrying.")
            app.logger.exception(e)
            raise e

    @staticmethod
    def build_summary(records, invalid_imeis, unprocessed_imeis):
        """Generate summary for DVS bulk records."""
        try:
            response = {}
            if records:
                result = pd.DataFrame(records)  # main dataframe for results

                registration_list = pd.DataFrame(
                    list(result['registration_status']))  # dataframe for registration status
                pending_reg_count = len(registration_list.loc[registration_list['provisional_only'] == True])

                stolen_list = pd.DataFrame(list(result['stolen_status']))  # dataframe for stolen status
                pending_stolen_count = len(stolen_list.loc[stolen_list['provisional_only'] == True])

                count_per_condition = {}

                realtime = pd.DataFrame(list(result['realtime_checks']))  # dataframe of realtime checks

                classification_states = pd.DataFrame(
                    list(result['classification_state']))  # dataframe of classifcation states

                blocking_condition = pd.DataFrame(
                    list(classification_states['blocking_conditions']))  # dataframe of blocking conditions

                info_condition = pd.DataFrame(
                    list(classification_states['informative_conditions']))  # dataframe for informative conditions

                #  IMEI count per blocking condition
                count_per_condition, block = BulkCommonResources.count_condition(count=count_per_condition,
                                                                                 conditions=blocking_condition)

                # IMEI count per informative condition
                count_per_condition, info = BulkCommonResources.count_condition(count=count_per_condition,
                                                                                conditions=info_condition)

                all_conditions = pd.concat([block, info, realtime],
                                           axis=1).transpose()  # concatenate dataframes for all conditions

                # count IMEIs which does not meeting any condition
                no_condition = BulkCommonResources.no_condition_count(all_conditions)

                # processing compliant status for all IMEIs
                non_compliant, filename, report = BulkCommonResources.generate_compliant_report(records)

                # summary for bulk verify IMEI
                response["unprocessed_imeis"] = sum(len(imei) for imei in unprocessed_imeis)
                response["invalid_imei"] = invalid_imeis
                response["pending_registration"] = pending_reg_count
                response["pending_stolen_verification"] = pending_stolen_count
                response["verified_imei"] = len(records)
                response["count_per_condition"] = count_per_condition
                response["no_condition"] = no_condition
                response["non_complaint"] = non_compliant
                response["compliant_report_name"] = filename

            return response
        except Exception as e:
            raise e

    # generate compliant report and count non compliant IMEIs
    @staticmethod
    def generate_compliant_report(records):
        """Return non compliant report for DVS bulk request."""
        try:
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
                complaint_report.to_csv(os.path.join(app.config['dev_config']['UPLOADS']['report_dir'], report_name),
                                        sep='\t')  # writing non compliant statuses to .tsv file
            return non_complaint, report_name, complaint_report
        except Exception as e:
            app.logger.info("Error occurred while generating report.")
            app.logger.exception(e)
            raise e

    # count per condition classification state
    @staticmethod
    def count_condition(conditions, count):
        """Helper functions to generate summary, returns IMEI count per condition."""
        try:
            condition = []
            transponsed = conditions.transpose()
            for c in transponsed:
                cond = {}
                for i in transponsed[c]:
                    cond[i["condition_name"]] = i["condition_met"]  # serialize conditions in list of dictionaries
                condition.append(cond)
            condition = pd.DataFrame(condition)
            for key in condition:  # iterate over list
                count[key] = len(condition[condition[key]])  # count meeting conditions
            return count, condition
        except Exception as e:
            app.logger.info("Error occurred while generating summary - method=count condition.")
            app.logger.exception(e)
            raise e

    # count IMEIs meeting no condition
    @staticmethod
    def no_condition_count(all_conditions):
        """Helper functions to generate summary, returns count of IMEI satisfying no conditions."""
        try:
            no_conditions = 0
            for key in all_conditions:
                if (~all_conditions[key]).all():
                    no_conditions += 1
            return no_conditions
        except Exception as e:
            app.logger.info("Error occurred while generating summary - method=no_condition_count.")
            app.logger.exception(e)
            raise e
