from app import db


class Request(db.Model):
    """Database model for user bulk requests."""
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(25))
    start_time = db.Column(db.DateTime, server_default=db.func.now())
    end_time = db.Column(db.DateTime, server_default=None)
    status = db.Column(db.String(15))
    input_type = db.Column(db.String(15))
    input = db.Column(db.String(100))
    user_id = db.Column(db.String(100))
    username = db.Column(db.String(100))
    response_id = db.Column(db.Integer, db.ForeignKey('summary.id', ondelete='CASCADE'))

    def __init__(self, args):
        """Constructor."""
        self.tracking_id = args.get('tracking_id')
        self.status = args.get('status')
        self.user_id = args.get('user_id')
        self.username = args.get('username')
        self.input = args.get('input')
        self.input_type = args.get('input_type')

    @classmethod
    def create(cls, args):
        """Insert request data."""
        try:
            request = cls(args)
            db.session.add(request)
        except Exception:
            db.session.rollback()
            raise Exception

    @classmethod
    def update(cls, status, tracking_id, response_id):
        """Update request data."""
        try:
            request = cls.query.filter_by(tracking_id=tracking_id).first()
            request.end_time = db.func.now()
            request.status = status
            request.response_id = response_id
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise Exception
