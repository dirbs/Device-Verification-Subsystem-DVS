import re
from webargs import fields


def validate_imei(val):
    match = re.match(r'^[a-fA-F0-9]{14,16}$', val)
    if len(val)==0:
        raise ValueError("enter imei")
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
