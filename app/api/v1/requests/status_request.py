import re
from webargs import fields, ValidationError

from app import GlobalConfig

def validate_imei(val):
    match = re.match(r'^\d{8}[a-fA-F0-9]{6,8}$', val)
    if match is None:
        raise ValidationError("invalid imei")
    if len(val) > int(GlobalConfig['MaxImeiLength']):
        raise ValidationError("imei too long")

basic_status_args = {
    "imei": fields.Str(required=True, validate=lambda p: validate_imei(p))
}

full_status_args = {
    "imei": fields.Str(required=True, validate=lambda p: validate_imei(p)),
    "seen_with": fields.Int(),
    "start": fields.Int(validate=lambda p: p > 0),
    "limit": fields.Int(validate=lambda p: p > 0)
}
