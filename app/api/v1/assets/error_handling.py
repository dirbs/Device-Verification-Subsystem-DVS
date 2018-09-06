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
from flask import Response
from .responses import responses, messages, mime_types


@app.errorhandler(responses.get('not_found'))
def not_found(error=None):
    resp = Response(json.dumps({"message":messages.get('not_found'), "status_code": responses.get('not_found')}),
                    status=responses.get('not_found'),
                    mimetype=mime_types.get('json'))
    return resp


@app.errorhandler(responses.get('bad_request'))
def bad_request(error=None):
    resp = Response(json.dumps({"message":messages.get('bad_request'), "status_code": responses.get('bad_request')}),
                    status=responses.get('bad_request'),
                    mimetype=mime_types.get('json'))
    return resp


@app.errorhandler(responses.get('internal_error'))
def internal_error(error=None):
    resp = Response(json.dumps({"message":messages.get('internal_error'), "status_code": responses.get('internal_error')}),
                    status=responses.get('internal_error'),
                    mimetype=mime_types.get('json'))
    return resp

@app.errorhandler(responses.get('method_not_allowed'))
def method_not_allowed(error=None):
    resp = Response(json.dumps({"message":messages.get('method_not_allowed'), "status_code": responses.get('method_not_allowed')}),
                    status=responses.get('method_not_allowed'),
                    mimetype=mime_types.get('json'))
    return resp


def custom_response(message, status, mimetype):
    resp = Response(json.dumps({"message": message, "status_code": status}),
                    status=status,
                    mimetype=mimetype)
    return resp
