import math
from datetime import datetime

def paginate_query(query, page, per_page=20):
    total   = query.count()
    items   = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        'items':       [i.to_dict() for i in items],
        'total':       total,
        'page':        page,
        'per_page':    per_page,
        'total_pages': max(1, math.ceil(total / per_page)),
        'has_next':    page * per_page < total,
        'has_prev':    page > 1,
    }

def success(data=None, message='OK', status=200):
    from flask import jsonify
    return jsonify({'success': True, 'message': message, 'data': data}), status

def error(message='Erreur', status=400, details=None):
    from flask import jsonify
    resp = {'success': False, 'error': message}
    if details:
        resp['details'] = details
    return jsonify(resp), status

def current_user():
    from flask_jwt_extended import get_jwt_identity
    from app.models.user import User
    return User.query.get(get_jwt_identity())

def log_action(entity_type, entity_id, action, old_val=None, new_val=None):
    from flask import request
    from app import db
    from app.models.audit_log import AuditLog
    from flask_jwt_extended import get_jwt_identity
    try:
        uid = get_jwt_identity()
    except Exception:
        uid = None
    log = AuditLog(
        user_id=uid, entity_type=entity_type, entity_id=entity_id,
        action=action, old_value=old_val, new_value=new_val,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent', '')[:255]
    )
    db.session.add(log)
    db.session.commit()