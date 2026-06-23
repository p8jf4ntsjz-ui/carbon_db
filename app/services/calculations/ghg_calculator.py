"""
GHG Protocol compliant calculator.
Supports: Scope 1 (direct fuel combustion),
          Scope 2 (purchased energy),
          Scope 3 (upstream + downstream, 15 categories).
"""

# ── IPCC AR6 GWP 100-year ──────────────────────────────────────────────
GWP = {'co2': 1.0, 'ch4': 27.9, 'n2o': 273.0}

# ── Default IMO/IPCC emission factors (kgCO2e/mt_fuel) ────────────────
FUEL_EMISSION_FACTORS = {
    'hfo':      {'co2': 3.114, 'ch4': 0.00006, 'n2o': 0.00015},
    'vlsfo':    {'co2': 3.151, 'ch4': 0.00006, 'n2o': 0.00015},
    'mdo':      {'co2': 3.206, 'ch4': 0.00006, 'n2o': 0.00015},
    'mgo':      {'co2': 3.206, 'ch4': 0.00006, 'n2o': 0.00015},
    'lng':      {'co2': 2.750, 'ch4': 0.00150, 'n2o': 0.00010},
    'methanol': {'co2': 1.375, 'ch4': 0.00003, 'n2o': 0.00005},
    'ammonia':  {'co2': 0.0,   'ch4': 0.00000, 'n2o': 0.02100},
}

# ── Spend-based factors (kgCO2e/USD) — moyenne sectorielle maritime ───
SPEND_FACTORS = {
    'fuel':         2.85,
    'port_services': 0.42,
    'maintenance':  0.38,
    'food':         1.95,
    'logistics':    0.67,
    'other':        0.55,
}


class GHGCalculator:

    # ── SCOPE 1 : combustion directe ──────────────────────────────────
    @staticmethod
    def scope1_fuel_combustion(fuel_consumed_mt: float, fuel_type: str) -> dict:
        """
        Calcule les émissions Scope 1 par combustion de carburant.
        fuel_consumed_mt : tonnes métriques de carburant
        fuel_type        : 'hfo','vlsfo','mdo','mgo','lng','methanol','ammonia'
        Retourne : {co2, ch4, n2o, total_co2e} en tCO2e
        """
        factors = FUEL_EMISSION_FACTORS.get(fuel_type, FUEL_EMISSION_FACTORS['vlsfo'])
        co2 = fuel_consumed_mt * factors['co2']
        ch4 = fuel_consumed_mt * factors['ch4']
        n2o = fuel_consumed_mt * factors['n2o']
        total = co2 * GWP['co2'] + ch4 * GWP['ch4'] + n2o * GWP['n2o']
        return {
            'co2_tonnes': round(co2, 4),
            'ch4_tonnes': round(ch4, 4),
            'n2o_tonnes': round(n2o, 4),
            'total_co2e': round(total, 4),
            'method':     'fuel_based',
            'scope':      'scope1',
        }

    # ── SCOPE 2 : énergie achetée ──────────────────────────────────────
    @staticmethod
    def scope2_purchased_energy(kwh: float, grid_factor_kg_per_kwh: float = 0.233) -> dict:
        """
        Calcule les émissions Scope 2 (électricité à quai).
        kwh                  : kWh consommés
        grid_factor_kg_per_kwh : facteur réseau (défaut : mix EU moyen)
        """
        co2 = kwh * grid_factor_kg_per_kwh / 1000   # → tonnes
        return {
            'co2_tonnes': round(co2, 4),
            'ch4_tonnes': 0.0,
            'n2o_tonnes': 0.0,
            'total_co2e': round(co2, 4),
            'method':     'average_data',
            'scope':      'scope2',
        }

    # ── SCOPE 3 : spend-based ──────────────────────────────────────────
    @staticmethod
    def scope3_spend_based(spend_usd: float, category: str) -> dict:
        """
        Scope 3 — méthode spend-based (Cat 1 achats, Cat 4 transport amont…).
        spend_usd : montant en USD
        category  : clé dans SPEND_FACTORS
        """
        factor = SPEND_FACTORS.get(category, SPEND_FACTORS['other'])
        total  = spend_usd * factor / 1000   # kg → tonnes
        return {
            'co2_tonnes': round(total, 4),
            'ch4_tonnes': 0.0,
            'n2o_tonnes': 0.0,
            'total_co2e': round(total, 4),
            'method':     'spend_based',
            'scope':      'scope3',
        }

    # ── SCOPE 3 : average-data ─────────────────────────────────────────
    @staticmethod
    def scope3_average_data(activity_value: float, activity_unit: str,
                             emission_factor: float) -> dict:
        """
        Scope 3 — méthode average-data.
        activity_value  : quantité (ex: nm, tonnes-km)
        emission_factor : kgCO2e/unité
        """
        total = activity_value * emission_factor / 1000
        return {
            'co2_tonnes': round(total, 4),
            'ch4_tonnes': 0.0,
            'n2o_tonnes': 0.0,
            'total_co2e': round(total, 4),
            'method':     'average_data',
            'scope':      'scope3',
        }

    # ── SCOPE 3 : supplier-specific ───────────────────────────────────
    @staticmethod
    def scope3_supplier_specific(activity_value: float,
                                  supplier_factor: float,
                                  factor_unit: str) -> dict:
        """
        Scope 3 Cat 1 — facteur fourni directement par le fournisseur.
        Meilleure qualité de donnée selon GHG Protocol.
        """
        total = activity_value * supplier_factor / 1000
        return {
            'co2_tonnes': round(total, 4),
            'ch4_tonnes': 0.0,
            'n2o_tonnes': 0.0,
            'total_co2e': round(total, 4),
            'method':     'supplier_specific',
            'scope':      'scope3',
        }

    # ── Utilitaire : agréger plusieurs émissions ───────────────────────
    @staticmethod
    def aggregate(emission_list: list) -> dict:
        total_co2  = sum(e.get('co2_tonnes', 0) for e in emission_list)
        total_ch4  = sum(e.get('ch4_tonnes', 0) for e in emission_list)
        total_n2o  = sum(e.get('n2o_tonnes', 0) for e in emission_list)
        total_co2e = sum(e.get('total_co2e', 0) for e in emission_list)
        return {
            'co2_tonnes': round(total_co2, 4),
            'ch4_tonnes': round(total_ch4, 4),
            'n2o_tonnes': round(total_n2o, 4),
            'total_co2e': round(total_co2e, 4),
        }

    # ── Indice CII (Carbon Intensity Indicator — IMO) ─────────────────
    @staticmethod
    def compute_cii(co2_tonnes: float, distance_nm: float, dwt: float) -> dict:
        """
        CII = CO2 (grammes) / (DWT × distance nautique)
        Rating: A(<0.86) B(<0.94) C(<1.06) D(<1.19) E(>=1.19) — valeurs indicatives
        """
        if not distance_nm or not dwt:
            return {'cii': None, 'rating': 'N/A'}
        cii = (co2_tonnes * 1e6) / (dwt * distance_nm)
        if   cii < 0.86: rating = 'A'
        elif cii < 0.94: rating = 'B'
        elif cii < 1.06: rating = 'C'
        elif cii < 1.19: rating = 'D'
        else:             rating = 'E'
        return {'cii': round(cii, 4), 'rating': rating}