import pytest
from src.probabilidad_descenso import load_teams, load_fixtures, calculate_distributions

def test_distribution_sum(tmp_path):
    # Crear datos de prueba
    teams = {"A": {"points":0,"gf":0,"ga":0}}
    fixtures = []
    json_file = tmp_path / "teams.json"
    json_file.write_text(json.dumps(teams))
    # fixtures empty
    # Cargar y calcular
    t = load_teams(str(json_file))
    probs, pos = calculate_distributions(t, fixtures, spots=1, iterations=100, processes=1)
    # Para un solo equipo, prob=1 y pos=[1.0]
    assert pytest.approx(probs["A"], rel=1e-3) == 1.0
    assert pytest.approx(sum(pos["A"]), rel=1e-3) == 1.0
