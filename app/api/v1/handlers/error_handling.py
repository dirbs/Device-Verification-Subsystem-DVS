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

"""This module handles flask app errors"""

import json
from app import app
from flask import Response
from .codes import RESPONSES, MESSAGES, MIME_TYPES


@app.errorhandler(RESPONSES.get('NOT_FOUND'))
def not_found(error=None):
    """handle app's 404 error."""
    resp = Response(json.dumps({"message": MESSAGES.get('NOT_FOUND'), "status_code": RESPONSES.get('NOT_FOUND')}),
                    status=RESPONSES.get('NOT_FOUND'),
                    mimetype=MIME_TYPES.get('JSON'))
    return resp


@app.errorhandler(RESPONSES.get('BAD_REQUEST'))
def bad_request(error=None):
    """handle app's 400 error"""
    resp = Response(json.dumps({"message": MESSAGES.get('BAD_REQUEST'), "status_code": RESPONSES.get('BAD_REQUEST')}),
                    status=RESPONSES.get('BAD_REQUEST'),
                    mimetype=MIME_TYPES.get('JSON'))
    return resp


@app.errorhandler(RESPONSES.get('INTERNAL_SERVER_ERROR'))
def internal_error(error=None):
    """handle app's 500 error"""
    resp = Response(json.dumps({"message":MESSAGES.get('INTERNAL_SERVER_ERROR'), "status_code": RESPONSES.get('INTERNAL_SERVER_ERROR')}),
                    status=RESPONSES.get('INTERNAL_SERVER_ERROR'),
                    mimetype=MIME_TYPES.get('JSON'))
    return resp


@app.errorhandler(RESPONSES.get('METHOD_NOT_ALLOWED'))
def method_not_allowed(error=None):
    """handle app's 405 error"""
    resp = Response(json.dumps({"message":MESSAGES.get('METHOD_NOT_ALLOWED'), "status_code": RESPONSES.get('METHOD_NOT_ALLOWED')}),
                    status=RESPONSES.get('METHOD_NOT_ALLOWED'),
                    mimetype=MIME_TYPES.get('JSON'))
    return resp


def custom_response(message, status, mimetype):
    """handle custom errors"""
    resp = Response(json.dumps({"message": message, "status_code": status}),
                    status=status,
                    mimetype=mimetype)
    return resp
