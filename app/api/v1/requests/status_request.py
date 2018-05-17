from webargs import fields

status_args = {
        "imei": fields.Str(Required=True),
        "seen_with": fields.Int(Required=True)
    }
