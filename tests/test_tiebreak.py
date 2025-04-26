import pytest
from src.probabilidad_descenso import tie_break, Team, Match, resolve_final_ranking

def test_tie_break_triple():
    # Configurar un mini-grupo de 3 equipos con head-to-head
    teams = ['A','B','C']
    # Crear estados básicos
    states = {t: Team(t, points=0, gf=0, ga=0) for t in teams}
    # Definir head-to-head manual
    hh = {
        'A': {'B':{'points':3,'gf':2,'ga':1}, 'C':{'points':1,'gf':1,'ga':1}},
        'B': {'A':{'points':1,'gf':1,'ga':2}, 'C':{'points':3,'gf':2,'ga':0}},
        'C': {'A':{'points':1,'gf':1,'ga':1}, 'B':{'points':0,'gf':0,'ga':2}}
    }
    # Inject hh into Team objects
    for t in teams:
        states[t].hh = hh[t]
    order = tie_break(teams, states, hh)
    # B debe quedar primero, luego A, luego C
    assert order == ['B','A','C']

def test_resolve_final_ranking_no_tie():
    # Sin empates, orden por puntos global
    states = {
        'X': Team('X', points=5, gf=5, ga=3),
        'Y': Team('Y', points=3, gf=4, ga=4),
        'Z': Team('Z', points=1, gf=2, ga=5)
    }
    ranking = resolve_final_ranking(states, {})
    assert ranking == ['X','Y','Z']
