from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User

def jwt_required_custom(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        uid = get_jwt_identity()
        user = User.query.get(uid)
        if not user or not user.is_active:
            return jsonify({'error': 'Accès refusé'}), 403
        return f(*args, **kwargs)
    return decorated

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            uid  = get_jwt_identity()
            user = User.query.get(uid)
            if not user or user.role not in roles:
                return jsonify({'error': 'Rôle insuffisant'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def company_access(f):
    """Vérifie que l'utilisateur accède aux ressources de sa propre company."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        uid  = get_jwt_identity()
        user = User.query.get(uid)
        company_id = kwargs.get('company_id')
        if user.role not in ('superadmin',) and user.company_id != company_id:
            return jsonify({'error': 'Accès non autorisé à cette organisation'}), 403
        return f(*args, **kwargs)
    return decorated