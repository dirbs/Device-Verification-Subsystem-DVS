from app import db


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
