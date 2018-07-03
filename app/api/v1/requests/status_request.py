import re
from webargs import fields


def validate_imei(val):
    match = re.match(r'^\d{8}[a-fA-F0-9]{6,8}$', val)
    if len(val) > 16:
        raise ValueError("imei too long")
    if len(val) < 14:
        raise ValueError('imei too short')
    if match is None:
        raise ValueError("invalid imei")



def validate_start_limit(val, input):
    if val<1:
        raise ValueError("{} should be greater or equal to 1".format(input))


basic_status_args = {
    "imei": fields.Str(required=True, validate=validate_imei)
}

full_status_args = {
    "imei": fields.Str(required=True, validate=validate_imei),
    "seen_with": fields.Int(),
    "start": fields.Int(validate=lambda p: validate_start_limit(p, "start")),
    "limit": fields.Int(validate=lambda p: validate_start_limit(p, "limit"))
}
