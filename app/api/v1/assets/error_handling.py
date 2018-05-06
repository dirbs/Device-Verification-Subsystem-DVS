import json
from app import app
from flask import Response
from .responses import responses, messages, mime_types

@app.errorhandler(404)
def not_found(error=None):
    resp = Response(json.dumps(messages['not_found']), status=responses['not_found'], mimetype=mime_types['json'])
    return resp

@app.errorhandler(400)
def bad_request(error=None):
    resp = Response(json.dumps(messages['bad_request']), status=responses['bad_request'], mimetype=mime_types['json'])
    return resp