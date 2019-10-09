"""
Copyright (c) 2018-2019 Qualcomm Technologies, Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the limitations in the disclaimer below) provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
    The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
    Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
    This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

from marshmallow import Schema, fields
from app.api.v1.schema.validations import Validations


class BasicStatusSchema(Schema):
    """Marshmallow schema for basic status request."""
    imei = fields.Str(required=True, validate=Validations.validate_imei, description="14-16 digit IMEI")
    token = fields.Str(required=True, validate=Validations.validate_fields, description="token generated from reCaptcha validation")
    source = fields.Str(required=True, validate=Validations.validate_fields, description="source of request i.e. Android, Web, iOS")

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
    tac = fields.Str(description="Enter 8 digit TAC", validate=Validations.validate_tac)
    username = fields.Str(description="User name", validate=Validations.validate_username)
    user_id = fields.Str(description="User id", validate=Validations.validate_user_id)

    @property
    def fields_dict(self):
        """Convert declared fields to dictionary."""
        return self._declared_fields
