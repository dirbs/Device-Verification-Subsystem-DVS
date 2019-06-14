"""
 SPDX-License-Identifier: BSD-4-Clause-Clear

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
   disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided with the distribution.
 * All advertising materials mentioning features or use of this software, or any deployment of this software, or
   documentation accompanying any distribution of this software, must display the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
   products derived from this software without specific prior written permission.

 SPDX-License-Identifier: ZLIB-ACKNOWLEDGEMENT

 Copyright (c) 2018-2019 Qualcomm Technologies, Inc.

 This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable
 for any damages arising from the use of this software.

 Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter
 it and redistribute it freely, subject to the following restrictions:

 * The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If
   you use this software in a product, an acknowledgment is required by displaying the trademark/logo as per the details
   provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
 * Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
 * This notice may not be removed or altered from any source distribution.

 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.                                                               #
"""

from app import db
from ..models.summary import Summary


class Request(db.Model):
    """Database model for user bulk requests."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))
    username = db.Column(db.String(100))
    summary_id = db.Column(db.Integer, db.ForeignKey('summary.id', ondelete='CASCADE'))

    def __init__(self, args):
        """Constructor."""
        self.user_id = args.get('user_id')
        self.username = args.get('username')
        self.summary_id = args.get('summary_id')

    @property
    def serialize(self):
        return {
            "username": self.username,
            "user_id": self.user_id,
            "summary_id": self.summary_id
        }

    @classmethod
    def create(cls, args):
        """Insert request data."""
        try:
            request = cls(args)
            db.session.add(request)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def find(cls, summary_id, user_id):
        try:
            request_data = cls.query.filter_by(summary_id=summary_id, user_id=user_id).first()
            if request_data:
                response = request_data.serialize
                return response
            else:
                return None
        except Exception:
            raise Exception


    @classmethod
    def find_requests(cls, user_id):
        try:
            records = []
            done = []
            request_data = cls.query.filter_by(user_id=user_id)
            if request_data:
                for record in request_data:
                    data = record.serialize
                    if data['summary_id'] not in done:
                        done.append(data['summary_id'])
                        summary = Summary.find_by_id(data['summary_id'])
                        resp = {**data, **summary}
                        records.append(resp)
                records = sorted(records, key=lambda k: k['start_time'], reverse=True)
                return records
            else:
                return None
        except Exception:
            raise Exception

