from app import db
from datetime import datetime

class AuditLog(db.Model):
    """Change log complet pour traçabilité GHG Protocol."""
    __tablename__ = 'audit_logs'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    company_id  = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    entity_type = db.Column(db.String(50), nullable=False)   # 'emission','vessel','voyage'...
    entity_id   = db.Column(db.Integer, nullable=False)
    action      = db.Column(db.Enum('create','update','delete','verify','export'), nullable=False)
    old_value   = db.Column(db.JSON)
    new_value   = db.Column(db.JSON)
    ip_address  = db.Column(db.String(45))
    user_agent  = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'created_at': self.created_at.isoformat(),
        }