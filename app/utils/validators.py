import re

def validate_email(email):
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email or ''))

def validate_imo(imo):
    """Validate IMO number format (IMO + 7 digits)."""
    return bool(re.match(r'^IMO\d{7}$', imo or ''))

def validate_year(year):
    return isinstance(year, int) and 2000 <= year <= 2100

def validate_required(data, fields):
    missing = [f for f in fields if not data.get(f)]
    return missing

CALC_METHODS = ['spend_based', 'average_data', 'supplier_specific', 'hybrid', 'fuel_based']
FUEL_TYPES   = ['hfo', 'vlsfo', 'mdo', 'mgo', 'lng', 'methanol', 'ammonia', 'other']
SCOPES       = ['scope1', 'scope2', 'scope3']