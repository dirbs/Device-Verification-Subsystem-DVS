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

import ast
from app import db
from flask_babel import _


class Summary(db.Model):
    """Database model for summary responses"""
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.String(100))
    tracking_id = db.Column(db.String(100))
    status = db.Column(db.String(20))
    summary_response = db.Column(db.String(1000), server_default=None)
    input_type = db.Column(db.String(40))
    start_time = db.Column(db.DateTime, server_default=db.func.now())
    end_time = db.Column(db.DateTime, server_default=None)
    request = db.relationship("Request", backref="summary", passive_deletes=True, lazy=True)

    def __init__(self, args):
        """Constructor."""
        self.input = args.get("input")
        self.status = args.get("status")
        self.tracking_id = args.get("tracking_id")
        self.input_type = args.get("input_type")


    @property
    def serialize(self):
        """Serialize."""
        if self.summary_response:
            return {"response": ast.literal_eval(self.summary_response),
                    "input": self.input, "status": self.status, "tracking_id": self.tracking_id,
                    "start_time": self.start_time,
                    "end_time": self.end_time,
                    "id": self.id}
        else:
            return {"response": self.summary_response, "input": self.input, "status": self.status,
                    "tracking_id": self.tracking_id,
                    "start_time": self.start_time,
                    "end_time": self.end_time, "id": self.id}

    @property
    def serialize_summary(self):
        """Serialize."""
        return {"input": self.input, "status": _(self.status), "tracking_id": self.tracking_id,
                "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S")}

    @classmethod
    def create(cls, args):
        """Insert request data."""
        try:
            summary = cls(args)
            db.session.add(summary)
            db.session.commit()
            return summary.id
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update(cls, input, status, response):
        """Update request data."""
        try:
            for row in cls.query.filter_by(input=input, tracking_id=response['task_id']).all():
                row.summary_response = str(response)
                row.status = status
                row.end_time = db.func.now()
                db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update_failed_task_to_pending(cls, args):
        """Update request data."""
        try:
            for row in cls.query.filter_by(input=args.get("input"), tracking_id=args.get("tracking_id")).all():
                row.status = args.get("status")
                row.start_time = db.func.now()
                row.end_time = None
                row.summary_response = None
                db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def find_by_input(cls, input):
        try:
            data = cls.query.filter_by(input=input).first()
            if data:
                return data.serialize
            else:
                return None
        except Exception:
            raise Exception

    @classmethod
    def find_by_trackingid(cls, tracking_id):
        try:
            data = cls.query.filter_by(tracking_id=tracking_id).first()
            if data:
                return data.serialize
            else:
                return None
        except Exception:
            raise Exception

    @classmethod
    def find_by_id(cls, summary_id):
        try:
            data = cls.query.filter_by(id=summary_id).first()
            if data:
                return data.serialize_summary
            else:
                return None
        except Exception:
            raise Exception

