from app import create_app, db
import os

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.cli.command('init-db')
def init_db():
    """Crée toutes les tables."""
    db.create_all()
    print('✅ Base de données initialisée.')

@app.cli.command('seed-db')
def seed_db():
    """Insère les données de référence (catégories GHG, facteurs d'émission)."""
    from app.models.emission import EmissionCategory
    from app.models.emission_factor import EmissionFactor
    from app.models.user import User
    from app.models.company import Company

    # Catégories GHG Protocol
    cats = [
        ('scope1', 'direct',  'Combustion directe (carburant navire)'),
        ('scope1', 'fugitive','Émissions fugitives'),
        ('scope2', 'market',  'Électricité achetée — méthode marché'),
        ('scope2', 'location','Électricité achetée — méthode localisation'),
        ('scope3', 'cat1',    'Achats de biens et services'),
        ('scope3', 'cat3',    'Activités liées à l\'énergie'),
        ('scope3', 'cat4',    'Transport et distribution — amont'),
        ('scope3', 'cat5',    'Déchets générés en opération'),
        ('scope3', 'cat6',    'Voyages d\'affaires'),
        ('scope3', 'cat7',    'Déplacements domicile-travail'),
        ('scope3', 'cat9',    'Transport et distribution — aval'),
        ('scope3', 'cat11',   'Utilisation des produits vendus'),
    ]
    for scope, cat, name in cats:
        if not EmissionCategory.query.filter_by(scope=scope, category=cat).first():
            db.session.add(EmissionCategory(scope=scope, category=cat, name=name))

    # Facteurs d'émission par défaut (IMO)
    fuel_factors = [
        ('IMO', 'hfo',   3.114, 0.00006, 0.00015, 'tCO2e/mt_fuel'),
        ('IMO', 'vlsfo', 3.151, 0.00006, 0.00015, 'tCO2e/mt_fuel'),
        ('IMO', 'mgo',   3.206, 0.00006, 0.00015, 'tCO2e/mt_fuel'),
        ('IMO', 'lng',   2.750, 0.00150, 0.00010, 'tCO2e/mt_fuel'),
    ]
    for src, fuel, co2, ch4, n2o, unit in fuel_factors:
        if not EmissionFactor.query.filter_by(source=src, fuel_type=fuel).first():
            db.session.add(EmissionFactor(source=src, fuel_type=fuel,
                co2_factor=co2, ch4_factor=ch4, n2o_factor=n2o, unit=unit,
                is_verified=True, data_quality='secondary', year=2023))

    # Compte admin par défaut
    if not User.query.filter_by(email='admin@carbonpath.com').first():
        co = Company(name='CarbonPath Demo', type='ship_owner', country='TN')
        db.session.add(co)
        db.session.flush()
        u = User(first_name='Admin', last_name='CarbonPath',
                  email='admin@carbonpath.com', role='superadmin', company_id=co.id)
        u.set_password('Admin1234!')
        db.session.add(u)

    db.session.commit()
    print('✅ Données de référence insérées.')
    print('   👤 admin@carbonpath.com / Admin1234!')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)