"""
Funciones para estimar parámetros Poisson (lambda) a partir de datos históricos.
"""

import json
from typing import Dict, Tuple

def estimate_lambdas(teams_data: Dict[str, Dict[str, int]]) -> Dict[str, Tuple[float, float]]:
    """
    Calcula lambdas de goles a favor y en contra por partido para cada equipo.
    teams_data: {
        team: {'gf': total_goals_for, 'ga': total_goals_against, 'matches_played': int}
    }
    """
    lambdas = {}
    for team, data in teams_data.items():
        gf = data.get('gf', 0)
        ga = data.get('ga', 0)
        mp = data.get('matches_played', 1)
        home_lambda = gf / mp
        away_lambda = ga / mp
        lambdas[team] = (home_lambda, away_lambda)
    return lambdas

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Estima lambdas de goles Poisson")
    parser.add_argument('--input', required=True, help='JSON con datos históricos')
    parser.add_argument('--output', required=True, help='JSON donde guardar lambdas')
    args = parser.parse_args()
    with open(args.input) as f:
        data = json.load(f)
    lambdas = estimate_lambdas(data)
    with open(args.output, 'w') as f:
        json.dump(lambdas, f, indent=2, ensure_ascii=False)
    print(f"Lambdas guardadas en {args.output}")
