from app import app
from .resources.public import BasicStatus
from .resources.admin import FullStatus
from .resources.bulk_check import BulkCheck
from app import config

base_route = config.get("Development", "base_route")

@app.route(base_route+'/basicstatus', methods=['GET'])
def basicstatus():
    return BasicStatus().get()

@app.route(base_route+'/fullstatus', methods=['GET', 'POST'])
def fullstatus():
    return FullStatus().get()

@app.route(base_route+'/bulk', methods=['GET', 'POST'])
def bulk():
    return BulkCheck().get()

