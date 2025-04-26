"""
Funciones para estimar parámetros Poisson (lambda) a partir de datos históricos.
"""
import json
from typing import Dict, Tuple

def estimate_lambdas(teams_data: Dict[str, Dict[str, int]]) -> Dict[str, Tuple[float, float]]:
    """
    Dado un dict de equipos con 'gf', 'ga' totales y 'matches_played', estima
    lambda_home y lambda_away como media de goles a favor/en contra por equipo.
    teams_data: {
        team: {'gf': int, 'ga': int, 'matches_played': int}, ...
    }
    Retorna: {team: (lambda_home, lambda_away)}
    """
    lambdas = {}
    for team, data in teams_data.items():
        mf = data['matches_played']
        lambdas[team] = (
            data['gf'] / mf if mf else 1.0,
            data['ga'] / mf if mf else 1.0
        )
    return lambdas
