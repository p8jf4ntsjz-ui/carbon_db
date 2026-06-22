import os
from datetime import timedelta

class Config:
    # ... (vos configs existantes) ...
    CLIMATIQ_API_KEY = os.environ.get('CLIMATIQ_API_KEY') or 'YOUR_API_KEY_HERE'
    CLIMATIQ_DATA_VERSION = '^21'
    # Filtres par défaut pour votre secteur (textile/matières selon vos fichiers Excel)
    CLIMATIQ_DEFAULT_FILTERS = {
        "data_version": "^21",
        "category": "Material Use",   # adapter selon vos secteurs
        "unit_type": "Weight",
    }