###################################################
#                                                 #
# Copyright (c) 2018 Qualcomm Technologies, Inc.  #
#                                                 #
# All rights reserved.                            #
#                                                 #
###################################################

responses = {
    'not_found': 404,
    'bad_request': 400,
    'ok': 200,
    'no_content': 204,
    'internal_error': 500,
    'service_unavailable': 503,
    'timeout': 504,
    'method_not_allowed': 405
}

messages = {
    'not_found': 'Resource not found.',
    'bad_request': 'Bad Format',
    'ok': 'Status OK',
    'internal_error': 'There is some internal error',
    'method_not_allowed': 'Method not allowed.'
}

mime_types = {
    'json': 'application/json',
    'text': 'text/plain',
    'all': 'application/*'
}
