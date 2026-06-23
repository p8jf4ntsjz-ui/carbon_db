from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import db
from app.models.emission import Emission, EmissionCategory
from app.models.emission_factor import EmissionFactor
from app.services.calculations.ghg_calculator import GHGCalculator
from app.services.calculations.data_quality import assess_quality
from app.utils.helpers import success, error, paginate_query, current_user, log_action
from datetime import datetime

emissions_bp = Blueprint('emissions', __name__)
calc = GHGCalculator()

@emissions_bp.get('/')
@jwt_required()
def list_emissions():
    user  = current_user()
    page  = int(request.args.get('page', 1))
    year  = request.args.get('year', type=int)
    scope = request.args.get('scope')
    vessel_id = request.args.get('vessel_id', type=int)

    q = Emission.query.filter_by(company_id=user.company_id)
    if year:      q = q.filter_by(reporting_year=year)
    if vessel_id: q = q.filter_by(vessel_id=vessel_id)
    if scope:
        q = q.join(EmissionCategory).filter(EmissionCategory.scope == scope)
    return success(paginate_query(q.order_by(Emission.created_at.desc()), page))

@emissions_bp.post('/')
@jwt_required()
def create_emission():
    user = current_user()
    data = request.get_json() or {}

    required = ['category_id', 'reporting_year', 'calc_method',
                'activity_value', 'activity_unit']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error('Champs manquants', 400, {'missing': missing})

    # Calcul automatique selon la méthode
    method = data['calc_method']
    result = {}

    if method == 'fuel_based':
        result = calc.scope1_fuel_combustion(
            float(data['activity_value']),
            data.get('fuel_type', 'vlsfo')
        )
    elif method == 'spend_based':
        result = calc.scope3_spend_based(
            float(data['activity_value']),
            data.get('spend_category', 'other')
        )
    elif method in ('average_data', 'supplier_specific'):
        ef_id = data.get('emission_factor_id')
        ef    = EmissionFactor.query.get(ef_id) if ef_id else None
        factor_val = ef.total_co2e_factor if ef else float(data.get('emission_factor_value', 0))
        result = calc.scope3_average_data(float(data['activity_value']),
                                           data['activity_unit'], factor_val)

    # Qualité de données
    dq = assess_quality(method,
                         bool(data.get('emission_factor_id')),
                         False, 0)

    emission = Emission(
        company_id=user.company_id,
        vessel_id=data.get('vessel_id'),
        voyage_id=data.get('voyage_id'),
        category_id=data['category_id'],
        supplier_id=data.get('supplier_id'),
        reporting_year=data['reporting_year'],
        reporting_period=data.get('reporting_period'),
        calc_method=method,
        activity_value=float(data['activity_value']),
        activity_unit=data['activity_unit'],
        emission_factor_id=data.get('emission_factor_id'),
        emission_factor_value=data.get('emission_factor_value'),
        emission_factor_unit=data.get('emission_factor_unit'),
        co2_tonnes=result.get('co2_tonnes', 0),
        ch4_tonnes=result.get('ch4_tonnes', 0),
        n2o_tonnes=result.get('n2o_tonnes', 0),
        total_co2e=result.get('total_co2e', 0),
        data_quality=dq['label'],
        confidence=dq['confidence'],
        notes=data.get('notes'),
        created_by=user.id,
    )
    db.session.add(emission)
    db.session.commit()
    log_action('emission', emission.id, 'create', None, emission.to_dict())
    return success(emission.to_dict(), 'Émission enregistrée', 201)

@emissions_bp.get('/<int:eid>')
@jwt_required()
def get_emission(eid):
    user = current_user()
    em   = Emission.query.filter_by(id=eid, company_id=user.company_id).first_or_404()
    return success(em.to_dict())

@emissions_bp.put('/<int:eid>')
@jwt_required()
def update_emission(eid):
    user = current_user()
    em   = Emission.query.filter_by(id=eid, company_id=user.company_id).first_or_404()
    old  = em.to_dict()
    data = request.get_json() or {}
    for field in ('activity_value','activity_unit','notes','reporting_period'):
        if field in data:
            setattr(em, field, data[field])
    db.session.commit()
    log_action('emission', em.id, 'update', old, em.to_dict())
    return success(em.to_dict(), 'Mis à jour')

@emissions_bp.delete('/<int:eid>')
@jwt_required()
def delete_emission(eid):
    user = current_user()
    em   = Emission.query.filter_by(id=eid, company_id=user.company_id).first_or_404()
    log_action('emission', em.id, 'delete', em.to_dict(), None)
    db.session.delete(em)
    db.session.commit()
    return success(message='Émission supprimée')

@emissions_bp.post('/<int:eid>/verify')
@jwt_required()
def verify_emission(eid):
    user = current_user()
    if user.role not in ('admin', 'superadmin', 'manager'):
        return error('Rôle insuffisant pour vérifier', 403)
    em = Emission.query.filter_by(id=eid, company_id=user.company_id).first_or_404()
    em.verified    = True
    em.verified_by = user.id
    em.verified_at = datetime.utcnow()
    db.session.commit()
    log_action('emission', em.id, 'verify', None, {'verified_by': user.id})
    return success(em.to_dict(), 'Émission vérifiée')

@emissions_bp.get('/summary/by-scope')
@jwt_required()
def summary_by_scope():
    """Agrégat tCO2e par scope pour l'année courante."""
    user = current_user()
    year = request.args.get('year', type=int, default=datetime.utcnow().year)
    rows = (db.session.query(EmissionCategory.scope,
                              db.func.sum(Emission.total_co2e).label('total'))
            .join(Emission, Emission.category_id == EmissionCategory.id)
            .filter(Emission.company_id == user.company_id,
                    Emission.reporting_year == year)
            .group_by(EmissionCategory.scope)
            .all())
    data = [{'scope': r.scope, 'total_co2e': round(float(r.total), 2)} for r in rows]
    grand_total = sum(d['total_co2e'] for d in data)
    return success({'year': year, 'by_scope': data, 'grand_total': round(grand_total, 2)})