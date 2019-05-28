import ast
from app import db


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
                    "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else 'N/A',
                    "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else 'N/A',
                    "id": self.id}
        else:
            return {"response": self.summary_response, "input": self.input, "status": self.status,
                    "tracking_id": self.tracking_id,
                    "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else 'N/A',
                    "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else 'N/A', "id": self.id}

    @property
    def serialize_summary(self):
        """Serialize."""
        return {"input": self.input, "status": self.status, "tracking_id": self.tracking_id}

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

