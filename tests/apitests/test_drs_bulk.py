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

import io
import json

drs_api = '/api/v1/drs_bulk'


def test_drs_bulk(flask_app):
    """Tests DRS bulk IMEI verification."""
    data = dict(file=(
        io.BytesIO(b'01206400000001\n12344321000020\n35499405000401\n35236005000001\n01368900000001'),
        'drs-bulk.tsv'))

    response = flask_app.post(drs_api, data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['task_id'] is not None
    assert json.loads(response.get_data(as_text=True))['message'] == "You can track your request using this id"


def test_drs_bulk_method_not_allowed(flask_app):
    """Tests DRS bulk allowed methods."""
    data = dict(file=(io.BytesIO(b'\n\n\n'), 'imeis.tsv'))
    response = flask_app.get(drs_api, data=data, content_type='multipart/form-data')
    assert response.status_code == 405
    data = dict(file=(io.BytesIO(b'\n\n\n'), 'imeis.tsv'))
    response = flask_app.put(drs_api, data=data, content_type='multipart/form-data')
    assert response.status_code == 405
    data = dict(file=(io.BytesIO(b'\n\n\n'), 'imeis.tsv'))
    response = flask_app.patch(drs_api, data=data, content_type='multipart/form-data')
    assert response.status_code == 405
    data = dict(file=(io.BytesIO(b'\n\n\n'), 'imeis.tsv'))
    response = flask_app.delete(drs_api, data=data, content_type='multipart/form-data')
    assert response.status_code == 405


def test_drs_bulk_input_format(flask_app):
    """Tests DRS bulk input format validation"""
    data = dict(file=(
    io.BytesIO(b'01206400000001\n35332206000303\n12344321000020\n35499405000401\n35236005000001\n01368900000001'),
    "imeis.csv"))

    response = flask_app.post('/api/v1/bulk', data=data, content_type='multipart/form-data')
    assert json.loads(response.get_data(as_text=True))['message'] == 'System only accepts tsv/txt files.'
