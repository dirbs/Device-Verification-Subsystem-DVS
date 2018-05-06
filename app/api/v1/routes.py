from flask_restful import Api
from app import app
from .resources.user import BasicStatus, FullStatus

api = Api(app, prefix='/api/v1')

try:
    api.add_resource(BasicStatus, '/basicstatus')
    api.add_resource(FullStatus, '/fullstatus')
except Exception as e:
    print(e)

