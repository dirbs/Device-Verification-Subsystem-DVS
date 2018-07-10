import json
import time
from app import app
from .resources.public import BasicStatus
from .resources.admin import FullStatus
from .resources.bulk_check import BulkCheck
from flask import Response, Blueprint

public_api = Blueprint('public', __name__)
admin_api = Blueprint('admin', __name__)
bulk_api = Blueprint('bulk', __name__)


@app.route('/')
def index_route():
    data = {
        'message': 'Welcome to DVS'
    }

    response = Response(json.dumps(data), status=200, mimetype='application/json')
    return response


@public_api.route('/basicstatus', methods=['GET'])
def basicstatus():
    response = BasicStatus.get()
    if response.status_code in [504, 503]:
        response = BasicStatus.get()
        if response.status_code in [504, 503]:
            response = BasicStatus.get()
    return response

@admin_api.route('/fullstatus', methods=['POST'])
def fullstatus():
    response = FullStatus.get()
    if response.status_code in [504, 503]:
        response = FullStatus.get()
        if response.status_code in [504, 503]:
            response = FullStatus.get()
    return response


@bulk_api.route('/bulk', methods=['POST'])
def bulk():
    return BulkCheck.get()


@bulk_api.route('/download', methods=['POST'])
def download():
    return BulkCheck.send_file()
