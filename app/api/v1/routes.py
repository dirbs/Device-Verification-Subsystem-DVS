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

import json
from app import app
from .resources.public import BasicStatus
from .resources.admin import FullStatus
from .resources.bulk_check import BulkCheck
from flask import Response, Blueprint

public_api = Blueprint('public', __name__)
admin_api = Blueprint('admin', __name__)
bulk_api = Blueprint('bulk', __name__)


@app.route('/', methods=['GET', 'POST'])
def index_route():
    data = {
        'message': 'Welcome to DVS'
    }

    response = Response(json.dumps(data), status=200, mimetype='application/json')
    return response

@public_api.route('/', methods=['GET', 'POST'])
def index():
    data = {
        'message': 'Welcome to DVS version 1.0'
    }

    response = Response(json.dumps(data), status=200, mimetype='application/json')
    return response

@public_api.route('/basicstatus', methods=['GET'])
def basicstatus():
    response = BasicStatus.get()
    return response

@public_api.route('/sms', methods=['GET'])
def sms_verifcation():
    response = BasicStatus.get_basic()
    return response


@admin_api.route('/fullstatus', methods=['POST'])
def fullstatus():
    response = FullStatus.get()
    return response


@bulk_api.route('/bulk', methods=['POST'])
def bulk():
    return BulkCheck.summary()

@bulk_api.route('/drs_bulk', methods=['POST'])
def drs_bulk():
    return BulkCheck.drs_summary()


@bulk_api.route('/download/<filename>', methods=['POST'])
def download(filename):
    return BulkCheck.send_file(filename)


@bulk_api.route('/bulkstatus/<tracking_id>', methods=['POST'])
def status(tracking_id):
    return BulkCheck.check_status(tracking_id)
