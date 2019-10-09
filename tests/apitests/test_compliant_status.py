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

from app.api.v1.helpers.common import CommonResources


# testing compliant IMEI
def test_compliant_imei(mocked_imei_data):
    """Tests compliant IMEI"""
    compliant_imei_response = mocked_imei_data['compliant']
    response = CommonResources.compliance_status(compliant_imei_response, 'basic')
    assert "Compliant" in response['compliant']['status']


# testing compliant IMEI
def test_non_compliant_imei(mocked_imei_data):
    """Tests non compliant IMEI"""
    non_compliant_imei_response = mocked_imei_data['non_compliant_imei']
    response = CommonResources.compliance_status(non_compliant_imei_response, 'basic')
    assert "Non compliant" in response['compliant']['status']


# testing compliant IMEI
def test_p_compliant_imei(mocked_imei_data):
    """Tests provisionally compliant IMEI"""
    p_complaint_imei_response = mocked_imei_data['provisionally_compliant']
    response = CommonResources.compliance_status(p_complaint_imei_response, 'basic')
    assert "Provisionally Compliant" in response['compliant']['status']


# testing compliant IMEI
def test_p_non_compliant_imei(mocked_imei_data):
    """Tests provisionally non compliant IMEI"""
    p_non_complaint_imei_response = mocked_imei_data['provisionally_non_compliant']
    response = CommonResources.compliance_status(p_non_complaint_imei_response, 'basic')
    assert "Provisionally non compliant" in response['compliant']['status']


def test_gsma_not_found_imei(mocked_imei_data):
    """Tests IMEI meeting gsma not found condition"""
    gsma_not_found_imei_response = mocked_imei_data['gsma_not_found_imei']
    response = CommonResources.compliance_status(gsma_not_found_imei_response, 'basic')
    assert 'GSMA not found' in response['compliant']['inactivity_reasons']


def test_duplicate_imei(mocked_imei_data):
    """Tests IMEI meeting duplicate condition"""
    dupliacte_imei_response = mocked_imei_data['duplicate_imei']
    response = CommonResources.compliance_status(dupliacte_imei_response, 'basic')
    assert 'IMEI is duplicate' in response['compliant']['inactivity_reasons']


def test_local_stolen_imei(mocked_imei_data):
    """Tests IMEI meeting local stolen condition"""
    local_stolen_imei_response = mocked_imei_data['local_stolen_imei']
    response = CommonResources.compliance_status(local_stolen_imei_response, 'basic')
    assert 'Device is stolen' in response['compliant']['inactivity_reasons']


