from app import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Enum('ship_owner', 'ship_operator', 'supplier', 'port_authority', 'other'),
                     default='ship_owner', nullable=False)
    country = db.Column(db.String(60))
    address = db.Column(db.String(255))
    website = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='company', lazy='dynamic')
    vessels = db.relationship('Vessel', back_populates='company', lazy='dynamic')
    reports = db.relationship('Report', back_populates='company', lazy='dynamic')
    suppliers = db.relationship('Supplier', back_populates='company', lazy='dynamic')
    emissions = db.relationship('Emission', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', lazy='dynamic')
    fixture_schedules = db.relationship('FixtureSchedule', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'country': self.country,
            'address': self.address,
            'website': self.website,
            'is_active': self.is_active,
        }
