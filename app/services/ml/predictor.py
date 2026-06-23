"""
ML module : prédit les émissions futures et détecte les anomalies.
Utilise scikit-learn (LinearRegression + IsolationForest).
"""
import numpy as np
from datetime import datetime

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class EmissionPredictor:

    def predict_annual_trend(self, yearly_data: list[dict]) -> dict:
        """
        Prédit les émissions pour N+1 à N+3.
        yearly_data : [{'year': 2020, 'total_co2e': 1200.5}, ...]
        """
        if not SKLEARN_AVAILABLE or len(yearly_data) < 3:
            return {'error': 'Données insuffisantes (minimum 3 ans requis)'}

        years  = np.array([d['year'] for d in yearly_data]).reshape(-1, 1)
        values = np.array([d['total_co2e'] for d in yearly_data])

        model = LinearRegression()
        model.fit(years, values)

        last_year = max(d['year'] for d in yearly_data)
        future    = np.array([[last_year + 1], [last_year + 2], [last_year + 3]])
        preds     = model.predict(future)

        trend_pct = ((model.coef_[0]) / np.mean(values)) * 100

        return {
            'predictions': [
                {'year': int(future[i][0]), 'predicted_co2e': round(max(0, preds[i]), 2)}
                for i in range(3)
            ],
            'trend_pct_per_year': round(trend_pct, 2),
            'trend_direction': 'hausse' if trend_pct > 0 else 'baisse',
            'r2_score': round(model.score(years, values), 3),
        }

    def detect_anomalies(self, emission_records: list[dict]) -> list[dict]:
        """
        Détecte les enregistrements anormaux (outliers).
        emission_records : [{'id':1, 'total_co2e': 500.0, ...}, ...]
        """
        if not SKLEARN_AVAILABLE or len(emission_records) < 10:
            return []

        values = np.array([r['total_co2e'] for r in emission_records]).reshape(-1, 1)
        scaler = StandardScaler()
        values_scaled = scaler.fit_transform(values)

        clf = IsolationForest(contamination=0.05, random_state=42)
        labels = clf.fit_predict(values_scaled)

        anomalies = []
        for i, label in enumerate(labels):
            if label == -1:
                rec = emission_records[i].copy()
                rec['anomaly_reason'] = 'Valeur statistiquement atypique'
                anomalies.append(rec)
        return anomalies

    def benchmark_vessel(self, vessel_emissions: list[dict],
                          fleet_emissions: list[dict]) -> dict:
        """Compare un navire à la flotte."""
        if not vessel_emissions or not fleet_emissions:
            return {}
        vessel_avg = np.mean([e['total_co2e'] for e in vessel_emissions])
        fleet_avg  = np.mean([e['total_co2e'] for e in fleet_emissions])
        delta_pct  = ((vessel_avg - fleet_avg) / fleet_avg * 100) if fleet_avg else 0
        return {
            'vessel_avg_co2e': round(vessel_avg, 2),
            'fleet_avg_co2e':  round(fleet_avg, 2),
            'delta_pct':       round(delta_pct, 2),
            'performance':     'sous_moyenne' if delta_pct > 5 else (
                               'sur_moyenne' if delta_pct < -5 else 'dans_la_moyenne'),
        }