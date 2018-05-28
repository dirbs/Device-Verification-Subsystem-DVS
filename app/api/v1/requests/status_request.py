from webargs import fields
from app import GlobalConfig

status_args = {
        "imei": fields.Str(Required=True, validate=lambda p:int(GlobalConfig['MinImeiLength']) <= len(p) <= int(GlobalConfig['MaxImeiLength'])),
        "seen_with": fields.Int(Required=True)
    }
