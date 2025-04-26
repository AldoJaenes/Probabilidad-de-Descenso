#!/usr/bin/env python3
"""
Módulo avanzado para estimar probabilidades de descenso vía simulación Monte Carlo con distribuciones detalladas.

Características:
  - Procesa la clasificación actual y los próximos partidos desde JSON.
  - Simulación Monte Carlo configurable: iteraciones y procesos paralelos.
  - Modelo Poisson para goles o probabilidades personalizadas.
  - Cálculo de distribución de posiciones para cada equipo (1.º,2.º,...).
  - Salida de resumen: riesgo de descenso y probabilidad por puesto.
  - Exportación opcional a CSV/JSON y generación de gráficos con matplotlib.

Uso:
  pip install -r requirements.txt
  python probabilidad_descenso.py \
      --teams teams.json --fixtures fixtures.json \
      --spots 3 --iterations 20000 --processes 4 \
      [--granular] [--output probs.csv] [--plot]
"""
import json                # para Leer/Escribir JSON
import argparse            # ingesta de argumentos de línea de comandos
import random              # para generación de números aleatorios
import multiprocessing as mp  # ejecución en paralelo
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from tqdm import tqdm      # barra de progreso
import numpy as np         # para modelo Poisson
import csv                 # manejo de CSV
import os                  # operaciones de sistema de archivos

@dataclass
class Team:
    """
    Representa un equipo con estado actual en la liga.
    Attributes:
        name: Nombre del equipo.
        points: Puntos actuales.
        gf: Goles a favor.
        ga: Goles en contra.
    """
    name: str
    points: int = 0
    gf: int = 0
    ga: int = 0

    def goal_diff(self) -> int:
        """Devuelve la diferencia de goles (gf - ga)."""
        return self.gf - self.ga

    def clone(self) -> 'Team':
        """Crea y devuelve una copia independiente del equipo."""
        return Team(self.name, self.points, self.gf, self.ga)

@dataclass
class Match:
    """
    Representa un partido con modelo Poisson de goles.
    Attributes:
        home: Equipo local.
        away: Equipo visitante.
        expected: Tupla (lambda_local, lambda_visitante) para Poisson.
    """
    home: str
    away: str
    expected: Tuple[float, float] = field(default_factory=lambda: (1.2, 1.0))

    def simulate(self, teams: Dict[str, Team]) -> None:
        """
        Simula el resultado del partido:
          - Genera goles según Poisson.
          - Actualiza gf, ga y puntos de los equipos.
        """
        gh = np.random.poisson(self.expected[0])
        ga = np.random.poisson(self.expected[1])
        teams[self.home].gf += gh
        teams[self.home].ga += ga
        teams[self.away].gf += ga
        teams[self.away].ga += gh
        if gh > ga:
            teams[self.home].points += 3
        elif gh < ga:
            teams[self.away].points += 3
        else:
            teams[self.home].points += 1
            teams[self.away].points += 1

def load_teams(path: str) -> Dict[str, Team]:
    """
    Carga el estado de los equipos desde un archivo JSON.
    JSON esperado: {"Equipo": {"points": int, "gf": int, "ga": int}, ...}
    """
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    return {name: Team(name, **data) for name, data in raw.items()}

def load_fixtures(path: str) -> List[Match]:
    """
    Carga los partidos restantes desde un JSON.
    JSON esperado:
    [
      {"home": str, "away": str, "expected": [float, float]},
      ...
    ]
    """
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    fixtures: List[Match] = []
    for m in raw:
        exp = tuple(m.get("expected", [1.2, 1.0]))
        fixtures.append(Match(home=m["home"], away=m["away"], expected=exp))
    return fixtures

def simulate_once(args: Tuple[Dict[str, Team], List[Match]]) -> List[str]:
    """
    Simula una temporada completa:
      - Clona estado inicial de equipos.
      - Ejecuta simulate() para cada partido.
      - Ordena equipos por (puntos, goal_diff, gf) descendente.
      - Devuelve lista de nombres ordenados de mejor a peor.
    """
    teams, fixtures = args
    scenario = {n: t.clone() for n, t in teams.items()}
    for match in fixtures:
        match.simulate(scenario)
    sorted_names = [t.name for t in sorted(
        scenario.values(),
        key=lambda t: (t.points, t.goal_diff(), t.gf),
        reverse=True
    )]
    return sorted_names

