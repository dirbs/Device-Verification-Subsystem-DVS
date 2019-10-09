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
from app.api.v1.helpers.tasks import CeleryTasks
import pandas as pd


def test_dvs_bulk_summary():
    """Tests DVS bulk summary JSON response and counts."""
    task = CeleryTasks.get_summary(['01206400000001', '35332206000303', '12344321000020', '35499405000401',
                                            '35236005000001', '01368900000001'], 0)
    task = task['response']
    assert task['pending_registration'] == 8 and task['invalid_imei'] == 0 and task['no_condition'] == 2 and \
           task['pending_stolen_verification'] == 7 and task['unprocessed_imeis'] == 0 and \
           task['count_per_condition']['gsma_not_found'] == 7 and task['count_per_condition']['local_stolen'] == 7 and \
           task['count_per_condition']['duplicate'] == 6 and task['count_per_condition']['not_on_registration_list'] == 7\
           and task['non_complaint'] > 0 and task['verified_imei'] == 18


def test_dvs_bulk_empty_summary():
    """Tests DVS bulk summary with empty list."""
    summary = CeleryTasks.get_summary([], 0)
    assert len(summary['response']) is 0


def test_compliant_report(app):
    """Tests DVS compliant report contents"""
    task = CeleryTasks.get_summary(['01206400000001', '35332206000303', '12344321000020', '35499405000401',
                                            '35236005000001', '01368900000001'], 0)

    report = os.path.join(app.config['dev_config']['UPLOADS']['report_dir'], task['response']['compliant_report_name'])
    task_file = pd.read_csv(report, sep='\t', index_col=0)
    task_list = task_file.to_dict(orient='records')
    assert len(task_list) > 0


def test_report_deletion():
    """Tests report deletion process"""
    CeleryTasks.delete_files()
