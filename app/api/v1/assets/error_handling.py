###################################################
#                                                 #
# Copyright (c) 2018 Qualcomm Technologies, Inc.  #
#                                                 #
# All rights reserved.                            #
#                                                 #
###################################################

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
