#!/usr/bin/env python3
"""
Benchmark de convergencia para Monte Carlo.
"""
import json
import argparse
from src.probabilidad_descenso import load_teams, load_fixtures, calculate_distributions
import csv
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Benchmark convergence MC")
    parser.add_argument('--teams', required=True)
    parser.add_argument('--fixtures', required=True)
    parser.add_argument('--iterations', nargs='+', type=int, default=[1000,5000,10000,20000])
    parser.add_argument('--spots', type=int, default=3)
    parser.add_argument('--processes', type=int, default=1)
    parser.add_argument('--output', default='convergence.csv')
    args = parser.parse_args()

    teams = load_teams(args.teams)
    fixtures = load_fixtures(args.fixtures)

    results = {}
    for it in args.iterations:
        releg_probs, _ = calculate_distributions(teams, fixtures, args.spots, it, args.processes)
        for team, p in releg_probs.items():
            results.setdefault(team, []).append((it, p))
    # Save CSV
    teams_list = list(results.keys())
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['iterations'] + teams_list
        writer.writerow(header)
        for idx,it in enumerate(args.iterations):
            row = [it] + [results[t][idx] for t in teams_list]
            writer.writerow(row)
    print(f"Convergence data saved to {args.output}")
    # Plot each team
    for team, data in results.items():
        plt.plot(args.iterations, [p for _,p in data], label=team)
    plt.xlabel('Iterations')
    plt.ylabel('Relegation Probability')
    plt.legend()
    plt.tight_layout()
    plt.savefig('convergence.png')
    print("Convergence plot saved to convergence.png")

if __name__ == "__main__":
    main()
