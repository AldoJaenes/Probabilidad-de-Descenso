# Probabilidad de Descenso

Repositorio para estimar las probabilidades de descenso de equipos de fútbol mediante simulación Monte Carlo, aplicando criterios de desempate "mini-liga" (head-to-head) para grupos empatados.

---

## Características principales

- **Modelo Monte Carlo**: simulación de goles con distribución de Poisson.  
- **Paralelización**: `multiprocessing` + `tqdm`.  
- **Desempate “mini-liga”**: head-to-head (puntos, goal diff, GF) en subgrupos empatados.  
- **Distribución de posiciones**: probabilidad de cada puesto para cada equipo.  
- **Exportación**: CSV/JSON + gráficos (`matplotlib`).  
- **Scripts**:  
  - `src/probabilidad_descenso.py`  
  - `src/enumerador_descenso.py`  
  - `src/fetch_and_simulate.py`

---

## Asunciones y validación

1. **Modelo de goles**: Se usa Poisson, basado en estudios que muestran que los goles en fútbol se ajustan a este modelo (p.ej., Dixon & Coles, 1997).  
2. **Independencia de partidos**: Asumimos resultados independientes entre encuentros.  
3. **Estimación de parámetros**: Por defecto `lambda` uniforme; para mayor precisión, se puede estimar a partir de datos históricos de cada equipo. Consulta `scripts/utilidad_estimacion.py`.  
4. **Convergencia**: Recomendamos verificar estabilidad con 5k, 10k y 20k simulaciones, comparando estimaciones y rangos de confianza.

---

## Instalación

Requiere Python 3.7+ y dependencias:

```bash
pip install numpy tqdm matplotlib requests python-dateutil pytest flake8
```

O bien:

```bash
pip install -r requirements.txt
```

---

## Estructura del proyecto

```plaintext
Probabilidad-de-Descenso/
├── src/
│   ├── probabilidad_descenso.py    # Simulación Monte Carlo con mini-liga
│   ├── enumerador_descenso.py      # Enumerador exacto de escenarios
│   └── fetch_and_simulate.py       # Obtiene datos de API y ejecuta simulación
├── data/
│   ├── teams.json                  # Clasificación actual (input)
│   └── fixtures.json               # Partidos pendientes (input)
├── outputs/
│   ├── detailed_probs.json         # Distribuciones detalladas (output)
│   ├── probs.csv                   # CSV de probabilidades (output)
│   └── relegation_probs.png        # Gráfico de barras (output)
├── notebooks/
│   ├── CalculadorEscenariosdeDescenso.ipynb  # Históricos originales
│   ├── Prob_Des_Total_1RFEF.ipynb            # Históricos originales
│   └── SFCD_Prob.ipynb                       # Históricos originales
├── scripts/
│   └── utilidad_estimacion.py       # Funciones de estimación de parámetros Poisson
├── tests/
│   └── test_tiebreak.py            # Pruebas unitarias de desempate mini-liga
├── .github/
│   └── workflows/ci.yml            # Pipeline CI: lint y tests
├── requirements.txt                # Dependencias
└── README.md                       # Documentación
```

---

## Formato de datos

### `data/teams.json`

```json
{
  "EquipoA": {"points": 41, "gf": 31, "ga": 34},
  "EquipoB": {"points": 43, "gf": 30, "ga": 44}
}
```

- `points`: puntos actuales.  
- `gf`: goles a favor.  
- `ga`: goles en contra.  

### `data/fixtures.json`

```json
[
  {"home": "EquipoA", "away": "EquipoB", "expected": [1.2, 1.0]},
  {"home": "EquipoC", "away": "EquipoD"}
]
```

- `expected` (opcional): `[lambda_home, lambda_away]`.  

---

## Uso principal

```bash
python src/probabilidad_descenso.py \
  --teams data/teams.json \
  --fixtures data/fixtures.json \
  --spots 3 \
  --iterations 20000 \
  --processes 4 \
  [--granular] \
  [--output outputs/detailed_probs.json] \
  [--plot]
```

- `--spots`: plazas de descenso.  
- `--iterations`: simulaciones Monte Carlo.  
- `--granular`: muestra distribución por puesto.  
- `--output`: ruta CSV o JSON.  
- `--plot`: genera `outputs/relegation_probs.png`.  

---

## Desempate “mini-liga”

Para **subgrupos empatados** (2+ equipos):  
1. Puntos en enfrentamientos directos.  
2. Diferencia de goles en enfrentamientos directos.  
3. Goles a favor en enfrentamientos directos.  
4. Si persiste empate: diferencia de goles global y luego goles a favor global.  

---

## Ejemplo de resultados

- **detailed_probs.json**:
  ```json
  {
    "EquipoA": {"relegation": 0.75, "positions": [0.10, 0.15, ..., 0.75]},
    ...
  }
  ```
- **probs.csv**:
  ```csv
  Team,Relegation,P1,P2,...
  EquipoA,0.7500,0.1000,0.1500,...,0.7500
  ...
  ```
- **relegation_probs.png**: gráfica de barras de probabilidades.  

---

## Consumir datos de la API y simular

Para competiciones soportadas por Football-Data.org:

```bash
export FOOTBALL_DATA_API_TOKEN=TU_TOKEN
python src/fetch_and_simulate.py \
  --competition 2014 \
  --season 2024/2025 \
  --matchday last \
  --spots 3 \
  --iterations 20000 \
  --processes 4 \
  --granular \
  --output outputs/api_probs.json \
  --plot
```

---

## CI/CD y calidad de código

- **Tests**: `pytest tests/` ejecuta pruebas unitarias.  
- **Lint**: `flake8 src/` para estilo.  
- **Integración Continua**: `.github/workflows/ci.yml` corre lint y tests en cada push.  

---
