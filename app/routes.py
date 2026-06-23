from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
from app.utils_root import sync_emission_factors, calculate_emission
from app.models_root import EmissionFactor, EmissionEntry
from app import db

# Create blueprint
main = Blueprint('main', __name__)

# Custom decorator for admin-only routes
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Vous devez être administrateur.', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# ─── CARBON DASHBOARD ────────────────────────────────────────
@main.route('/carbon')
@login_required
def carbon_dashboard():
    """Vue principale du tableau de bord carbone."""
    from sqlalchemy import func, extract

    # Total CO2e par scope
    by_scope = db.session.query(
        EmissionEntry.scope,
        func.sum(EmissionEntry.co2e_kg).label('total')
    ).filter_by(user_id=current_user.id)\
     .group_by(EmissionEntry.scope).all()

    # Total par catégorie (via join avec EmissionFactor)
    by_category = db.session.query(
        EmissionFactor.category,
        func.sum(EmissionEntry.co2e_kg).label('total')
    ).join(EmissionFactor, EmissionEntry.factor_id == EmissionFactor.id)\
     .filter(EmissionEntry.user_id == current_user.id)\
     .group_by(EmissionFactor.category)\
     .order_by(func.sum(EmissionEntry.co2e_kg).desc()).all()

    # Tendance mensuelle
    monthly = db.session.query(
        extract('month', EmissionEntry.date).label('month'),
        func.sum(EmissionEntry.co2e_kg).label('total')
    ).filter(
        EmissionEntry.user_id == current_user.id,
        extract('year', EmissionEntry.date) == datetime.utcnow().year
    ).group_by('month').order_by('month').all()

    total_co2e = db.session.query(func.sum(EmissionEntry.co2e_kg))\
        .filter_by(user_id=current_user.id).scalar() or 0

    recent = EmissionEntry.query.filter_by(user_id=current_user.id)\
        .order_by(EmissionEntry.created_at.desc()).limit(10).all()

    return render_template('carbon_dashboard.html',
        by_scope=by_scope, by_category=by_category,
        monthly=monthly, total_co2e=total_co2e, recent=recent)


@main.route('/carbon/add', methods=['GET', 'POST'])
@login_required
def add_emission():
    """Ajouter une entrée d'émission en sélectionnant un facteur Climatiq."""
    if request.method == 'POST':
        activity_id = request.form.get('activity_id')
        quantity    = float(request.form.get('quantity', 0))
        scope       = request.form.get('scope', '3')
        date_str    = request.form.get('date')
        notes       = request.form.get('notes', '')

        factor = EmissionFactor.query.filter_by(activity_id=activity_id)\
            .order_by(EmissionFactor.year.desc()).first()
        if not factor:
            flash('Facteur d\'émission introuvable.', 'error')
            return redirect(url_for('main.add_emission'))

        entry = EmissionEntry(
            user_id=current_user.id, factor_id=factor.id,
            activity_id=activity_id, quantity=quantity,
            unit=factor.unit, scope=scope, notes=notes,
            date=datetime.strptime(date_str, '%Y-%m-%d').date()
        )
        entry.calculate_co2e()
        db.session.add(entry)
        db.session.commit()
        flash(f'Émission de {entry.co2e_kg:.2f} kgCO₂e enregistrée.', 'success')
        return redirect(url_for('main.carbon_dashboard'))

    categories = db.session.query(EmissionFactor.category).distinct().all()
    return render_template('add_emission.html', categories=categories)


# ─── API : Recherche de facteurs Climatiq ────────────────────
@main.route('/api/emission-factors/search')
@login_required
def api_search_factors():
    """Recherche de facteurs d'émission stockés en base."""
    q        = request.args.get('q', '')
    category = request.args.get('category', '')
    sector   = request.args.get('sector', '')
    region   = request.args.get('region', '')
    limit    = request.args.get('limit', 50, type=int)

    query = EmissionFactor.query
    if q:
        query = query.filter(EmissionFactor.name.ilike(f'%{q}%'))
    if category:
        query = query.filter_by(category=category)
    if sector:
        query = query.filter_by(sector=sector)
    if region:
        query = query.filter_by(region=region)

    factors = query.order_by(EmissionFactor.name).limit(limit).all()
    return jsonify([f.to_dict() for f in factors])


# ─── Admin : Synchronisation Climatiq ────────────────────────
@main.route('/admin/climatiq/sync', methods=['POST'])
@login_required
@admin_required
def sync_climatiq():
    """Lance une synchronisation manuelle depuis l'API Climatiq."""
    api_key = current_app.config.get('CLIMATIQ_API_KEY')
    filters = {
        'data_version': request.form.get('data_version', '^21'),
        'category':     request.form.get('category', ''),
        'sector':       request.form.get('sector', ''),
        'region':       request.form.get('region', ''),
        'unit_type':    request.form.get('unit_type', ''),
        'year':         request.form.get('year', ''),
    }
    result = sync_emission_factors(api_key, filters)
    if result['status'] == 'ok':
        flash(f"Sync OK — {result['inserted']} nouveaux, {result['updated']} mis à jour.", 'success')
    else:
        flash(f"Erreur sync Climatiq : {result['message']}", 'error')
    return redirect(url_for('main.manage_users'))


# ─── API JSON : résumé CO2e pour graphiques ──────────────────
@main.route('/api/carbon/summary')
@login_required
def api_carbon_summary():
    from sqlalchemy import func, extract
    year = request.args.get('year', datetime.utcnow().year, type=int)

    monthly = db.session.query(
        extract('month', EmissionEntry.date).label('m'),
        func.sum(EmissionEntry.co2e_kg).label('total')
    ).filter(
        EmissionEntry.user_id == current_user.id,
        extract('year', EmissionEntry.date) == year
    ).group_by('m').order_by('m').all()

    by_scope = db.session.query(
        EmissionEntry.scope,
        func.sum(EmissionEntry.co2e_kg)
    ).filter_by(user_id=current_user.id).group_by(EmissionEntry.scope).all()

    return jsonify({
        'monthly': [{'month': int(r.m), 'co2e_kg': float(r.total or 0)} for r in monthly],
        'by_scope': {r[0]: float(r[1] or 0) for r in by_scope},
    })