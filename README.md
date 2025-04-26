# Probabilidad de Descenso

Repositorio para estimar las probabilidades de descenso de equipos de fútbol mediante simulación Monte Carlo, incluyendo criterios de desempate “mini-liga” (head-to-head) para grupos de 2 o más equipos.

---

## Características principales

- **Modelo Monte Carlo** con simulación de goles vía distribución de Poisson.
- **Paralelización** con `multiprocessing` y barra de progreso `tqdm`.
- **Desempate “mini-liga”**: aplica puntos, golaveraje y goles a favor de los enfrentamientos directos en grupos empatados.
- **Distribución de posiciones**: calcula probabilidad de cada equipo de acabar en cada puesto.
- **Exportación** a CSV/JSON y generación opcional de gráfico de barras con `matplotlib`.

---

## Instalación

Requiere Python 3.7+ y las siguientes dependencias:

```bash
pip install numpy tqdm matplotlib
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
│   └── probabilidad_descenso.py    # Script principal con lógica y comentarios
├── data/
│   ├── teams.json                 # Estado actual de la liga
│   └── fixtures.json              # Partidos restantes y parámetros Poisson
├── outputs/
│   ├── detailed_probs.json        # Ejemplo de salida JSON con distribuciones
│   ├── probs.csv                  # Ejemplo de salida CSV
│   └── relegation_probs.png       # Gráfico de ejemplo (--plot)
├── notebooks/
│   ├── CalculadorEscenariosdeDescenso.ipynb  # Código original histórico
│   ├── Prob_Des_Total_1RFEF.ipynb            # Código original histórico
│   └── SFCD_Prob.ipynb                       # Código original histórico
├── requirements.txt           # Lista de dependencias
└── README.md                  # Este archivo
```

---

## Formato de datos

### `data/teams.json`

JSON que define cada equipo y su estado actual:

```json
{
  "EquipoA": {"points": 41, "gf": 31, "ga": 34},
  "EquipoB": {"points": 43, "gf": 30, "ga": 44},
  ...
}
```

- `points`: puntos acumulados.
- `gf`: goles a favor.
- `ga`: goles en contra.

### `data/fixtures.json`

Lista de encuentros restantes y sus parámetros de Poisson (opcional):

```json
[
  {"home": "EquipoA", "away": "EquipoB", "expected": [1.2, 1.0]},
  {"home": "EquipoC", "away": "EquipoD"}
]
```

- `expected`: `[lambda_home, lambda_away]` para generar goles (por defecto `[1.2,1.0]`).

---

## Uso

Ejecuta el script principal desde la carpeta raíz:

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

- `--spots`: número de puestos de descenso (por defecto `3`).
- `--iterations`: número de simulaciones Monte Carlo (por defecto `10000`).
- `--processes`: trabajadores paralelos (por defecto número de CPUs).
- `--granular`: muestra en consola distribución completa por puesto.
- `--output`: archivo de salida (CSV o JSON). Si no se especifica, solo imprime en pantalla.
- `--plot`: genera `outputs/relegation_probs.png` con la gráfica de riesgo de descenso.

---

## Criterio de desempate “mini-liga”

Para cualquier grupo de **2 o más** equipos empatados a puntos:

1. Se extraen los enfrentamientos directos entre ellos.
2. Se recalculan:
   - **Puntos** dentro de ese subgrupo.
   - **Diferencia de goles** (gf-ga) entre ellos.
   - **Goles a favor** entre ellos.
3. Si persiste empate, se usa **diferencia de goles global** y luego **goles a favor global**.

Este procedimiento garantiza un orden fiel a la normativa de competiciones.

---

## Ejemplo de resultados

- **detailed_probs.json**:
  ```json
  {
    "EquipoA": {"relegation": 0.75, "positions": [0.10,0.15,...,0.75]},
    ...
  }
  ```

- **probs.csv**:
  ```csv
  Team,Relegation,P1,P2,...
  EquipoA,0.7500,0.1000,0.1500,...,0.7500
  ...
  ```

- **relegation_probs.png**: gráfica de barras de probabilidades de descenso.

---
