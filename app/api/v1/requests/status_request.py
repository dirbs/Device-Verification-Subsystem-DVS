import re
from webargs import fields
from app import GlobalConfig

basic_status_args = {
        "imei": fields.Str(required=True, validate=lambda p:int(GlobalConfig['MinImeiLength']) <= len(p) <= int(GlobalConfig['MaxImeiLength']))
    }

full_status_args = {
        "imei": fields.Str(required=True, validate=lambda p:int(GlobalConfig['MinImeiLength']) <= len(p) <= int(GlobalConfig['MaxImeiLength'])),
        "seen_with": fields.Int(),
        "start": fields.Int(validate=lambda p: p>0),
        "limit": fields.Int(validate=lambda p: p>0)
    }