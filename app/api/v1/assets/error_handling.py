import json
from app import app
from flask import Response
from .responses import responses, messages, mime_types

@app.errorhandler(responses.get('not_found'))
def not_found():
    resp = Response(json.dumps(messages.get('not_found')),
                    status=responses.get('not_found'),
                    mimetype=mime_types.get('json'))
    return resp

@app.errorhandler(responses.get('bad_request'))
def bad_request():
    resp = Response(json.dumps(messages.get('bad_request')),
                    status=responses.get('bad_request'),
                    mimetype=mime_types.get('json'))
    return resp

@app.errorhandler(responses.get('internal_error'))
def internal_error():
    resp = Response(json.dumps(messages.get('internal_error')),
                    status=responses.get('internal_error'),
                    mimetype=mime_types.get('json'))
    return resp

def custom_response(message, status, mimetype):
    resp = Response(json.dumps({"message": message}),
                    status=status,
                    mimetype=mimetype)
    return resp
