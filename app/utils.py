import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from flask import current_app
from models import EmissionFactor, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

CLIMATIQ_URL = "https://api.climatiq.io/data/v1/search"

def get_climatiq_session(api_key: str):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.headers.update({"Authorization": f"Bearer {api_key}"})
    return session


def sync_emission_factors(api_key: str, filters: dict = None) -> dict:
    """
    Synchronise les facteurs d'émission depuis l'API Climatiq.
    Equivalent Python du notebook Emission-Factor-Database-Extraction.ipynb.
    
    filters: dict avec clés optionnelles :
        data_version, query, activity_id, category,
        sector, region, source, year, unit_type
    """
    if filters is None:
        filters = {"data_version": "^21"}

    session = get_climatiq_session(api_key)
    query_str = "?results_per_page=500"
    for key, value in filters.items():
        if value:
            query_str += f"&{key}={value}"

    no_of_pages = 1
    current_page = 1
    all_results = []
    inserted = updated = 0

    try:
        while current_page <= no_of_pages:
            response = session.get(
                f"{CLIMATIQ_URL}{query_str}&page={current_page}", timeout=30
            )
            response.raise_for_status()
            data = response.json()
            no_of_pages = data.get("last_page", 1)
            all_results.extend(data.get("results", []))
            current_page += 1

        # Upsert into DB
        for row in all_results:
            ef = EmissionFactor.query.filter_by(
                activity_id=row.get('activity_id'),
                region=row.get('region', ''),
                year=row.get('year')
            ).first()

            factor_val = None
            if row.get('factor'):
                factor_val = row['factor'].get('co2e')

            if ef:
                ef.factor_value = factor_val
                ef.last_synced = datetime.utcnow()
                updated += 1
            else:
                ef = EmissionFactor(
                    activity_id  = row.get('activity_id', ''),
                    name         = row.get('name', ''),
                    category     = row.get('category', ''),
                    sector       = row.get('sector', ''),
                    source       = row.get('source', ''),
                    region       = row.get('region', ''),
                    unit_type    = row.get('unit_type', ''),
                    unit         = row.get('unit', ''),
                    factor_value = factor_val,
                    year         = row.get('year'),
                    data_version = row.get('data_version', ''),
                )
                db.session.add(ef)
                inserted += 1

        db.session.commit()
        logger.info(f"Climatiq sync: {inserted} inserted, {updated} updated")
        return {'status': 'ok', 'inserted': inserted, 'updated': updated, 'total': len(all_results)}

    except Exception as e:
        db.session.rollback()
        logger.error(f"Climatiq sync error: {e}")
        return {'status': 'error', 'message': str(e)}


def calculate_emission(quantity: float, activity_id: str, region: str = None) -> dict:
    """Calcule les émissions CO2e pour une activité et une quantité données."""
    q = EmissionFactor.query.filter_by(activity_id=activity_id)
    if region:
        q = q.filter_by(region=region)
    factor = q.order_by(EmissionFactor.year.desc()).first()
    if not factor or not factor.factor_value:
        return {'co2e_kg': None, 'error': 'Facteur introuvable'}
    co2e = round(quantity * factor.factor_value, 4)
    return {
        'co2e_kg': co2e,
        'factor_value': factor.factor_value,
        'unit': factor.unit,
        'source': factor.source,
        'activity_id': activity_id,
    }