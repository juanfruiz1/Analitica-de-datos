# Proyecto de Analítica de Datos — Despliegue de Modelos

Aplicación web interactiva construida con **Streamlit** que despliega dos modelos de Machine Learning previamente entrenados:

- **Modelo de Regresión** → predice el **valor de mercado (€)** de un jugador de fútbol a partir de sus variables deportivas y demográficas.
- **Modelo de Clasificación** → predice el **nivel de dificultad cognitiva** (Principiante / Intermedio / Avanzado / Maestro) de un puzzle de ajedrez de Lichess a partir de la disposición del tablero y metadatos.

Además, la aplicación incluye un dashboard de Análisis Exploratorio de Datos (EDA) para ambos dominios.

---

## Descripción del proyecto

El proyecto cubre el ciclo completo de analítica de datos sobre dos datasets:

1. **Fútbol** (valor de mercado de jugadores): regresión con un `RandomForestRegressor` dentro de un `Pipeline` de scikit-learn que incluye preprocesamiento (imputación KNN, escalado y one-hot encoding de variables categóricas).
2. **Ajedrez** (puzzles tácticos de Lichess): clasificación multiclase (4 clases) con un `XGBClassifier` dentro de un `Pipeline` que numéricamente escala las features del tablero y aplica TF-IDF sobre el campo textual `Themes`.

Las **features del tablero** (factor de ramificación, índice de forzamiento, densidad del grafo de interacciones, componentes de tensión, entropía espacial y distancia de Chebyshev entre centros de masa) se calculan en tiempo real desde un FEN + primer movimiento mediante la clase `ChessFeatureExtractor` (ver `src/boarddataextraction.py`).

La interfaz de predicción de ajedrez incluye un **tablero interactivo drag-and-drop** (componente Streamlit personalizado basado en `chessboard.js`) que permite montar la posición pieza a pieza y realizar el primer movimiento del puzzle.

---

## Cómo instalar dependencias

Requisitos: **Python 3.10+**.

1. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## Cómo ejecutar la aplicación

Desde la raíz del proyecto:

```bash
streamlit run src/app.py
```

La aplicación se abre en el navegador (`http://localhost:8501`). Usa el **menú lateral** para alternar entre:

- **Fútbol (Regresión)** → pestaña **Predicción** para ingresar las variables del jugador y obtener el valor de mercado estimado.
- **Ajedrez (Clasificación)** → pestaña **Predicción** para montar la posición en el tablero interactivo, realizar el primer movimiento y obtener el nivel de dificultad predicho con sus probabilidades.

---

## Descripción de los modelos utilizados

### Modelo de Regresión — `models/model_regression.joblib`

- **Tipo:** `Pipeline(ColumnTransformer → RandomForestRegressor)` (scikit-learn).
- **Entrada:** 18 variables (14 numéricas + 4 categóricas: `pie_habil`, `posicion_principal`, `nacionalidad`, `liga_actual`).
- **Salida:** valor de mercado en euros (variable continua).
- **Features de entrada:** `edad_al_momento`, `mes_de_nacimiento`, `altura_cm`, `pie_habil`, `posicion_principal`, `nacionalidad`, `minutos_jugados_12m`, `partidos_jugados_12m`, `goles_12m`, `asistencias_12m`, `tarjetas_amarillas_12m`, `tarjetas_rojas_12m`, `participacion_goles_p90`, `partidos_seleccion_12m`, `convocatorias_historicas_seleccion`, `dias_para_fin_contrato`, `valor_maximo_historico_previo`, `liga_actual`.
- **Artefacto auxiliar:** `models/features_regression.joblib` (lista de 241 features post-encoding, usada para poblar las opciones de los selectbox).

### Modelo de Clasificación — `models/model_classification.joblib`

- **Tipo:** `Pipeline(ColumnTransformer[numéricas + TF-IDF sobre Themes] → XGBClassifier)`.
- **Entrada:** 10 variables (`RatingDeviation`, `Popularity`, `NbPlays`, `Themes` (texto), `branching_factor`, `forcing_index`, `graph_density`, `tension_components`, `spatial_entropy`, `com_chebyshev_dist`).
- **Salida:** clase ∈ {0, 1, 2, 3} mapeada a niveles de dificultad:
  - `0` → Principiante
  - `1` → Intermedio
  - `2` → Avanzado
  - `3` → Maestro
- **Features del tablero:** calculadas en tiempo real por `ChessFeatureExtractor` a partir del FEN y el primer movimiento del puzzle.
- **Artefacto auxiliar:** `models/features_classification.joblib` (lista de 83 features post-encoding).

---

## Estructura del proyecto

```
ml-project_analitica_datos/
├── src/
│   ├── app.py                         # Aplicación Streamlit (dashboard + despliegue de modelos)
│   ├── boarddataextraction.py         # ChessFeatureExtractor (features del tablero desde FEN)
│   ├── render_position.py             # Renderizado de posiciones a PNG (PIL)
│   └── chessboard_component/          # Componente Streamlit de tablero interactivo (chessboard.js)
│       ├── index.html                 # Editor drag-and-drop de 2 fases (setup + primer movimiento)
│       ├── streamlit-component-lib.js # Lib de comunicación Streamlit (vendorizada)
│       ├── chessboard-1.0.0.min.js    # chessboard.js (vendorizada)
│       ├── chessboard-1.0.0.min.css
│       ├── chess.min.js               # chess.js (validación de movimientos)
│       ├── jquery-3.7.1.min.js
│       └── pieces/                    # 12 PNGs de piezas (estilo neo)
├── models/
│   ├── model_regression.joblib        # Pipeline de regresión completo
│   ├── model_classification.joblib    # Pipeline de clasificación completo
│   ├── features_regression.joblib
│   └── features_classification.joblib
├── database/
│   └── proyecto_analitica.db          # SQLite con los datasets (fútbol + ajedrez)
├── assets/                            # Recursos gráficos (tableros y piezas)
├── requirements.txt
└── README.md
```

---

## Notas

- Los modelos se cargan una sola vez con `joblib.load` y se cachean con `@st.cache_resource`.
- El componente de tablero interactivo funciona offline (todas las librerías JS están vendorizadas en `src/chessboard_component/`).
- La aplicación debe ejecutarse desde la raíz del proyecto para que las rutas relativas a `models/` y `database/` se resuelvan correctamente.
