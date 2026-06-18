import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import subprocess
import tempfile
import chess
import joblib
import numpy as np
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import plotly.graph_objects as go
from boarddataextraction import ChessFeatureExtractor

# --- DECLARACIÓN DEL COMPONENTE DE TABLERO INTERACTIVO ---
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
chessboard_component = components.declare_component(
    "chessboard", path=os.path.join(_SRC_DIR, "chessboard_component")
)

#================================================================================#
# 1. CONFIGURACIÓN DE PÁGINA
#================================================================================#
st.set_page_config(page_title="Despliegue de Modelos", page_icon="🤖", layout="wide")

#================================================================================#
# 2. INYECCIÓN DEL FONDO VANTA.JS (HACK NATIVO)
#================================================================================#
vanta_html = """
<script>
    if (!window.parent.document.getElementById('three-js-script')) {
        var threeScript = window.parent.document.createElement('script');
        threeScript.id = 'three-js-script';
        threeScript.src = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js";
        window.parent.document.head.appendChild(threeScript);
        threeScript.onload = function() {
            var vantaScript = window.parent.document.createElement('script');
            vantaScript.id = 'vanta-js-script';
            vantaScript.src = "https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js";
            window.parent.document.head.appendChild(vantaScript);
            vantaScript.onload = function() {
                window.parent.VANTA.NET({
                    el: window.parent.document.querySelector('.stApp'),
                    mouseControls: true, touchControls: true, gyroControls: false,
                    minHeight: 200.00, minWidth: 200.00, scale: 1.00, scaleMobile: 1.00,
                    color: 0x3fbbff, backgroundColor: 0x110c1f
                });
            };
        };
    }
</script>
"""
components.html(vanta_html, width=0, height=0)

