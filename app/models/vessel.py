from app import db
from datetime import datetime

class Vessel(db.Model):
    __tablename__ = 'vessels'

    id             = db.Column(db.Integer, primary_key=True)
    company_id     = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name           = db.Column(db.String(150), nullable=False)
    imo_number     = db.Column(db.String(20), unique=True, nullable=False)
    vessel_type    = db.Column(db.Enum('bulk_carrier','tanker','container','ro_ro',
                                       'lng_carrier','general_cargo','cruise','other'),
                               nullable=False, default='bulk_carrier')
    flag_state     = db.Column(db.String(60))
    gross_tonnage  = db.Column(db.Float)
    dwt            = db.Column(db.Float)          # Deadweight tonnage
    built_year     = db.Column(db.Integer)
    main_engine    = db.Column(db.String(100))
    fuel_type      = db.Column(db.Enum('hfo','vlsfo','mdo','mgo','lng','methanol','ammonia','other'),
                               default='vlsfo')
    ownership_type = db.Column(db.Enum('owned','leased','chartered_in','chartered_out'),
                               default='owned')
    is_active      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company  = db.relationship('Company', back_populates='vessels')
    voyages  = db.relationship('Voyage', back_populates='vessel', lazy='dynamic')
    fixtures = db.relationship('FixtureSchedule', back_populates='vessel', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'imo_number': self.imo_number,
            'vessel_type': self.vessel_type, 'flag_state': self.flag_state,
            'gross_tonnage': self.gross_tonnage, 'dwt': self.dwt,
            'built_year': self.built_year, 'fuel_type': self.fuel_type,
            'ownership_type': self.ownership_type, 'is_active': self.is_active,
            'company_id': self.company_id,
        }