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

import re
from marshmallow import ValidationError
from flask_babel import _

from app import app


class Validations:
    """Class for input validations."""

    @staticmethod
    def validate_imei(val):
        """Validates IMEI input format."""
        match = re.match('^[a-fA-F0-9]{14,16}$', val)
        if len(val) == 0:
            raise ValidationError(_("Enter IMEI."))
        if match is None:
            raise ValidationError(_("IMEI is invalid. Enter 16 digit IMEI."))

    @staticmethod
    def validate_fields(val):
        if val is None or val is "":
            raise ValidationError(_("Invalid Value."))

    @staticmethod
    def validate_tac(val):
        if val.isdigit() is False:
            raise ValidationError(_("Not a valid integer."))

    @staticmethod
    def validate_username(val):
        if val is None or len(val) == 0 or val == "":
            raise ValidationError(_("Enter username."))
        match = re.match(app.config['system_config']['regex'][app.config['system_config']['language_support']['default']], val)
        if match is None:
            raise ValidationError(_('Username is invalid. Does not match the selected language or invalid format.'))

    @staticmethod
    def validate_user_id(val):
        if val is None or len(val)==0 or val=="":
            raise ValidationError(_("Enter userid."))
