###################################################
#                                                 #
# Copyright (c) 2018 Qualcomm Technologies, Inc.  #
#                                                 #
# All rights reserved.                            #
#                                                 #
###################################################

import re
from webargs import fields


def validate_imei(val):
    match = re.match(r'^[a-fA-F0-9]{14,16}$', val)
    if len(val)==0:
        raise ValueError("Enter IMEI.")
    if match is None:
        raise ValueError("IMEI is invalid. Enter 16 digit IMEI.")


def validate_start_limit(val, input):
    if val<1:
        raise ValueError("{} should be greater or equal to 1".format(input))


basic_status_args = {
    "imei": fields.Str(required=True, validate=validate_imei),
    "token": fields.Str(required=True),
    "source": fields.Str(required=True)
}

sms_args = {
    "imei": fields.Str(required=True, validate=validate_imei)
}

full_status_args = {
    "imei": fields.Str(required=True, validate=validate_imei),
    "subscribers": fields.Nested({
        "start": fields.Int(validate=lambda p: validate_start_limit(p, "start")),
        "limit": fields.Int(validate=lambda p: validate_start_limit(p, "limit"))
    }),
    "pairs": fields.Nested({
        "start": fields.Int(validate=lambda p: validate_start_limit(p, "start")),
        "limit": fields.Int(validate=lambda p: validate_start_limit(p, "limit"))
    })
}
