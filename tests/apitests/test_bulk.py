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

import io
import json
from app.api.v1.models.request import Request
from app.api.v1.models.summary import Summary


def test_bulk_post_route(flask_app):
    """Test mime type and success response via TAC input"""
    data = {
        'tac': '62783667',
        'username': 'username',
        'user_id': '5261531276351'
    }
    # dict(tac='86453223', indicator='False', username="username", user_id="678126378126378")
    response = flask_app.post('/api/v1/bulk', content_type='multipart/form-data', buffered=True, data=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['task_id'] is not None
    assert json.loads(response.get_data(as_text=True))['message'] is not None


def test_bulkfile_post_route(flask_app):
    """Test mime type and success response via File input"""
    data = dict(
        file=(io.BytesIO(b'01206400000001\n353322asddas00303\n12344321000020\n35499405000401\n35236005000001\n01368900000001'),
              "imeis.tsv"), username="username", user_id="678126378126378")

    response = flask_app.post('/api/v1/bulk', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['task_id'] is not None
    assert json.loads(response.get_data(as_text=True))['message'] is not None


def test_bulk_route_method_not_allowed(flask_app):
    """Test allowed request methods"""
    response = flask_app.get('/api/v1/bulk', data=dict(tac=12345678, indicator="True"))
    assert response.status_code == 405
    response = flask_app.put('/api/v1/bulk', data=dict(tac=12345678))
    assert response.status_code == 405
    response = flask_app.patch('/api/v1/bulk', data=dict(tac=12345678))
    assert response.status_code == 405
    response = flask_app.delete('/api/v1/bulk', data=dict(tac=12345678))
    assert response.status_code == 405


def test_bulk_tac_input_format(flask_app):
    """Test TAC format validation"""
    # TAC length less than 8 digits
    response = flask_app.post('/api/v1/bulk', data=dict(tac='8645', indicator='False', username="username", user_id="678126378126378"))
    assert json.loads(response.get_data(as_text=True))['message'] is not None

    # TAC is empty
    response = flask_app.post('/api/v1/bulk', data=dict(tac='', file='', indicator='False', username="username", user_id="678126378126378"))
    assert json.loads(response.get_data(as_text=True))['messages'] is not None

    # TAC containing invalid characters
    response = flask_app.post('/api/v1/bulk', data=dict(tac='8645asdas', indicator='False', username="username", user_id="678126378126378"))
    assert json.loads(response.get_data(as_text=True))['messages'] is not None

    # TAC length greater than 8 digits
    response = flask_app.post('/api/v1/bulk', data=dict(tac='86456786878', indicator='False', username="username", user_id="678126378126378"))
    assert json.loads(response.get_data(as_text=True))['message'] is not None


def test_bulk_file_input_format(flask_app):
    """Test file format validation"""

    data = dict(file=(io.BytesIO(b'01206400000001\n35332206000303\n12344321000020\n35499405000401\n35236005000001\n01368900000001'),
                      "imeis.csv"), username="username", user_id="678126378126378")

    # Incorrect file type
    response = flask_app.post('/api/v1/bulk', data=data, content_type='multipart/form-data')
    assert json.loads(response.get_data(as_text=True))['message'] is not None

    # Empty tsv File
    response = flask_app.post('/api/v1/bulk', data=dict(file=(io.BytesIO(b'\n\n\n'), 'imeis.tsv'), content_type='multipart/form-data', username="username", user_id="678126378126378"))
    assert json.loads(response.get_data(as_text=True))['message'] is not None

    # File with invalid content
    response = flask_app.post('/api/v1/bulk', data=dict(file=(io.BytesIO(b'hello\nworld\n'),'imeis.tsv'), content_type='multipart/form-data', username="username", user_id="678126378126378"))
    assert json.loads(response.get_data(as_text=True))['message'] is not None

    # File not selected
    response = flask_app.post('/api/v1/bulk', data=dict(), content_type='multipart/form-data')
    assert json.loads(response.get_data(as_text=True))['message'] is not None


def test_bulk_via_tac_pending(flask_app):
    summary_data = {
        "tracking_id": '1234567-asdfgh-890123',
        "input": '67890123',
        "input_type": "tac",
        "status": 'PENDING'
    }
    summary_record = Summary.create(summary_data)
    request_data = {
        "username": 'username',
        "user_id": 'user_id',
        "summary_id": summary_record
    }
    Request.create(request_data)
    response = flask_app.post('/api/v1/bulk', data=dict(tac='67890123', indicator='False', username="username", user_id="678126378126378"))
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['task_id'] is not None
    assert json.loads(response.get_data(as_text=True))['message'] is not None


def test_bulk_via_tac_success(flask_app):
    summary_data = {
        "tracking_id": '1234567-asdfgh-890123',
        "input": '67890122',
        "input_type": "tac",
        "status": 'SUCCESS'
    }
    summary_record = Summary.create(summary_data)
    request_data = {
        "username": 'username',
        "user_id": 'user_id',
        "summary_id": summary_record
    }
    Request.create(request_data)
    response = flask_app.post('/api/v1/bulk', data=dict(tac='67890122', indicator='False', username="username", user_id="678126378126378"))
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['task_id'] is not None
    assert json.loads(response.get_data(as_text=True))['message'] is not None


def test_bulk_via_tac_failure(flask_app):
    summary_data = {
        "tracking_id": '1234567-asdfgh-890123',
        "input": '67890222',
        "input_type": "tac",
        "status": 'FAILURE'
    }
    summary_record = Summary.create(summary_data)
    request_data = {
        "username": 'username',
        "user_id": 'user_id',
        "summary_id": summary_record
    }
    Request.create(request_data)
    response = flask_app.post('/api/v1/bulk', data=dict(tac='67890222', indicator='False', username='username', user_id='678126378126378'))
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['task_id'] is not None
    assert json.loads(response.get_data(as_text=True))['message'] is not None
