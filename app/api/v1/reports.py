from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required
from app import db
from app.models.report import Report
from app.models.emission import Emission, EmissionCategory
from app.utils.helpers import success, error, current_user, log_action
from datetime import datetime
import io, os, json

reports_bp = Blueprint('reports', __name__)

@reports_bp.get('/')
@jwt_required()
def list_reports():
    user    = current_user()
    reports = Report.query.filter_by(company_id=user.company_id)\
                    .order_by(Report.created_at.desc()).all()
    return success([r.to_dict() for r in reports])

@reports_bp.post('/generate')
@jwt_required()
def generate_report():
    user = current_user()
    data = request.get_json() or {}
    year = data.get('reporting_year', datetime.utcnow().year)
    fmt  = data.get('format', 'json')

    report = Report(
        company_id=user.company_id,
        title=data.get('title', f'GHG Report {year}'),
        report_type=data.get('report_type', 'annual'),
        reporting_year=year,
        scope_filter=data.get('scope_filter', 'all'),
        format=fmt,
        status='generating',
        generated_by=user.id,
    )
    db.session.add(report)
    db.session.commit()

    # Collecte des données
    q = Emission.query.filter_by(company_id=user.company_id, reporting_year=year)
    if data.get('scope_filter') and data['scope_filter'] != 'all':
        q = q.join(EmissionCategory).filter(EmissionCategory.scope == data['scope_filter'])
    emissions = q.all()

    summary = {
        'company_id': user.company_id,
        'reporting_year': year,
        'total_records': len(emissions),
        'total_co2e': round(sum(e.total_co2e for e in emissions), 2),
        'by_scope': {},
        'by_method': {},
        'generated_at': datetime.utcnow().isoformat(),
    }
    for e in emissions:
        cat = e.category_obj
        if cat:
            summary['by_scope'][cat.scope] = round(
                summary['by_scope'].get(cat.scope, 0) + e.total_co2e, 2)
        summary['by_method'][e.calc_method] = round(
            summary['by_method'].get(e.calc_method, 0) + e.total_co2e, 2)

    # Sauvegarde JSON
    folder = os.path.join('uploads', 'reports')
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f'report_{report.id}.json')
    with open(filepath, 'w') as f:
        json.dump(summary, f, indent=2)

    report.status       = 'ready'
    report.file_path    = filepath
    report.generated_at = datetime.utcnow()
    db.session.commit()

    log_action('report', report.id, 'create', None, summary)
    return success({'report': report.to_dict(), 'summary': summary}, 'Rapport généré', 201)

@reports_bp.get('/<int:rid>/download')
@jwt_required()
def download_report(rid):
    user   = current_user()
    report = Report.query.filter_by(id=rid, company_id=user.company_id).first_or_404()
    if report.status != 'ready' or not report.file_path:
        return error('Rapport non disponible', 404)
    return send_file(report.file_path, as_attachment=True,
                     download_name=f"ghg_report_{report.reporting_year}.json")