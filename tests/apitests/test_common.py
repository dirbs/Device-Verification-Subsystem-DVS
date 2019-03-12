"""
 Copyright (c) 2018 Qualcomm Technologies, Inc.                                                                      #
                                                                                                                     #
 All rights reserved.                                                                                                #
                                                                                                                     #
 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the      #
 limitations in the disclaimer below) provided that the following conditions are met:                                #
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following  #
   disclaimer.                                                                                                       #
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the         #
   following disclaimer in the documentation and/or other materials provided with the distribution.                  #
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or       #
   promote products derived from this software without specific prior written permission.                            #
                                                                                                                     #
 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED  #
 BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED #
 TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT      #
 SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR   #
 CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,      #
 DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,      #
 STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,   #
 EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                                  #
"""

import os
from app.api.v1.helpers.bulk_common import BulkCommonResources
from app.api.v1.helpers.scheduled import delete_files
import pandas as pd


def test_dvs_bulk_result():
    """Tests DVS bulk summary JSON response and counts."""
    task = BulkCommonResources.get_summary(['01206400000001', '35332206000303', '12344321000020', '35499405000401',
                                            '35236005000001', '01368900000001'], 0, 'dvs')
    assert task['pending_registration'] == 8 and task['invalid_imei'] == 0 and task['no_condition'] == 2 and \
           task['pending_stolen_verification'] == 7 and task['unprocessed_imeis'] == 0 and \
           task['count_per_condition']['gsma_not_found'] == 7 and task['count_per_condition']['local_stolen'] == 7 and \
           task['count_per_condition']['duplicate'] == 6 and task['count_per_condition']['not_on_registration_list'] == 7\
           and task['non_complaint'] == 14 and task['verified_imei'] == 18


def test_dvs_bulk_result_empty():
    """Tests DVS bulk summary with empty list."""
    summary = BulkCommonResources.get_summary([], 0, 'dvs')
    assert len(summary) is 0


def test_drs_bulk_result():
    """Tests DRS bulk summary JSON response and counts."""
    task = BulkCommonResources.get_summary(['01206400000001', '35332206000303', '12344321000020', '35499405000401',
                                            '35236005000001', '01368900000001'], None, 'drs')
    assert task['provisional_stolen'] == 7 and task['verified_imei'] == 18 and \
           task['count_per_condition']['gsma_not_found'] == 7 and task['count_per_condition']['local_stolen'] == 7 and \
           task['count_per_condition']['duplicate'] == 6 and task['count_per_condition']['not_on_registration_list'] == 7\
           and task['non_complaint'] == 9 and task['seen_on_network'] == 4 and task['complaint'] == 2 and \
           task['stolen'] == 7 and task['provisional_compliant'] == 2 and task['provisional_non_compliant'] == 5


def test_drs_bulk_result_empty():
    """Tests DRS bulk summary with empty list."""
    summary = BulkCommonResources.get_summary([], None, 'drs')
    assert len(summary) is 0


def test_compliant_report(app):
    """Tests DVS compliant report contents"""
    task = BulkCommonResources.get_summary(['01206400000001', '35332206000303', '12344321000020', '35499405000401',
                                            '35236005000001', '01368900000001'], 0, 'dvs')

    report = os.path.join(app.config['dev_config']['UPLOADS']['report_dir'], task['compliant_report_name'])
    task_file = pd.read_csv(report, sep='\t', index_col=0)
    task_list = task_file.to_dict(orient='records')
    assert len(task_list) == 14


def test_drs_compliant_report(app):
    """Tests DRS compliant report contents"""
    task = BulkCommonResources.get_summary(['01206400000001', '35332206000303', '12344321000020', '35499405000401',
                                            '35236005000001', '01368900000001'], None, 'drs')

    report = os.path.join(app.config['dev_config']['UPLOADS']['report_dir'], task['compliant_report_name'])
    task_file = pd.read_csv(report, sep='\t', index_col=0)
    task_list = task_file.to_dict(orient='records')
    assert len(task_list) == 18


def test_report_deletion():
    """Tests report deletion process"""
    delete_files()