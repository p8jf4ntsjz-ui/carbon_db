from datetime import datetime
from __init__ import db


class EmissionFactor(db.Model):
    __tablename__ = 'emission_factors'

    id = db.Column(db.Integer, primary_key=True)
    activity_id   = db.Column(db.String(200), nullable=False, index=True)
    name          = db.Column(db.String(300))
    category      = db.Column(db.String(100), index=True)
    sector        = db.Column(db.String(100), index=True)
    source        = db.Column(db.String(100))
    region        = db.Column(db.String(50), index=True)
    unit_type     = db.Column(db.String(80))
    unit          = db.Column(db.String(40))
    factor_value  = db.Column(db.Float)      # kgCO2e par unité
    year          = db.Column(db.Integer)
    data_version  = db.Column(db.String(20))
    last_synced   = db.Column(db.DateTime, default=datetime.utcnow)

    emissions = db.relationship('EmissionEntry', backref='factor', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'name': self.name,
            'category': self.category,
            'sector': self.sector,
            'source': self.source,
            'region': self.region,
            'unit_type': self.unit_type,
            'factor_value': self.factor_value,
        }


class EmissionEntry(db.Model):
    """Entrée de consommation liée à un facteur d'émission Climatiq."""
    __tablename__ = 'emission_entries'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    factor_id        = db.Column(db.Integer, db.ForeignKey('emission_factors.id'))
    activity_id      = db.Column(db.String(200))   # copie pour audit
    quantity         = db.Column(db.Float, nullable=False)
    unit             = db.Column(db.String(40))
    co2e_kg          = db.Column(db.Float)          # calculé : quantity × factor_value
    scope            = db.Column(db.Enum('1','2','3', name='scope_levels'), default='3')
    date             = db.Column(db.Date, nullable=False)
    notes            = db.Column(db.Text)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_co2e(self):
        if self.factor and self.factor.factor_value:
            self.co2e_kg = round(self.quantity * self.factor.factor_value, 4)
        return self.co2e_kg