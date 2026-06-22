from __init__ import create_app, db
from models import EmissionFactor

app = create_app()

def seed_emission_factors():
    """Importe un jeu de facteurs de démonstration sans appeler l'API."""
    with app.app_context():
        if EmissionFactor.query.count() > 0:
            print('ℹ️  Facteurs déjà présents.')
            return

        demo_factors = [
            EmissionFactor(activity_id='electricity-supply_grid-source_residual_mix',
                name='Electricity (grid)', category='Energy', sector='Electricity',
                source='IEA', region='TN', unit_type='Energy', unit='kWh', factor_value=0.437, year=2021),
            EmissionFactor(activity_id='passenger_vehicle-vehicle_type_car-fuel_source_petrol',
                name='Petrol car', category='Transport', sector='Road',
                source='ADEME', region='FR', unit_type='Distance', unit='km', factor_value=0.192, year=2022),
            EmissionFactor(activity_id='freight_flight-route_type_domestic-weight_kg',
                name='Air freight domestic', category='Transport', sector='Air',
                source='DEFRA', region='GB', unit_type='Weight', unit='kg', factor_value=1.23, year=2023),
            EmissionFactor(activity_id='material-cotton',
                name='Cotton (raw)', category='Material Use', sector='Textiles',
                source='ecoinvent', region='global', unit_type='Weight', unit='kg', factor_value=5.89, year=2022),
            EmissionFactor(activity_id='material-polyester',
                name='Polyester (virgin)', category='Material Use', sector='Textiles',
                source='ecoinvent', region='global', unit_type='Weight', unit='kg', factor_value=9.52, year=2022),
            EmissionFactor(activity_id='waste-type_mixed',
                name='Mixed waste', category='Waste', sector='Solid Waste',
                source='EPA', region='US', unit_type='Weight', unit='kg', factor_value=0.468, year=2023),
        ]
        db.session.bulk_save_objects(demo_factors)
        db.session.commit()
        print(f'✅ {len(demo_factors)} facteurs de démonstration insérés.')