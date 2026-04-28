from datetime import datetime
from app.extensions import db

class TripRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100))
    duration_days = db.Column(db.Integer)
    budget = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)