#================================================================================#
# 3. DISEÑO CSS (GLASSMORPHISM Y ACENTOS NEÓN)
#================================================================================#
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: transparent !important;
}
[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid rgba(0, 229, 255, 0.2) !important;
    min-width: 280px !important;
}
[data-testid="stExpander"], .stDataFrame, div[data-testid="stMetric"], .stTabs, div.css-1r6slb0, div.css-12oz5g7 {
    background-color: rgba(15, 20, 30, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 15px !important;
    border: 1px solid rgba(0, 229, 255, 0.3) !important;
}
.stTabs { padding: 15px !important; }
div[data-baseweb="tab-highlight"] { background-color: #00e5ff !important; }
h1, h2, h3, label, .st-emotion-cache-16idsys p { color: #4cc9f0 !important; }
p { color: #e0e0e0; }
</style>
""", unsafe_allow_html=True)

#================================================================================#
# 4. CARGA DE DATOS (SQLITE) Y MODELOS (.joblib)
#================================================================================#
@st.cache_resource
def init_connection():
    ruta_db = os.path.join(_BASE_DIR, 'database', 'proyecto_analitica.db')
    return sqlite3.connect(ruta_db, check_same_thread=False)

conn = init_connection()

@st.cache_data(ttl=600)
def load_jugador_by_id(player_id):
    df = pd.read_sql_query(
        "SELECT * FROM jugadores WHERE player_id = ? LIMIT 1", conn, params=(int(player_id),)
    )
    return df

@st.cache_data(ttl=600)
def load_jugadores_filtrados(nacionalidad, liga, posicion, limite=100):
    q = ("SELECT player_id, edad_al_momento, nacionalidad, liga_actual, posicion_principal, "
         "valor_mercado_eur_TARGET FROM jugadores WHERE 1=1")
    params = []
    if nacionalidad != "Todas":
        q += " AND nacionalidad = ?"; params.append(nacionalidad)
    if liga != "Todas":
        q += " AND liga_actual = ?"; params.append(liga)
    if posicion != "Todas":
        q += " AND posicion_principal = ?"; params.append(posicion)
    q += " ORDER BY valor_mercado_eur_TARGET DESC LIMIT ?"; params.append(int(limite))
    return pd.read_sql_query(q, conn, params=params)

@st.cache_data(ttl=600)
def load_puzzle_by_id(puzzle_id):
    df = pd.read_sql_query(
        "SELECT * FROM muestra_procesada WHERE PuzzleId = ? LIMIT 1", conn, params=(str(puzzle_id),)
    )
    return df

@st.cache_data(ttl=30)
def load_puzzle_aleatorio(rating_min, rating_max):
    q = ("SELECT * FROM muestra_procesada WHERE Rating BETWEEN ? AND ? "
         "ORDER BY RANDOM() LIMIT 1")
    return pd.read_sql_query(q, conn, params=(int(rating_min), int(rating_max)))

@st.cache_resource
def load_models():
    ruta_models = os.path.join(_BASE_DIR, 'models')
    model_reg = joblib.load(os.path.join(ruta_models, 'model_regression.joblib'))
    model_clf = joblib.load(os.path.join(ruta_models, 'model_classification.joblib'))
    features_reg = joblib.load(os.path.join(ruta_models, 'features_regression.joblib'))
    features_clf = joblib.load(os.path.join(ruta_models, 'features_classification.joblib'))
    return model_reg, model_clf, features_reg, features_clf

model_regression, model_classification, features_regression, features_classification = load_models()

# Mapeo de las 4 clases del XGBoost a niveles de dificultad (bins Rating 1200/1800/2400)
CLASES_DIFICULTAD = {0: 'Principiante', 1: 'Intermedio', 2: 'Avanzado', 3: 'Maestro'}
COLORES_CLASES = ['#00e5ff', '#4cc9f0', '#f72585', '#7209b7']

def clase_real_desde_rating(rating):
    """Devuelve la clase real (0-3) basada en los bins de Rating."""
    if rating < 1200: return 0
    if rating < 1800: return 1
    if rating < 2400: return 2
    return 3


#================================================================================#
# 5. HELPERS DE UI
#================================================================================#
def tarjeta_titulo(icono, titulo, subtitulo):
    st.markdown(f"""
    <div style="background-color: rgba(15, 20, 30, 0.7); backdrop-filter: blur(12px);
                border-radius: 15px; border: 1px solid rgba(0, 229, 255, 0.3);
                padding: 25px; margin-bottom: 20px;">
        <h1 style="color:#FFFFFF; margin:0; font-size:2.2rem; text-shadow: 2px 2px 8px #000000;">
            <i class="bi bi-{icono}" style="color:#00e5ff; margin-right:10px;"></i>{titulo}
        </h1>
        <p style="color:#cbd5e1; margin:8px 0 0 0; font-size:1rem;">{subtitulo}</p>
    </div>
    """, unsafe_allow_html=True)


def tarjeta_resultado(icono, etiqueta, valor, color_borde, color_valor, sombra):
    return f"""
    <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px);
                border: 2px solid {color_borde}; border-radius: 12px; padding: 25px;
                text-align: center; box-shadow: 0 0 25px {sombra}; height: 100%;">
        <p style="color:#8b949e; margin:0; font-size:0.85rem;">{icono} {etiqueta}</p>
        <h2 style="color:{color_valor}; margin:10px 0 0 0; font-size:1.6rem;">{valor}</h2>
    </div>
    """


def barras_probabilidad(probas, clases_modelo):
    nombres = [CLASES_DIFICULTAD.get(int(c), f"Clase {c}") for c in clases_modelo]
    fig = go.Figure(data=[go.Bar(
        x=nombres, y=[float(p) for p in probas],
        marker_color=COLORES_CLASES[:len(nombres)],
        text=[f"{float(p)*100:.1f}%" for p in probas], textposition='outside',
    )])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0'),
        yaxis=dict(title='Probabilidad', range=[0, 1], tickformat='.0%',
                   gridcolor='rgba(255,255,255,0.1)'),
        xaxis=dict(title=None), margin=dict(t=10, b=10), height=320,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


@st.cache_resource
def get_temp_dir():
    """Directorio temporal persistente para renderizar PNGs de tableros."""
    return tempfile.mkdtemp(prefix="appmodelo_chess_")

_temp_dir = get_temp_dir()

def render_board_image(fen, nombre="board", estilo_tablero="brown", estilo_piezas="neo"):
    """Renderiza una posición FEN a PNG usando src/render_position.py y devuelve la ruta.
    La orientación se decide según el turno del FEN (si juegan negras, se voltea)."""
    try:
        b = chess.Board(fen)
        flip = (b.turn == chess.BLACK)
    except Exception:
        flip = False
    output_path = os.path.join(_temp_dir, f"{nombre}.png")
    lado = "black" if flip else "white"
    command = [
        sys.executable, os.path.join(_SRC_DIR, "render_position.py"),
        "--fen", fen, "--board", estilo_tablero, "--pieces", estilo_piezas,
        "--size", "45", "--side", lado, "--output", output_path
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, check=True,
                       cwd=_BASE_DIR)  # render_position usa rutas relativas a assets/
        return output_path
    except subprocess.CalledProcessError:
        return None

def mostrar_tablero_centrado(img_path, caption=None):
    """Muestra una imagen PNG centrada horizontalmente vía HTML/base64 (ancho fijo 360px)."""
    import base64
    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    caption_html = f"<p style='text-align:center; color:#8b949e; font-size:0.8rem; margin-top:6px;'>{caption}</p>" if caption else ""
    st.markdown(
        f"<div style='display:flex; flex-direction:column; align-items:center; margin:10px 0;'>"
        f"<img src='data:image/png;base64,{encoded}' width='360' style='border-radius:8px; border:2px solid rgba(0,229,255,0.3);' />"
        f"{caption_html}</div>",
        unsafe_allow_html=True
    )


#================================================================================#
# 6. SIDEBAR (SELECCIÓN DE MODELO)
#================================================================================#
with st.sidebar:
    st.markdown("<h2 style='color:white !important; text-align:center; font-weight:700;'>Menú Principal</h2>", unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=["Fútbol (Regresión)", "Ajedrez (Clasificación)"],
        icons=["trophy", "puzzle"], menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00e5ff", "font-size": "18px"},
            "nav-link": {"color": "white", "font-size": "16px", "text-align": "left",
                         "margin": "0px", "--hover-color": "rgba(0, 229, 255, 0.2)"},
            "nav-link-selected": {"background-color": "rgba(0, 229, 255, 0.3)",
                                  "border-left": "4px solid #00e5ff"},
        }
    )
    st.markdown("<br><hr style='border:1px solid rgba(0,229,255,0.2);'><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px);
                border-radius: 15px; border: 1px solid rgba(0, 229, 255, 0.3); padding: 15px;">
        <h4 style="color:#4cc9f0; margin-top:0; text-align:center;">Contexto del Proyecto</h4>
        <p style="font-size:13px; color:#e0e0e0; margin-bottom:5px;"><b>Laboratorio:</b> #9 — Despliegue de Modelos</p>
        <p style="font-size:13px; color:#e0e0e0; margin-bottom:5px;"><b>Curso:</b> Analítica de Datos</p>
        <p style="font-size:13px; color:#e0e0e0; margin-bottom:5px;"><b>Profesor:</b> Duván Cataño</p>
        <p style="font-size:13px; color:#e0e0e0; margin-bottom:5px;"><b>Institución:</b> Universidad de Antioquia</p>
    </div>
    """, unsafe_allow_html=True)


#================================================================================#
# 7. SECCIÓN: FÚTBOL (REGRESIÓN)
#================================================================================#
if selected == "Fútbol (Regresión)":
    tarjeta_titulo(
        "trophy", "Predicción de Valor de Mercado",
        "Modelo de regresión (Random Forest) que estima el valor de mercado de un jugador de fútbol en euros."
    )

    # Listas categóricas derivadas de las features procesadas
    lista_pies = sorted([c.replace('pie_habil_', '') for c in features_regression if c.startswith('pie_habil_')])
    lista_posiciones = sorted([c.replace('posicion_principal_', '') for c in features_regression if c.startswith('posicion_principal_')])
    # Nota: las columnas nacionalidad/liga_actual contienen None/NaN mezclados con strings;
    # se filtran los nulos y se ordena solo por strings para evitar TypeError en sorted().
    lista_nacionalidades_db = sorted([str(x) for x in pd.read_sql_query("SELECT DISTINCT nacionalidad FROM jugadores", conn)['nacionalidad'].dropna().tolist()])
    lista_ligas_db = sorted([str(x) for x in pd.read_sql_query("SELECT DISTINCT liga_actual FROM jugadores", conn)['liga_actual'].dropna().tolist()])

    modo_entrada = st.radio("Modo de entrada de datos:", ["Manual", "Desde Base de Datos"], horizontal=True, key="radio_futbol")

    # --- Session state para valores cargados desde DB ---
    if "futbol_valores" not in st.session_state:
        st.session_state.futbol_valores = None

    # ----------------------------------------------------------------
    # MODO: DESDE BASE DE DATOS
    # ----------------------------------------------------------------
    if modo_entrada == "Desde Base de Datos":
        sub_modo = st.radio("Buscar por:", ["Por ID", "Por filtro"], horizontal=True, key="radio_futbol_db")

        if sub_modo == "Por ID":
            col_id, col_btn = st.columns([3, 1])
            with col_id:
                pid = st.number_input("player_id", min_value=215, max_value=1516901, value=927331, step=1,
                                      help="Identificador numérico del jugador en la base de datos.")
            with col_btn:
                st.write("")  # espaciador
                if st.button("Cargar", use_container_width=True, key="btn_cargar_id"):
                    df_j = load_jugador_by_id(pid)
                    if df_j.empty:
                        st.error(f"No se encontró ningún jugador con player_id = {pid}.")
                        st.session_state.futbol_valores = None
                    else:
                        st.session_state.futbol_valores = df_j.iloc[0].to_dict()
                        st.success(f"Jugador cargado: player_id={pid}")

        else:  # Por filtro
            with st.expander("Filtros de búsqueda", expanded=True):
                cf1, cf2, cf3 = st.columns(3)
                with cf1:
                    f_nac = st.selectbox("Nacionalidad", ["Todas"] + lista_nacionalidades_db, key="f_nac")
                with cf2:
                    f_liga = st.selectbox("Liga", ["Todas"] + lista_ligas_db, key="f_liga")
                with cf3:
                    f_pos = st.selectbox("Posición", ["Todas"] + lista_posiciones, key="f_pos")

                df_filtr = load_jugadores_filtrados(f_nac, f_liga, f_pos, limite=100)
                if df_filtr.empty:
                    st.warning("No hay jugadores que cumplan con esos filtros.")
                else:
                    st.caption(f"{len(df_filtr)} jugadores encontrados (top 100 por valor):")
                    df_show = df_filtr[['player_id', 'edad_al_momento', 'nacionalidad', 'liga_actual',
                                        'posicion_principal', 'valor_mercado_eur_TARGET']].copy()
                    df_show['valor_mercado_eur_TARGET'] = df_show['valor_mercado_eur_TARGET'].apply(lambda v: f"€ {v:,.0f}")
                    st.dataframe(df_show, use_container_width=True, hide_index=True)
                    opciones = df_filtr['player_id'].tolist()
                    sel = st.selectbox("Selecciona un jugador:", opciones, key="sel_jugador_filtr")
                    if st.button("Cargar seleccionado", use_container_width=True, key="btn_cargar_filtr"):
                        st.session_state.futbol_valores = df_filtr[df_filtr['player_id'] == sel].iloc[0].to_dict()
                        st.success(f"Jugador cargado: player_id={sel}")

        st.markdown("<hr style='border:1px solid rgba(0,229,255,0.2);'>", unsafe_allow_html=True)
        st.markdown("#### Variables cargadas (editables)")
        if st.session_state.futbol_valores is None:
            st.info("👆 Carga un jugador desde la base de datos para rellenar los inputs. También puedes editarlos antes de predecir.")

    # ----------------------------------------------------------------
    # FORMULARIO DE INPUTS (común a ambos modos, pre-rellenado si hay DB)
    # ----------------------------------------------------------------
    v = st.session_state.futbol_valores if st.session_state.futbol_valores else {}

    def _default(key, fallback):
        val = v.get(key, fallback)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return fallback
        return val

    with st.form("form_regresion"):
        st.markdown("<h5 style='color:#4cc9f0; border-bottom:1px solid rgba(0,229,255,0.3); padding-bottom:6px;'>Perfil del Jugador</h5>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            edad = st.number_input("Edad al momento", min_value=15, max_value=45, value=int(_default('edad_al_momento', 25)))
            mes_nacimiento = st.slider("Mes de Nacimiento", 1, 12, int(_default('mes_de_nacimiento', 6)))
            pie_default = _default('pie_habil', 'right')
            pie = st.selectbox("Pie Hábil", lista_pies, index=lista_pies.index(pie_default) if pie_default in lista_pies else 0)
        with c2:
            altura = st.number_input("Altura (cm)", min_value=150, max_value=210, value=int(_default('altura_cm', 180)))
            pos_default = _default('posicion_principal', 'Centre-Forward')
            posicion = st.selectbox("Posición Principal", lista_posiciones,
                                    index=lista_posiciones.index(pos_default) if pos_default in lista_posiciones else 0)
        with c3:
            nac_default = _default('nacionalidad', 'Colombia')
            nacionalidad = st.selectbox("Nacionalidad", lista_nacionalidades_db,
                                        index=lista_nacionalidades_db.index(nac_default) if nac_default in lista_nacionalidades_db else 0)
            liga_default = _default('liga_actual', 'ES1')
            liga = st.selectbox("Liga Actual", lista_ligas_db,
                                index=lista_ligas_db.index(liga_default) if liga_default in lista_ligas_db else 0)

        st.markdown("<h5 style='color:#4cc9f0; border-bottom:1px solid rgba(0,229,255,0.3); padding-bottom:6px; margin-top:15px;'>Rendimiento (Últimos 12 meses)</h5>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4:
            minutos = st.number_input("Minutos Jugados", min_value=0, max_value=6000, value=int(_default('minutos_jugados_12m', 2500)))
            partidos = st.number_input("Partidos Jugados", min_value=0, max_value=70, value=int(_default('partidos_jugados_12m', 35)))
            goles = st.number_input("Goles", min_value=0, max_value=60, value=int(_default('goles_12m', 8)))
        with c5:
            asistencias = st.number_input("Asistencias", min_value=0, max_value=40, value=int(_default('asistencias_12m', 5)))
            amarillas = st.number_input("Tarjetas Amarillas", min_value=0, max_value=30, value=int(_default('tarjetas_amarillas_12m', 4)))
            rojas = st.number_input("Tarjetas Rojas", min_value=0, max_value=10, value=int(_default('tarjetas_rojas_12m', 0)))
        with c6:
            participacion = st.number_input("Participación Goles p/90", min_value=0.0, max_value=3.0,
                                            value=float(_default('participacion_goles_p90', 0.45)), format="%.2f")
            partidos_sel = st.number_input("Partidos Selección (12m)", min_value=0, max_value=20, value=int(_default('partidos_seleccion_12m', 3)))
            convocatorias_sel = st.number_input("Convocatorias Históricas Sel.", min_value=0, max_value=150,
                                                value=int(_default('convocatorias_historicas_seleccion', 12)))

        st.markdown("<h5 style='color:#4cc9f0; border-bottom:1px solid rgba(0,229,255,0.3); padding-bottom:6px; margin-top:15px;'>Mercado</h5>", unsafe_allow_html=True)
        c7, c8 = st.columns(2)
        with c7:
            dias_contrato = st.number_input("Días para fin de contrato", min_value=0, max_value=3000, value=int(_default('dias_para_fin_contrato', 365)))
        with c8:
            valor_historico = st.number_input("Valor Máx. Histórico Previo (€)", min_value=0, max_value=200000000,
                                              value=int(_default('valor_maximo_historico_previo', 5000000)), step=500000)

        submitted = st.form_submit_button("Predict", type="primary", use_container_width=True)

    if submitted:
        input_dict = {
            'edad_al_momento': edad, 'mes_de_nacimiento': mes_nacimiento, 'altura_cm': altura,
            'pie_habil': pie, 'posicion_principal': posicion, 'nacionalidad': nacionalidad,
            'minutos_jugados_12m': minutos, 'partidos_jugados_12m': partidos,
            'goles_12m': goles, 'asistencias_12m': asistencias,
            'tarjetas_amarillas_12m': amarillas, 'tarjetas_rojas_12m': rojas,
            'participacion_goles_p90': participacion, 'partidos_seleccion_12m': partidos_sel,
            'convocatorias_historicas_seleccion': convocatorias_sel,
            'dias_para_fin_contrato': dias_contrato,
            'valor_maximo_historico_previo': valor_historico, 'liga_actual': liga,
        }
        df_input = pd.DataFrame([input_dict])
        try:
            pred = float(model_regression.predict(df_input)[0])
            valor_real = v.get('valor_mercado_eur_TARGET') if st.session_state.futbol_valores else None

            if valor_real is not None:
                error_eur = pred - float(valor_real)
                error_pct = (error_eur / float(valor_real)) * 100 if float(valor_real) != 0 else 0.0
                col_r1, col_r2, col_r3 = st.columns(3)
                with col_r1:
                    st.markdown(tarjeta_resultado("bi-cash-stack", "Predicción", f"€ {pred:,.0f}",
                                                  "#10B981", "#10B981", "rgba(16,185,129,0.3)"), unsafe_allow_html=True)
                with col_r2:
                    st.markdown(tarjeta_resultado("bi-bullseye", "Valor Real", f"€ {float(valor_real):,.0f}",
                                                  "#00e5ff", "#00e5ff", "rgba(0,229,255,0.3)"), unsafe_allow_html=True)
                with col_r3:
                    color_err = "#f72585" if abs(error_pct) > 30 else "#4cc9f0"
                    st.markdown(tarjeta_resultado("bi-arrow-left-right", "Error",
                                                  f"€ {error_eur:,.0f}\n({error_pct:+.1f}%)",
                                                  color_err, color_err, "rgba(247,37,133,0.2)"), unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: rgba(16,185,129,0.1); border:2px solid #10B981;
                            border-radius:12px; padding:30px; text-align:center; margin-top:15px;
                            box-shadow:0 0 30px rgba(16,185,129,0.3);">
                    <p style="color:#8b949e; margin:0; font-size:0.9rem;">Valor de Mercado Predicho</p>
                    <h2 style="color:#10B981; margin:10px 0; font-size:2.4rem;">€ {pred:,.0f}</h2>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error al generar la predicción: {e}")


#================================================================================#
# 8. SECCIÓN: AJEDREZ (CLASIFICACIÓN)
#================================================================================#
elif selected == "Ajedrez (Clasificación)":
    tarjeta_titulo(
        "puzzle", "Predicción de Dificultad de Puzzle",
        "Modelo de clasificación (XGBoost) que predice el nivel de dificultad cognitiva (Principiante / Intermedio / Avanzado / Maestro) de un puzzle de ajedrez."
    )

    extractor = ChessFeatureExtractor()
    modo_entrada_a = st.radio("Modo de entrada de datos:",
                              ["Editor de tablero", "Pegar FEN", "Desde Base de Datos"],
                              horizontal=True, key="radio_ajedrez")

    setup_fen, first_move = "", ""
    features_from_db = None  # si viene de DB, las 6 features ya están calculadas
    bloque_fen_valido = False

    # ----------------------------------------------------------------
    # MODO: EDITOR DE TABLERO (drag-and-drop)
    # ----------------------------------------------------------------
    if modo_entrada_a == "Editor de tablero":
        st.markdown("Monta la posición arrastrando piezas, confirma y realiza el primer movimiento:")
        board_state = chessboard_component(key="chess_board", default={"phase": "setup", "setup_fen": "", "first_move_uci": ""})
        if board_state and isinstance(board_state, dict) and board_state.get("phase") == "done":
            setup_fen = board_state.get("setup_fen", "")
            first_move = board_state.get("first_move_uci", "")
            bloque_fen_valido = bool(setup_fen and first_move)
        else:
            st.info("👆 Termina ambas fases del editor (setup + primer movimiento) para habilitar Predict.")

    # ----------------------------------------------------------------
    # MODO: PEGAR FEN
    # ----------------------------------------------------------------
    elif modo_entrada_a == "Pegar FEN":
        st.markdown("Pega un FEN válido y el primer movimiento del puzzle en formato UCI (ej: `e2e4`):")
        fen_input = st.text_input("FEN de la posición",
                                  value="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                                  help="Formato FEN estándar, ej: r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
        move_input = st.text_input("Primer movimiento (UCI)", value="e2e4", help="Notación UCI: casilla origen + destino (+ promoción). Ej: e2e4, g7g8q")
        if fen_input and move_input:
            try:
                _ = chess.Board(fen_input)  # validar FEN
                setup_fen = fen_input.strip()
                first_move = move_input.strip()
                bloque_fen_valido = True
                # Renderizar tablero (con caché por FEN)
                cache_key = f"fen_img_{hash(setup_fen)}"
                if cache_key not in st.session_state:
                    path = render_board_image(setup_fen, nombre=f"fen_{abs(hash(setup_fen))}")
                    if path and os.path.exists(path):
                        st.session_state[cache_key] = path
                    else:
                        st.session_state[cache_key] = None
                img_path = st.session_state.get(cache_key)
                if img_path:
                    mostrar_tablero_centrado(img_path, "Posición del FEN")
                else:
                    st.warning("No se pudo renderizar el tablero. Verifica el FEN.")
            except Exception as e:
                st.error(f"FEN inválido: {e}")

    # ----------------------------------------------------------------
    # MODO: DESDE BASE DE DATOS
    # ----------------------------------------------------------------
    elif modo_entrada_a == "Desde Base de Datos":
        st.markdown("Carga un puzzle desde la base de datos de Lichess (5.8M de puzzles):")
        col_pid, col_rng = st.columns([2, 3])
        with col_pid:
            pid_a = st.text_input("PuzzleId (opcional)", value="", help="Si lo dejas vacío, se sampleará un puzzle aleatorio dentro del rango de Rating.")
        with col_rng:
            rating_min_a, rating_max_a = st.slider("Rango de Rating (ELO)", 400, 3300, (1200, 2200), 50, key="sl_rng_a")

        if st.button("Cargar puzzle", use_container_width=True, type="primary", key="btn_cargar_puzzle"):
            if pid_a.strip():
                df_p = load_puzzle_by_id(pid_a.strip())
                if df_p.empty:
                    st.error(f"No se encontró ningún puzzle con PuzzleId = {pid_a.strip()!r}.")
                else:
                    st.session_state.puzzle_cargado = df_p.iloc[0].to_dict()
                    st.success(f"Puzzle cargado: {pid_a.strip()} (Rating={int(df_p.iloc[0]['Rating'])})")
            else:
                with st.spinner("Sampleando puzzle aleatorio..."):
                    df_p = load_puzzle_aleatorio(rating_min_a, rating_max_a)
                    if df_p.empty:
                        st.error("No se encontraron puzzles en ese rango de Rating.")
                    else:
                        st.session_state.puzzle_cargado = df_p.iloc[0].to_dict()
                        st.success(f"Puzzle aleatorio cargado: {df_p.iloc[0]['PuzzleId']} (Rating={int(df_p.iloc[0]['Rating'])})")

        p = st.session_state.get("puzzle_cargado")
        if p is not None:
            with st.expander("Puzzle cargado (datos)", expanded=True):
                st.markdown(f"**PuzzleId:** `{p['PuzzleId']}`  |  **Rating:** `{int(p['Rating'])}`  |  **Themes:** `{p['Themes']}`")
                st.markdown(f"**FEN:** `{p['FEN']}`")
                st.markdown(f"**Moves:** `{p['Moves']}`  (primer movimiento: `{str(p['Moves']).split()[0]}`)")
            # Renderizar el tablero de la posición inicial del puzzle
            cache_key = f"db_img_{p['PuzzleId']}"
            if cache_key not in st.session_state:
                path = render_board_image(p['FEN'], nombre=f"db_{p['PuzzleId']}")
                if path and os.path.exists(path):
                    st.session_state[cache_key] = path
                else:
                    st.session_state[cache_key] = None
            img_path = st.session_state.get(cache_key)
            if img_path:
                mostrar_tablero_centrado(img_path, f"Posición inicial — Puzzle {p['PuzzleId']}")
            setup_fen = p['FEN']
            first_move = str(p['Moves']).split()[0]
            features_from_db = {
                'branching_factor': p['branching_factor'], 'forcing_index': p['forcing_index'],
                'graph_density': p['graph_density'], 'tension_components': p['tension_components'],
                'spatial_entropy': p['spatial_entropy'], 'com_chebyshev_dist': p['com_chebyshev_dist'],
            }
            bloque_fen_valido = True
        else:
            st.info("👆 Carga un puzzle para rellenar los metadatos y habilitar Predict.")

    # ----------------------------------------------------------------
    # METADATOS + PREDICCIÓN (común a los 3 modos)
    # ----------------------------------------------------------------
    if modo_entrada_a != "Desde Base de Datos" or st.session_state.get("puzzle_cargado") is not None:
        st.markdown("<hr style='border:1px solid rgba(0,229,255,0.2);'>", unsafe_allow_html=True)
        st.markdown("<h5 style='color:#4cc9f0; border-bottom:1px solid rgba(0,229,255,0.3); padding-bottom:6px;'>Metadatos del Puzzle</h5>", unsafe_allow_html=True)

        # Pre-rellenar metadatos si hay puzzle cargado
        pa = st.session_state.get("puzzle_cargado")
        def _pa(key, fb):
            if pa is None: return fb
            val = pa.get(key, fb)
            return val if val is not None else fb

        cm1, cm2, cm3 = st.columns(3)
        with cm1:
            rating_dev = st.number_input("Rating Deviation", min_value=0, max_value=600, value=int(_pa('RatingDeviation', 80)))
        with cm2:
            popularity = st.number_input("Popularity", min_value=-100, max_value=100, value=int(_pa('Popularity', 90)))
        with cm3:
            nb_plays = st.number_input("NbPlays", min_value=0, max_value=10000000, value=int(_pa('NbPlays', 1000)), step=100)
        themes_input = st.text_input("Themes (separados por espacio)", value=_pa('Themes', 'mate fork'),
                                     help="Ej: 'mate fork pin endgame'")

        if st.button("Predict", type="primary", use_container_width=True, key="btn_predict_clf"):
            if not bloque_fen_valido:
                st.warning("⚠️ Falta una posición válida y un primer movimiento. Completa el modo de entrada seleccionado.")
            else:
                try:
                    # 6 features del tablero
                    if features_from_db is not None:
                        feats = features_from_db
                    else:
                        feats = extractor.get_all_features(setup_fen, first_move)

                    input_dict = {
                        'RatingDeviation': rating_dev, 'Popularity': popularity, 'NbPlays': nb_plays,
                        'Themes': themes_input,
                        'branching_factor': feats.get('branching_factor', 0),
                        'forcing_index': feats.get('forcing_index', 0.0),
                        'graph_density': feats.get('graph_density', 0.0),
                        'tension_components': feats.get('tension_components', 0),
                        'spatial_entropy': feats.get('spatial_entropy', 0.0),
                        'com_chebyshev_dist': feats.get('com_chebyshev_dist', 0.0),
                    }
                    df_input_a = pd.DataFrame([input_dict])
                    clase_pred = int(model_classification.predict(df_input_a)[0])
                    probas = model_classification.predict_proba(df_input_a)[0]
                    nombre_clase = CLASES_DIFICULTAD.get(clase_pred, f"Clase {clase_pred}")

                    # ¿Hay valor real para comparar?
                    rating_real = None
                    if pa is not None and 'Rating' in pa:
                        rating_real = int(pa['Rating'])
                    elif modo_entrada_a == "Pegar FEN":
                        rating_real = None

                    if rating_real is not None:
                        clase_real = clase_real_desde_rating(rating_real)
                        nombre_real = CLASES_DIFICULTAD.get(clase_real, f"Clase {clase_real}")
                        acierto = (clase_pred == clase_real)

                        col_a1, col_a2, col_a3 = st.columns(3)
                        with col_a1:
                            st.markdown(tarjeta_resultado("bi-cpu", "Predicción", nombre_clase,
                                                          "#f72585", "#f72585", "rgba(247,37,133,0.3)"), unsafe_allow_html=True)
                        with col_a2:
                            st.markdown(tarjeta_resultado("bi-bullseye", f"Real (Rating {rating_real})", nombre_real,
                                                          "#00e5ff", "#00e5ff", "rgba(0,229,255,0.3)"), unsafe_allow_html=True)
                        with col_a3:
                            if acierto:
                                st.markdown(tarjeta_resultado("bi-check-circle", "Resultado", "✓ Correcto",
                                                              "#10B981", "#10B981", "rgba(16,185,129,0.3)"), unsafe_allow_html=True)
                            else:
                                st.markdown(tarjeta_resultado("bi-x-circle", "Resultado", "✗ Incorrecto",
                                                              "#f72585", "#f72585", "rgba(247,37,133,0.3)"), unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background-color: rgba(247,37,133,0.1); border:2px solid #f72585;
                                    border-radius:12px; padding:25px; text-align:center; margin-top:15px;
                                    box-shadow:0 0 25px rgba(247,37,133,0.3);">
                            <p style="color:#8b949e; margin:0; font-size:0.9rem;">Nivel de Dificultad Predicho</p>
                            <h2 style="color:#f72585; margin:8px 0; font-size:2.2rem;">{nombre_clase}</h2>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<h5 style='color:#4cc9f0; margin-top:20px;'>Probabilidades por Clase</h5>", unsafe_allow_html=True)
                    barras_probabilidad(probas, model_classification.classes_)

                    with st.expander("Ver features del tablero calculadas"):
                        st.markdown(f"**FEN:** `{setup_fen}`")
                        st.markdown(f"**Primer movimiento (UCI):** `{first_move}`")
                        feats_df = pd.DataFrame([{k: v for k, v in feats.items() if k != '_empty'}])
                        st.dataframe(feats_df.T.rename(columns={0: 'Valor'}), use_container_width=True)

                except Exception as e:
                    st.error(f"Error al generar la predicción: {e}")
