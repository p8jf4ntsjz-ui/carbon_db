from app import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'reports'

    id              = db.Column(db.Integer, primary_key=True)
    company_id      = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title           = db.Column(db.String(200), nullable=False)
    report_type     = db.Column(db.Enum('annual','quarterly','vessel','custom'), default='annual')
    reporting_year  = db.Column(db.Integer, nullable=False)
    scope_filter    = db.Column(db.String(30), default='all')     # scope1,scope2,scope3,all
    format          = db.Column(db.Enum('pdf','excel','json','csv'), default='pdf')
    status          = db.Column(db.Enum('pending','generating','ready','failed'), default='pending')
    file_path       = db.Column(db.String(255))
    generated_by    = db.Column(db.Integer, db.ForeignKey('users.id'))
    generated_at    = db.Column(db.DateTime)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', back_populates='reports')

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title,
            'report_type': self.report_type,
            'reporting_year': self.reporting_year,
            'scope_filter': self.scope_filter,
            'format': self.format, 'status': self.status,
            'file_path': self.file_path,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat(),
        }