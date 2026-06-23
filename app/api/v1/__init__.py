from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

from .auth       import auth_bp
from .companies  import companies_bp
from .vessels    import vessels_bp
from .voyages    import voyages_bp
from .emissions  import emissions_bp
from .factors    import factors_bp
from .fixtures   import fixtures_bp
from .suppliers  import suppliers_bp
from .reports    import reports_bp
from .dashboard  import dashboard_bp
from .audit      import audit_bp

api_v1.register_blueprint(auth_bp,       url_prefix='/auth')
api_v1.register_blueprint(companies_bp,  url_prefix='/companies')
api_v1.register_blueprint(vessels_bp,    url_prefix='/vessels')
api_v1.register_blueprint(voyages_bp,    url_prefix='/voyages')
api_v1.register_blueprint(emissions_bp,  url_prefix='/emissions')
api_v1.register_blueprint(factors_bp,    url_prefix='/emission-factors')
api_v1.register_blueprint(fixtures_bp,   url_prefix='/fixtures')
api_v1.register_blueprint(suppliers_bp,  url_prefix='/suppliers')
api_v1.register_blueprint(reports_bp,    url_prefix='/reports')
api_v1.register_blueprint(dashboard_bp,  url_prefix='/dashboard')
api_v1.register_blueprint(audit_bp,      url_prefix='/audit')