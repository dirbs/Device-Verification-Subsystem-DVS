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

data = {"imei": "12345678901234",
        "subscribers": {"limit": 10, "start": 1},
        "pairs": {"start": 1, "limit": 10}
        }

full_status_api_url = '/api/v1/fullstatus'


def test_fullstatus_gsma_reg(dirbs_core_mock, flask_app):
    """Test full status with GSMA and registration data"""
    response = flask_app.post(full_status_api_url, data=json.dumps(data),
                              content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'


def test_fullstatus_gsma(dirbs_core_mock, flask_app):
    """Test full status with GSMA data"""
    data = {"imei": "12345678904321",
            "subscribers": {"limit": 10, "start": 1},
            "pairs": {"start": 1, "limit": 10}
            }

    response = flask_app.post(full_status_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'


def test_fullstatus_reg(dirbs_core_mock, flask_app):
    """Test full status with registration data"""
    data = {"imei": "87654321904321",
            "subscribers": {"limit": 10, "start": 1},
            "pairs": {"start": 1, "limit": 10}
            }

    response = flask_app.post(full_status_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'


def test_fullstatus(dirbs_core_mock, flask_app):
    """Test full status with no GSMA and registration data"""
    data = {"imei": "87654321901234",
            "subscribers": {"limit": 10, "start": 1},
            "pairs": {"start": 1, "limit": 10}
            }

    response = flask_app.post(full_status_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'


def test_fullstatus_502(dirbs_core_mock, flask_app):
    """Test full status in case of GSMA and registration request failure"""
    data = {"imei": "89764532901234",
            "subscribers": {"limit": 10, "start": 1},
            "pairs": {"start": 1, "limit": 10}
            }
    response = flask_app.post(full_status_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'


def test_fullstatus_request_method(flask_app):
    """Test full status allowed methods"""
    response = flask_app.get(full_status_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    response = flask_app.put(full_status_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    response = flask_app.patch(full_status_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405
    response = flask_app.delete(full_status_api_url, data=json.dumps(data), content_type='application/json')
    assert response.status_code == 405


def test_fullstatus_input_format(flask_app):
    """Test full status input format validation."""
    response = flask_app.post(full_status_api_url,
                              data=json.dumps({"imei": "12344329x00060000", "subscribers": {"limit": 10, "start": 1},
                                               "pairs": {"start": 1, "limit": 10}}), content_type='application/json')
    assert response.status_code == 422
    assert json.loads(response.get_data(as_text=True))['messages']['imei'][0] is not None

    response = flask_app.post(full_status_api_url,
                              data=json.dumps({"imei": "", "subscribers": {"limit": 10, "start": 1},
                                               "pairs": {"start": 1, "limit": 10}}), content_type='application/json')
    assert response.status_code == 422
    assert json.loads(response.get_data(as_text=True))['messages']['imei'][0] is not None


def test_core_response_failure(dirbs_core_mock, flask_app):
    """Test full status in case of IMEI request failure"""
    response = flask_app.post(full_status_api_url,
                              data=json.dumps({"imei": "12345678909999", "subscribers": {"limit": 10, "start": 1},
                                              "pairs": {"start": 1, "limit": 10}}), content_type='application/json')
    assert response.status_code == 503


def test_full_status_response(dirbs_core_mock, flask_app):
    """Test full status JSON response"""
    response = flask_app.post(full_status_api_url, data=json.dumps({"imei": "12345678901111",
                                                                    "subscribers": {"limit": 10, "start": 1},
                                                                    "pairs": {"start": 1, "limit": 10}}),
                              content_type='application/json')
    response = json.loads(response.get_data(as_text=True))
    assert response['registration_status'] is not None
    assert response['stolen_status'] is not None
    assert response['gsma'] is not None
    assert response['compliant'] is not None


def test_full_status_reg_response(dirbs_core_mock, flask_app):
    """Test registration and stolen status customization in case of IMEI being stolen and registration request is pending"""
    response = flask_app.post(full_status_api_url, data=json.dumps({"imei": "12345678902222",
                                                                    "subscribers": {"limit": 10, "start": 1},
                                                                    "pairs": {"start": 1, "limit": 10}}),
                              content_type='application/json')
    response = json.loads(response.get_data(as_text=True))
    assert response['registration_status'] is not None
    assert response['stolen_status'] is not None


def test_full_status_not_reg_response(dirbs_core_mock, flask_app):
    """Test registration and stolen status customization in case of IMEI being registered and stolen request is pending"""
    response = flask_app.post(full_status_api_url, data=json.dumps({"imei": "12345678903333",
                                                                    "subscribers": {"limit": 10, "start": 1},
                                                                    "pairs": {"start": 1, "limit": 10}}),
                              content_type='application/json')
    response = json.loads(response.get_data(as_text=True))
    assert response['registration_status'] is not None
    assert response['stolen_status'] is not None
