from webargs import fields
from app import GLOBAL_CONF

status_args = {
        "imei": fields.Str(Required=True, validate=lambda p:int(GLOBAL_CONF['min_imei_length']) <= len(p) <= int(GLOBAL_CONF['max_imei_length'])),
        "seen_with": fields.Int(Required=True)
    }
