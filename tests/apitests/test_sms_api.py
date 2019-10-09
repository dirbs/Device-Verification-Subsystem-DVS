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

import json

sms_api = '/api/v1/sms?'


def test_index_route(flask_app):
    """Tests DVS index route."""
    response = flask_app.get('/')
    assert response.status_code == 200
    assert response.data is not None


def test_sms_mimetype(dirbs_core_mock, flask_app):
    """Test sms success status and mime type."""
    response = flask_app.get(sms_api+'imei=12345678901111')
    assert response.status_code == 200
    assert response.mimetype == 'text/plain'


def test_sms_request_method(flask_app):
    """Tests sms allowed request methods"""
    response = flask_app.post(sms_api+'imei=123456789012345')
    assert response.status_code == 405
    response = flask_app.put(sms_api+'imei=123456789012345')
    assert response.status_code == 405
    response = flask_app.patch(sms_api+'imei=123456789012345')
    assert response.status_code == 405
    response = flask_app.delete(sms_api+'imei=123456789012345')
    assert response.status_code == 405


def test_sms_input_format(flask_app):
    """Test sms input format validation."""
    response = flask_app.get(sms_api+'imei=357380062x353789')
    assert response.status_code == 422
    response = flask_app.get(sms_api+'imei=')
    assert response.status_code == 422
    assert json.loads(response.get_data(as_text=True))['messages']['imei'][0] is not None


def test_core_response_failure(dirbs_core_mock, flask_app):
    """Tests SMS response in case for IMEI call failure."""
    response = flask_app.get(sms_api+'imei=12345678909999')
    assert response.status_code == 503


def test_sms_response(dirbs_core_mock, flask_app):
    """Test sms response in case of non compliant IMEI"""
    response = flask_app.get(sms_api + 'imei=12345678901111')
    assert 'STATUS:' in response.get_data(as_text=True)


def test_sms_compliant_response(dirbs_core_mock, flask_app):
    """Test sms response in case of compliant IMEI"""
    response = flask_app.get(sms_api + 'imei=12345678908888')
    assert 'STATUS:' in response.get_data(as_text=True)