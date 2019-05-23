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

import json

basic_status_api = '/api/v1/basicstatus?'


def test_basic_status_mimetype(dirbs_core_mock, mocked_captcha_call, flask_app):
    """Tests mime type and success response of API"""
    response = flask_app.get(basic_status_api+'imei=12345678901234&token=12345token&source=web')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'


def test_basic_status_request_method(flask_app):
    """Tests allowed request  methods"""
    response = flask_app.post(basic_status_api+'imei=123456789012345&token=12345token&source=web')
    assert response.status_code == 405
    response = flask_app.put(basic_status_api+'imei=123456789012345&token=12345token&source=web')
    assert response.status_code == 405
    response = flask_app.patch(basic_status_api + 'imei=123456789012345&token=12345token&source=web')
    assert response.status_code == 405
    response = flask_app.delete(basic_status_api + 'imei=123456789012345&token=12345token&source=web')
    assert response.status_code == 405


def test_basic_input_format(flask_app):
    """Test input format validation"""
    # test with no imei input
    response = flask_app.get(basic_status_api + 'imei=&token=237822372&source=web')
    assert json.loads(response.get_data(as_text=True))['messages']['imei'][0] == "Enter IMEI."

    # test with invalid source input
    response = flask_app.get(basic_status_api + 'imei=123456789012345&token=237822372&source=')
    assert json.loads(response.get_data(as_text=True))['messages']['source'][0] == "Invalid Value."

    # test with invalid imei input
    response = flask_app.get(basic_status_api + 'imei=12345ds8901234&token=237822372&source=web')
    assert json.loads(response.get_data(as_text=True))['messages']['imei'][0] == "IMEI is invalid. Enter 16 digit IMEI."


def test_basic_captcha_failure(mocked_captcha_failed_call, flask_app):
    """Test captcha failure scenario"""
    response = flask_app.get(basic_status_api+'imei=123456789012345&token=tokenforfailedcaptcha&source=web')
    assert json.loads(response.get_data(as_text=True))['message'] == "ReCaptcha Failed!"


def test_core_response_failure(dirbs_core_mock, flask_app):
    """Test failed response from core system"""
    response = flask_app.get(basic_status_api+'imei=12345678909999&token=12345token&source=web')
    assert response.status_code == 503


def test_basic_status_response(dirbs_core_mock, mocked_captcha_call, flask_app):
    """Test basic status JSON response"""
    response = flask_app.get(basic_status_api + 'imei=12345678901234&token=12345token&source=web')
    response = json.loads(response.get_data(as_text=True))
    assert response['gsma'] == {"model_name": "model", "brand": "brandsname"}
    assert response['compliant'] is not None
    assert response['compliant']['status'] == "Non compliant"
    assert response['compliant']['block_date'] == "2018-10-19"
    assert response['compliant']['inactivity_reasons'] == ["Your device is not registered", "IMEI is duplicate", "GSMA not found"]
