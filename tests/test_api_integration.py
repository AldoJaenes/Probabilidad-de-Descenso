import pytest
from unittest.mock import patch
from src.fetch_and_simulate import fetch_standings, fetch_fixtures

class DummyResponse:
    def __init__(self, data):
        self._data = data
    def json(self):
        return self._data
    def raise_for_status(self):
        pass

@patch('src.fetch_and_simulate.requests.get')
def test_fetch_standings(mock_get):
    data = {'standings':[{'table':[{'team':{'name':'X'},'points':5,'goalsFor':10,'goalsAgainst':8}]}]}
    mock_get.return_value = DummyResponse(data)
    res = fetch_standings('X','2024/2025')
    assert res['X']['points'] == 5

@patch('src.fetch_and_simulate.requests.get')
def test_fetch_fixtures(mock_get):
    # First call returns matchday, second returns matches
    def side_effect(url, headers):
        if 'matches?' not in url:
            return DummyResponse({'currentSeason':{'currentMatchday':1}})
        return DummyResponse({'matches':[{'status':'SCHEDULED','homeTeam':{'name':'A'},'awayTeam':{'name':'B'}},
                                         {'status':'TIMED','homeTeam':{'name':'C'},'awayTeam':{'name':'D'}}]})
    mock_get.side_effect = side_effect
    fixtures = fetch_fixtures('X','2024/2025','last')
    # Should include both matches since status SCHEDULED and TIMED accepted
    assert any(f['home']=='A' for f in fixtures)
