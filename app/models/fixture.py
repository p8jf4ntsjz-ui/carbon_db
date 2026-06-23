from app import db
from datetime import datetime

class FixtureSchedule(db.Model):
    """Leasing/Chartering agreements — alloue les émissions aux bonnes catégories Scope 3."""
    __tablename__ = 'fixture_schedules'

    id            = db.Column(db.Integer, primary_key=True)
    vessel_id     = db.Column(db.Integer, db.ForeignKey('vessels.id'), nullable=False)
    company_id    = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    charterer     = db.Column(db.String(200))
    fixture_type  = db.Column(db.Enum('time_charter','voyage_charter','bareboat',
                                      'contract_of_affreightment'), nullable=False)
    start_date    = db.Column(db.Date, nullable=False)
    end_date      = db.Column(db.Date)
    hire_rate     = db.Column(db.Float)                  # USD/day
    currency      = db.Column(db.String(10), default='USD')
    # Allocation rule : qui porte les émissions ?
    emission_allocation = db.Column(db.Enum('owner','charterer','split'), default='charterer')
    owner_pct     = db.Column(db.Float, default=0.0)     # % si split
    charterer_pct = db.Column(db.Float, default=100.0)
    status        = db.Column(db.Enum('active','expired','cancelled'), default='active')
    notes         = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    vessel  = db.relationship('Vessel', back_populates='fixtures')

    def to_dict(self):
        return {
            'id': self.id, 'vessel_id': self.vessel_id,
            'charterer': self.charterer, 'fixture_type': self.fixture_type,
            'start_date': str(self.start_date), 'end_date': str(self.end_date),
            'hire_rate': self.hire_rate, 'currency': self.currency,
            'emission_allocation': self.emission_allocation,
            'owner_pct': self.owner_pct, 'charterer_pct': self.charterer_pct,
            'status': self.status,
        }