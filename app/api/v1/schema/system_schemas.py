from marshmallow import Schema, fields
from app.api.v1.schema.validations import Validations


class BasicStatusSchema(Schema):
    """Marshmallow schema for basic status request."""
    imei = fields.Str(required=True, validate=Validations.validate_imei, description="14-16 digit IMEI")
    token = fields.Str(required=True, validate=lambda p: p != '', description="token generated from reCaptcha validation")
    source = fields.Str(required=True, validate=lambda p: p != '', description="source of request i.e. Android, Web, iOS")

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class SMSSchema(Schema):
    """Marshmallow schema for SMS API."""
    imei = fields.Str(required=True, validate=Validations.validate_imei, description="14-16 digit IMEI")

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class PaginationSchema(Schema):
    """Marshmallow schema for pagination."""
    start = fields.Int(validate=lambda p: p >= 1)
    limit = fields.Int(validate=lambda p: p >= 1)


class FullStatusSchema(Schema):
    """Marshmallow schema for full status request."""

    imei = fields.Str(required=True, validate=Validations.validate_imei, description="14-16 digit IMEI")
    subscribers = fields.Nested(PaginationSchema)
    pairs = fields.Nested(PaginationSchema)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields


class BulkSchema(Schema):
    """Marshmallow schema for bulk request."""

    file = fields.Str(description="Submit tsv/txt file path containing bulk IMEIs")
    tac = fields.Int(description="Enter 8 digit TAC")

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields