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
    return BasicStatus.get()


@admin_api.route('/fullstatus', methods=['POST'])
def fullstatus():
    return FullStatus.get()


@bulk_api.route('/bulk', methods=['POST'])
def bulk():
    return BulkCheck.summary()


@bulk_api.route('/download/<filename>', methods=['POST'])
def download(filename):
    return BulkCheck.send_file(filename)


@bulk_api.route('/bulkstatus/<tracking_id>', methods=['POST'])
def status(tracking_id):
    return BulkCheck.check_status(tracking_id)