def calculate_distributions(
    teams: Dict[str, Team], fixtures: List[Match],
    spots: int, iterations: int, processes: int
) -> Tuple[Dict[str, float], Dict[str, List[float]]]:
    """
    Ejecuta simulaciones Monte Carlo y calcula:
      - Probabilidad de descenso por equipo.
      - Distribución de posiciones (vector de probabilidades) por equipo.
    """
    pool = mp.Pool(processes)
    tasks = [(teams, fixtures)] * iterations

    team_list = list(teams.keys())
    pos_counts = {t: [0] * len(team_list) for t in team_list}

    for result in tqdm(
        pool.imap_unordered(simulate_once, tasks),
        total=iterations, desc="Simulating"
    ):
        for pos, name in enumerate(result):
            pos_counts[name][pos] += 1

    pool.close()
    pool.join()

    pos_probs = {t: [count / iterations for count in counts] for t, counts in pos_counts.items()}
    releg_probs = {t: sum(pos_probs[t][spots:]) for t in team_list}
    return releg_probs, pos_probs

def save_output(
    releg_probs: Dict[str, float], pos_probs: Dict[str, List[float]], path: str
) -> None:
    """
    Guarda resultados en CSV o JSON.
    CSV: Team,Relegation,P1,P2,...
    JSON: {team:{"relegation":p, "positions":[...]}}
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            header = ["Team", "Relegation"] + [f"P{p+1}" for p in range(len(next(iter(pos_probs.values()))))]
            writer.writerow(header)
            for t in releg_probs:
                row = [t, f"{releg_probs[t]:.4f}"] + [f"{p:.4f}" for p in pos_probs[t]]
                writer.writerow(row)
    elif ext == ".json":
        out = {t: {"relegation": releg_probs[t], "positions": pos_probs[t]} for t in releg_probs}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    else:
        raise ValueError(f"Unsupported format: {ext}")

def parse_args() -> argparse.Namespace:
    """
    Define y analiza argumentos de línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description="Estimate relegation probabilities with detailed distributions"
    )
    parser.add_argument("--teams", required=True, help="JSON con standings")
    parser.add_argument("--fixtures", required=True, help="JSON con fixtures")
    parser.add_argument("--spots", type=int, default=3, help="Nº de descensos")
    parser.add_argument("--iterations", type=int, default=10000, help="Simulaciones")
    parser.add_argument("--processes", type=int, default=mp.cpu_count(), help="Procesos paralelos")
    parser.add_argument("--granular", action="store_true", help="Mostrar distribuciones completas")
    parser.add_argument("--output", help="Guardar resultados en CSV/JSON")
    parser.add_argument("--plot", action="store_true", help="Generar gráficos")
    return parser.parse_args()

def main():
    """
    Función principal: carga datos, ejecuta simulaciones y muestra/guarda resultados.
    """
    args = parse_args()
    teams = load_teams(args.teams)
    fixtures = load_fixtures(args.fixtures)

    releg_probs, pos_probs = calculate_distributions(
        teams, fixtures, args.spots, args.iterations, args.processes
    )

    print("Relegation Probabilities:")
    for t, p in sorted(releg_probs.items(), key=lambda x: x[1], reverse=True):
        print(f"{t}: {p:.2%}")

    if args.granular:
        print("\nPosition Distributions:")
        num_pos = len(next(iter(pos_probs.values())))
        header = ["Team"] + [str(i+1) for i in range(num_pos)]
        print(" | ".join(header))
        for t in sorted(pos_probs, key=lambda x: releg_probs[x], reverse=True):
            probs = [f"{x:.1%}" for x in pos_probs[t]]
            print(f"{t} | {' | '.join(probs)}")

    if args.output:
        save_output(releg_probs, pos_probs, args.output)
        print(f"Saved to {args.output}")

    if args.plot:
        try:
            import matplotlib.pyplot as plt
            teams_list = list(releg_probs.keys())
            vals = [releg_probs[t] for t in teams_list]
            plt.figure()
            plt.bar(teams_list, vals)
            plt.title("Relegation Probabilities")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("relegation_probs.png")
            print("Saved relegation_probs.png")
        except ImportError:
            print("matplotlib not found; skipping plots")

if __name__ == "__main__":
    main()
