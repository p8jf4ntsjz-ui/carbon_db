from app import db
from datetime import datetime

class Voyage(db.Model):
    __tablename__ = 'voyages'

    id              = db.Column(db.Integer, primary_key=True)
    vessel_id       = db.Column(db.Integer, db.ForeignKey('vessels.id'), nullable=False)
    voyage_number   = db.Column(db.String(50), nullable=False)
    port_departure  = db.Column(db.String(100))
    port_arrival    = db.Column(db.String(100))
    departure_date  = db.Column(db.DateTime, nullable=False)
    arrival_date    = db.Column(db.DateTime)
    distance_nm     = db.Column(db.Float)          # Nautical miles
    cargo_weight_mt = db.Column(db.Float)          # Metric tons
    fuel_consumed   = db.Column(db.Float)          # Metric tons
    fuel_type       = db.Column(db.String(20))
    charter_party   = db.Column(db.String(100))
    status          = db.Column(db.Enum('planned','in_progress','completed','cancelled'),
                                default='planned')
    notes           = db.Column(db.Text)
    created_by      = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vessel    = db.relationship('Vessel', back_populates='voyages')
    emissions = db.relationship('Emission', back_populates='voyage', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'vessel_id': self.vessel_id,
            'voyage_number': self.voyage_number,
            'port_departure': self.port_departure,
            'port_arrival': self.port_arrival,
            'departure_date': self.departure_date.isoformat() if self.departure_date else None,
            'arrival_date': self.arrival_date.isoformat() if self.arrival_date else None,
            'distance_nm': self.distance_nm,
            'cargo_weight_mt': self.cargo_weight_mt,
            'fuel_consumed': self.fuel_consumed,
            'fuel_type': self.fuel_type,
            'status': self.status,
        }