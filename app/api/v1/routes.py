from app import app
from .resources.public import BasicStatus
from .resources.admin import FullStatus
from .resources.bulk_check import BulkCheck

@app.route('/basicstatus', methods=['GET'])
def basicstatus():
    return BasicStatus().get()

@app.route('/fullstatus', methods=['GET', 'POST'])
def fullstatus():
    return FullStatus().get()

@app.route('/bulk', methods=['GET', 'POST'])
def bulk():
    return BulkCheck().get()

@app.route('/download', methods=['GET', 'POST'])
def download():
    return BulkCheck().send_file()

