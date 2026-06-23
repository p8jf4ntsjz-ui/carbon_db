from flask import Blueprint, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                 jwt_required, get_jwt_identity)
from app.models.user import User
from app import db
from app.utils.helpers import success, error, current_user, log_action
from app.utils.validators import validate_email
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.post('/login')
def login():
    data     = request.get_json() or {}
    email    = (data.get('email') or '').strip().lower()
    password = data.get('password', '')
    if not email or not password:
        return error('Email et mot de passe requis', 400)
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error('Identifiants invalides', 401)
    if not user.is_active:
        return error('Compte désactivé', 403)
    user.last_login = datetime.utcnow()
    db.session.commit()
    access  = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)
    return success({'access_token': access, 'refresh_token': refresh,
                    'user': user.to_dict()}, 'Connexion réussie')

@auth_bp.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    uid    = get_jwt_identity()
    token  = create_access_token(identity=uid)
    return success({'access_token': token})

@auth_bp.get('/me')
@jwt_required()
def me():
    return success(current_user().to_dict())

@auth_bp.put('/me/password')
@jwt_required()
def change_password():
    data    = request.get_json() or {}
    old_pw  = data.get('current_password', '')
    new_pw  = data.get('new_password', '')
    if len(new_pw) < 8:
        return error('Le mot de passe doit contenir au moins 8 caractères', 400)
    user = current_user()
    if not user.check_password(old_pw):
        return error('Mot de passe actuel incorrect', 400)
    user.set_password(new_pw)
    db.session.commit()
    log_action('user', user.id, 'update', None, {'field': 'password'})
    return success(message='Mot de passe mis à jour')