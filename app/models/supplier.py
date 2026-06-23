from app import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id           = db.Column(db.Integer, primary_key=True)
    company_id   = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name         = db.Column(db.String(200), nullable=False)
    type         = db.Column(db.Enum('fuel_supplier','port','maintenance',
                                     'logistics','food','waste','other'), default='other')
    country      = db.Column(db.String(60))
    contact_email = db.Column(db.String(180))
    has_provided_factor = db.Column(db.Boolean, default=False)
    factor_year  = db.Column(db.Integer)
    tier         = db.Column(db.Integer, default=1)     # Supply chain tier
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    company         = db.relationship('Company', back_populates='suppliers')
    emission_factors = db.relationship('EmissionFactor', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'type': self.type,
            'country': self.country, 'contact_email': self.contact_email,
            'has_provided_factor': self.has_provided_factor,
            'tier': self.tier, 'is_active': self.is_active,
        }