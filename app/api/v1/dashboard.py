from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import db
from app.models.emission import Emission, EmissionCategory
from app.models.vessel import Vessel
from app.services.ml.predictor import EmissionPredictor
from app.utils.helpers import success, current_user
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)
predictor    = EmissionPredictor()

@dashboard_bp.get('/kpis')
@jwt_required()
def kpis():
    user = current_user()
    year = request.args.get('year', type=int, default=datetime.utcnow().year)

    total = (db.session.query(db.func.sum(Emission.total_co2e))
             .filter_by(company_id=user.company_id, reporting_year=year)
             .scalar() or 0)

    by_scope = (db.session.query(EmissionCategory.scope,
                                  db.func.sum(Emission.total_co2e))
                .join(Emission, Emission.category_id == EmissionCategory.id)
                .filter(Emission.company_id == user.company_id,
                        Emission.reporting_year == year)
                .group_by(EmissionCategory.scope).all())

    scope_dict = {s: round(float(v), 2) for s, v in by_scope}

    vessels_count = Vessel.query.filter_by(company_id=user.company_id, is_active=True).count()

    verified = (Emission.query
                .filter_by(company_id=user.company_id,
                            reporting_year=year, verified=True).count())
    total_em = (Emission.query
                .filter_by(company_id=user.company_id, reporting_year=year).count())

    return success({
        'year':               year,
        'total_co2e':         round(float(total), 2),
        'scope1':             scope_dict.get('scope1', 0),
        'scope2':             scope_dict.get('scope2', 0),
        'scope3':             scope_dict.get('scope3', 0),
        'active_vessels':     vessels_count,
        'verification_rate':  round(verified / total_em * 100, 1) if total_em else 0,
        'total_records':      total_em,
    })

@dashboard_bp.get('/trend')
@jwt_required()
def trend():
    user = current_user()
    rows = (db.session.query(Emission.reporting_year,
                              db.func.sum(Emission.total_co2e).label('total'))
            .filter_by(company_id=user.company_id)
            .group_by(Emission.reporting_year)
            .order_by(Emission.reporting_year).all())
    yearly = [{'year': int(r.reporting_year), 'total_co2e': round(float(r.total), 2)}
               for r in rows]
    forecast = predictor.predict_annual_trend(yearly)
    return success({'historical': yearly, 'forecast': forecast})

@dashboard_bp.get('/by-vessel')
@jwt_required()
def by_vessel():
    user = current_user()
    year = request.args.get('year', type=int, default=datetime.utcnow().year)
    rows = (db.session.query(Vessel.name, Vessel.imo_number,
                              db.func.sum(Emission.total_co2e).label('total'))
            .join(Emission, Emission.vessel_id == Vessel.id)
            .filter(Emission.company_id == user.company_id,
                    Emission.reporting_year == year)
            .group_by(Vessel.id, Vessel.name, Vessel.imo_number)
            .order_by(db.text('total DESC')).all())
    data = [{'vessel': r.name, 'imo': r.imo_number,
              'total_co2e': round(float(r.total), 2)} for r in rows]
    return success(data)

@dashboard_bp.get('/anomalies')
@jwt_required()
def anomalies():
    user = current_user()
    year = request.args.get('year', type=int, default=datetime.utcnow().year)
    records = [e.to_dict() for e in
               Emission.query.filter_by(company_id=user.company_id,
                                         reporting_year=year).all()]
    detected = predictor.detect_anomalies(records)
    return success({'count': len(detected), 'anomalies': detected})