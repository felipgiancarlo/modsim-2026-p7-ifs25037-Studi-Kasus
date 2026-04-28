from datetime import datetime
from app.extensions import db

class TripPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer)
    activity = db.Column(db.Text)
    estimated_cost = db.Column(db.String(100))
    tips = db.Column(db.Text)

    request_id = db.Column(db.Integer, db.ForeignKey('trip_request.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)