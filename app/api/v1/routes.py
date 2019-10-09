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

from flask_restful import Api
from app import app
from app.common.apidoc import ApiDocs

from .resources.public import BasicStatus, PublicSMS, BaseRoute
from .resources.admin import FullStatus
from .resources.dvs_bulk import AdminBulk
from .resources.common import AdminCheckBulkStatus, AdminDownloadFile, index, GetRequests

api = Api(app, prefix='/api/v1')
apidocs = ApiDocs(app, 'v1')

api.add_resource(BasicStatus, '/basicstatus')
api.add_resource(PublicSMS, '/sms')
api.add_resource(BaseRoute, '/')
api.add_resource(FullStatus, '/fullstatus')
api.add_resource(AdminBulk, '/bulk')
api.add_resource(AdminDownloadFile, '/download/<filename>')
api.add_resource(AdminCheckBulkStatus, '/bulkstatus/<task_id>')
api.add_resource(GetRequests, '/requests/<user_id>')

docs = apidocs.init_doc()


def register():
    """ Method to register routes. """
    for route in [BaseRoute, BasicStatus, FullStatus, AdminBulk, AdminDownloadFile, AdminCheckBulkStatus,
                  PublicSMS, index, GetRequests]:
        docs.register(route)

register()