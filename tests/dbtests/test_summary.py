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

from app.api.v1.models.summary import Summary


def test_summary_insert():
    """Test summary insertion"""
    summary_data = {
        "tracking_id": '1234567-asdfgh-890123',
        "input": '67890123',
        "input_type": "tac",
        "status": 'PENDING'
    }
    summary_record = Summary.create(summary_data)
    assert summary_record is not None

    result = Summary.find_by_input("67890123")
    assert result is not None

    result = Summary.find_by_trackingid("1234567-asdfgh-890123")
    assert result is not None


def test_summary_update():
    response = {
        "state": "SUCCESS",
        "result": {"count_per_condition":
                       {"gsma_not_found": 0,
                        "local_stolen": 0,
                        "duplicate_daily_avg": 0,
                        "duplicate_mk1": 0,
                        "malformed_imei": 0,
                        "not_on_registration_list": 0},
                   "verified_imei": 8,
                   "non_complaint": 8,
                   "no_condition": 7,
                   "unprocessed_imeis": 0,
                   "pending_registration": 0,
                   "compliant_report_name": "compliant_report707a6838-0ea8-4a12-a8ff-bd6f36d5af5e.tsv",
                   "invalid_imei": 3,
                   "pending_stolen_verification": 0}
    }
    data = {"response": response, "task_id": "1234567-asdfgh-890123"}
    resp = Summary.update("67890123", response['state'], data)
    assert resp is None

    resp = Summary.find_by_input("67890123")
    assert resp['status'] == 'SUCCESS'
