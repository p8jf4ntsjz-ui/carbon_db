from app import db
from datetime import datetime

class EmissionCategory(db.Model):
    __tablename__ = 'emission_categories'

    id          = db.Column(db.Integer, primary_key=True)
    scope       = db.Column(db.Enum('scope1','scope2','scope3'), nullable=False)
    category    = db.Column(db.String(50), nullable=False)   # e.g. "cat1","cat4","cat11"
    name        = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    is_relevant_shipping = db.Column(db.Boolean, default=True)

    emissions = db.relationship('Emission', back_populates='category_obj', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'scope': self.scope,
            'category': self.category, 'name': self.name,
            'description': self.description,
        }


class Emission(db.Model):
    __tablename__ = 'emissions'

    id              = db.Column(db.Integer, primary_key=True)
    company_id      = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    vessel_id       = db.Column(db.Integer, db.ForeignKey('vessels.id'), nullable=True)
    voyage_id       = db.Column(db.Integer, db.ForeignKey('voyages.id'), nullable=True)
    category_id     = db.Column(db.Integer, db.ForeignKey('emission_categories.id'), nullable=False)
    supplier_id     = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    reporting_year  = db.Column(db.Integer, nullable=False)
    reporting_period = db.Column(db.String(20))          # e.g. "2024-Q1"
    # Calculation method (GHG Protocol)
    calc_method     = db.Column(db.Enum('spend_based','average_data','supplier_specific',
                                        'hybrid','fuel_based'), nullable=False)
    # Activity data
    activity_value  = db.Column(db.Float, nullable=False)
    activity_unit   = db.Column(db.String(30), nullable=False)  # e.g. "mt_fuel", "USD", "nm"
    # Emission factor used
    emission_factor_id = db.Column(db.Integer, db.ForeignKey('emission_factors.id'))
    emission_factor_value = db.Column(db.Float)
    emission_factor_unit  = db.Column(db.String(50))
    # Results (tCO2e)
    co2_tonnes      = db.Column(db.Float, default=0.0)
    ch4_tonnes      = db.Column(db.Float, default=0.0)
    n2o_tonnes      = db.Column(db.Float, default=0.0)
    total_co2e      = db.Column(db.Float, nullable=False, default=0.0)
    # Data quality
    data_quality    = db.Column(db.Enum('primary','secondary','estimated'), default='secondary')
    confidence      = db.Column(db.Float, default=0.8)
    verified        = db.Column(db.Boolean, default=False)
    verified_by     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    verified_at     = db.Column(db.DateTime, nullable=True)
    notes           = db.Column(db.Text)
    created_by      = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vessel      = db.relationship('Vessel')
    voyage      = db.relationship('Voyage', back_populates='emissions')
    category_obj = db.relationship('EmissionCategory', back_populates='emissions')
    factor      = db.relationship('EmissionFactor')
    supplier    = db.relationship('Supplier')

    def to_dict(self):
        return {
            'id': self.id, 'company_id': self.company_id,
            'vessel_id': self.vessel_id, 'voyage_id': self.voyage_id,
            'category_id': self.category_id,
            'reporting_year': self.reporting_year,
            'reporting_period': self.reporting_period,
            'calc_method': self.calc_method,
            'activity_value': self.activity_value,
            'activity_unit': self.activity_unit,
            'co2_tonnes': self.co2_tonnes,
            'ch4_tonnes': self.ch4_tonnes,
            'n2o_tonnes': self.n2o_tonnes,
            'total_co2e': self.total_co2e,
            'data_quality': self.data_quality,
            'confidence': self.confidence,
            'verified': self.verified,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
        }