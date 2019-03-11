#######################################################################################################################
#                                                                                                                     #
# Copyright (c) 2018 Qualcomm Technologies, Inc.                                                                      #
#                                                                                                                     #
# All rights reserved.                                                                                                #
#                                                                                                                     #
# Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the      #
# limitations in the disclaimer below) provided that the following conditions are met:                                #
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following  #
#   disclaimer.                                                                                                       #
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the         #
#   following disclaimer in the documentation and/or other materials provided with the distribution.                  #
# * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or       #
#   promote products derived from this software without specific prior written permission.                            #
#                                                                                                                     #
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED  #
# BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED #
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT      #
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR   #
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE,      #
# DATA, OR PROFITS OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,      #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,   #
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                                  #
#                                                                                                                     #
#######################################################################################################################

import io
import json
import os


def test_bulk_post_route(flask_app):
    """Test mime type and success response via TAC input"""
    response = flask_app.post('/api/v1/bulk', data=dict(tac='86453223', indicator='False'))
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['task_id'] is not None
    assert json.loads(response.get_data(as_text=True))['message'] == "You can track your request using this id"


def test_bulkfile_post_route(flask_app):
    """Test mime type and success response via File input"""
    data = dict(
        file=(io.BytesIO(b'01206400000001\n353322asddas00303\n12344321000020\n35499405000401\n35236005000001\n01368900000001'),
              "imeis.tsv"))

    response = flask_app.post('/api/v1/bulk', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert json.loads(response.get_data(as_text=True))['task_id'] is not None
    assert json.loads(response.get_data(as_text=True))['message'] == "You can track your request using this id"


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
    response = flask_app.post('/api/v1/bulk', data=dict(tac='8645', indicator='False'))
    assert json.loads(response.get_data(as_text=True))['message'] == 'Invalid TAC, Enter 8 digit TAC.'

    # TAC is empty
    response = flask_app.post('/api/v1/bulk', data=dict(tac='', file='', indicator='False'))
    assert json.loads(response.get_data(as_text=True))['message'] == 'Upload file or enter TAC.'

    # TAC containing invalid characters
    response = flask_app.post('/api/v1/bulk', data=dict(tac='8645asdas', indicator='False'))
    assert json.loads(response.get_data(as_text=True))['message'] == 'Invalid TAC, Enter 8 digit TAC.'

    # TAC length greater than 8 digits
    response = flask_app.post('/api/v1/bulk', data=dict(tac='86456786878', indicator='False'))
    assert json.loads(response.get_data(as_text=True))['message'] == 'Invalid TAC, Enter 8 digit TAC.'


def test_bulk_file_input_format(flask_app):
    """Test file format validation"""

    data = dict(file=(
    io.BytesIO(b'01206400000001\n35332206000303\n12344321000020\n35499405000401\n35236005000001\n01368900000001'),
    "imeis.csv"))

    # Incorrect file type
    response = flask_app.post('/api/v1/bulk', data=data, content_type='multipart/form-data')
    assert json.loads(response.get_data(as_text=True))['message'] == 'System only accepts tsv/txt files.'

    # Empty tsv File
    response = flask_app.post('/api/v1/bulk', data=dict(file=(io.BytesIO(b'\n\n\n'), 'imeis.tsv'), content_type='multipart/form-data'))
    assert json.loads(response.get_data(as_text=True))['message'] == "File must have minimum 1 or maximum 1000000 IMEIs."

    # File with invalid content
    response = flask_app.post('/api/v1/bulk', data=dict(file=(io.BytesIO(b'hello\nworld\n'),'imeis.tsv'), content_type='multipart/form-data'))
    assert json.loads(response.get_data(as_text=True))['message'] == 'File contains malformed content'

    # File not selected
    response = flask_app.post('/api/v1/bulk', data=dict(), content_type='multipart/form-data')
    assert json.loads(response.get_data(as_text=True))['message'] == 'Upload file or enter TAC.'


def test_task_id_file(app, flask_app):
    """Test bulk status tracking ID properly written in task file"""
    task_dir = os.path.join(app.config['dev_config']['UPLOADS']['task_dir'], 'task_ids.txt')

    data = dict(file=(
        io.BytesIO(b'01206400000001\n35332206000303\n12344321000020\n35499405000401\n35236005000001\n01368900000001'),
        "imeis.tsv"))

    response = flask_app.post('/api/v1/bulk', data=data, content_type='multipart/form-data')
    task_file = open(task_dir, 'r')
    task_id = json.loads(response.get_data(as_text=True))['task_id']
    assert task_id in task_file.read().split()
    task_file.close()
