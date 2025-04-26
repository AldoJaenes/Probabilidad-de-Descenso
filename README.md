# Probabilidad de Descenso

Este repositorio estima las probabilidades de descenso de equipos de fútbol usando simulación Monte Carlo.

## Estructura del repositorio
```plaintext
Probabilidad-de-Descenso/
├── probabilidad_descenso.py    # Script principal comentado y didáctico
├── README.md                  # Documentación del proyecto
├── requirements.txt           # Dependencias Python
├── teams.json                 # Ejemplo de clasificación actual
├── fixtures.json              # Ejemplo de partidos restantes
├── detailed_probs.json        # Salida JSON de probabilidades detalladas (ejemplo)
├── probs.csv                  # Salida CSV de probabilidades (ejemplo)
└── relegation_probs.png       # Gráfico de ejemplo
```

## Archivos principales

### `probabilidad_descenso.py`
Módulo principal con comentarios didácticos:
- Definición de clases `Team` y `Match`.
- Carga de datos JSON.
- Simulación Monte Carlo con multiprocessing.
- Cálculo de distribuciones de posición y riesgo de descenso.
- Salida en consola, CSV/JSON y gráficos.

### `requirements.txt`
```text
numpy
tqdm
matplotlib
```
Instalar con:
```bash
pip install -r requirements.txt
```

### `teams.json`
Ejemplo de estado actual de la liga:
```json
{
  "Linense":    {"points": 41, "gf": 31, "ga": 34},
  "Sanse":      {"points": 43, "gf": 30, "ga": 44},
  "Fuenlabrada":{"points": 43, "gf": 30, "ga": 50},
  "Badajoz":    {"points": 43, "gf": 34, "ga": 49}
}
```

### `fixtures.json`
Ejemplo de partidos restantes:
```json
[
  {"home": "Linense",     "away": "Sanse",      "expected": [1.2, 1.0]},
  {"home": "Fuenlabrada", "away": "Badajoz"},
  {"home": "Sanse",       "away": "Badajoz",    "expected": [1.1, 1.05]}
]
```

## Ejecución de ejemplo
```bash
python probabilidad_descenso.py \
  --teams teams.json \
  --fixtures fixtures.json \
  --spots 3 \
  --iterations 20000 \
  --processes 4 \
  --granular \
  --output detailed_probs.json \
  --plot
```

Después de ejecutar obtendrás:
- `detailed_probs.json`: Probabilidades de descenso y distribuciones de posiciones.
- `relegation_probs.png`: Gráfico de barras.
- (Opcional) `probs.csv`: CSV con los mismos datos.

---

