from flask_restful import Api
from app import app
from .resources.common import BaseRoutes
from .resources.user import BasicStatus, FullStatus

api = Api(app, prefix='/api/v1')

try:
    api.add_resource(BaseRoutes, '/base')
    api.add_resource(BasicStatus, '/basicstatus/<int:imei>')
    api.add_resource(FullStatus, '/fullstatus/<int:imei>')
except Exception as e:
    print(e)

