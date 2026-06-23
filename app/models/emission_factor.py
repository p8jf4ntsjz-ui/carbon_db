from app import db
from datetime import datetime

class EmissionFactor(db.Model):
    __tablename__ = 'emission_factors'

    id              = db.Column(db.Integer, primary_key=True)
    source          = db.Column(db.String(100), nullable=False)  # e.g. "IMO","IPCC","EPA","supplier"
    fuel_type       = db.Column(db.String(50))
    activity_type   = db.Column(db.String(100))
    region          = db.Column(db.String(60), default='global')
    year            = db.Column(db.Integer)
    co2_factor      = db.Column(db.Float, nullable=False)         # kgCO2/unit
    ch4_factor      = db.Column(db.Float, default=0.0)
    n2o_factor      = db.Column(db.Float, default=0.0)
    unit            = db.Column(db.String(30), nullable=False)    # e.g. "kgCO2/mt_fuel"
    gwp_co2         = db.Column(db.Float, default=1.0)
    gwp_ch4         = db.Column(db.Float, default=27.9)           # AR6
    gwp_n2o         = db.Column(db.Float, default=273.0)          # AR6
    supplier_id     = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    is_verified     = db.Column(db.Boolean, default=False)
    data_quality    = db.Column(db.Enum('primary','secondary','estimated'), default='secondary')
    valid_from      = db.Column(db.Date)
    valid_to        = db.Column(db.Date)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def total_co2e_factor(self):
        return (self.co2_factor * self.gwp_co2 +
                self.ch4_factor * self.gwp_ch4 +
                self.n2o_factor * self.gwp_n2o)

    def to_dict(self):
        return {
            'id': self.id, 'source': self.source,
            'fuel_type': self.fuel_type, 'activity_type': self.activity_type,
            'co2_factor': self.co2_factor, 'ch4_factor': self.ch4_factor,
            'n2o_factor': self.n2o_factor, 'unit': self.unit,
            'total_co2e_factor': self.total_co2e_factor,
            'is_verified': self.is_verified,
            'data_quality': self.data_quality,
        }