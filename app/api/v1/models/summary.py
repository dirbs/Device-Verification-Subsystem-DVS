import json
from app import db


class Summary(db.Model):
    """Database model for summary responses"""
    id = db.Column(db.Integer, primary_key=True)
    tac = db.Column(db.String(16))
    response = db.Column(db.String(1000), server_default=None)
    request = db.relationship("Request", backref="summary", passive_deletes=True, lazy=True)

    def __init__(self, tac):
        """Constructor."""
        self.tac = tac

    @property
    def serialize(self):
        """Serialize."""
        return json.loads(self.response)

    @classmethod
    def create(cls, tac):
        """Insert request data."""
        try:
            summary = cls(tac)
            db.session.add(summary)
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update(cls, tac, response):
        """Update request data."""
        try:
            summary = cls.query.filter_by(tac=tac).first()
            summary.response = response
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception
