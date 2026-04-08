import streamlit as st
import pandas as pd
import sqlite3
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import sys
import chess
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA (VA PRIMERO SIEMPRE SIEMPRE SIEMPRE)
st.set_page_config(page_title="Dashboard Analítico", layout="wide", initial_sidebar_state="collapsed")

# 2. INICIALIZACIÓN DE VARIABLES
if "ajedrez_df" not in st.session_state:
    st.session_state["ajedrez_df"] = pd.DataFrame()
    
if "query_chess_visual" not in st.session_state:
    st.session_state["query_chess_visual"] = ""

if "ultima_consulta_ajedrez" not in st.session_state:
    st.session_state["ultima_consulta_ajedrez"] = ""

# 3. DIRECTORIO TEMPORAL
@st.cache_resource
def get_session_temp_dir():
    """Crea un directorio temporal único para esta sesión."""
    temp_dir = tempfile.mkdtemp(prefix="chess_session_")
    return temp_dir

session_temp_dir = get_session_temp_dir()

# 4. FUNCIÓN GENERADORA
def generate_puzzle_image(nombre_archivo, fen, temp_dir, board_style, pieces_style, flip=False):
    output_path = os.path.join(temp_dir, f"{nombre_archivo}.png")
    
    if os.path.exists(output_path):
        return output_path
        
    # Definimos el bando: si flip es True, queremos la vista de negras
    lado = "black" if flip else "white"
    
    command = [
        sys.executable, "src/render_position.py",
        "--fen", fen, 
        "--board", board_style, 
        "--pieces", pieces_style,
        "--size", "60",  # 60px por cuadro = 480px total de tablero
        "--side", lado,   
        "--output", output_path
    ]
    
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        # Esto te mostrará el error real si el script de Python falla
        st.error(f"Error en render_position.py: {e.stderr}")
        return None

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# Metemos el html (Fondo Vanta.js)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
vanta_html = """
<script>
    var threeScript = window.parent.document.createElement('script');
    threeScript.src = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js";
    window.parent.document.head.appendChild(threeScript);
    
    threeScript.onload = function() {
        var vantaScript = window.parent.document.createElement('script');
        vantaScript.src = "https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js";
        window.parent.document.head.appendChild(vantaScript);
        
        vantaScript.onload = function() {
            window.parent.VANTA.NET({
                el: window.parent.document.querySelector('.stApp'),
                mouseControls: true,
                touchControls: true,
                gyroControls: false,
                minHeight: 200.00,
                minWidth: 200.00,
                scale: 1.00,
                scaleMobile: 1.00,
                color: 0x3fbbff,
                backgroundColor: 0x110c1f
            });
        };
    };
</script>
"""
components.html(vanta_html, width=0, height=0)

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# Diseño CSS
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: transparent !important;
}

[data-testid="stExpander"], .stDataFrame, div[data-testid="stMetric"], .stTabs {
    background-color: rgba(15, 20, 30, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 15px !important; 
    border: 1px solid rgba(0, 229, 255, 0.3) !important; 
}

.stTabs {
    padding-top: 15px !important;
    padding-left: 15px !important;
    padding-right: 15px !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #00e5ff !important;
}

div.stButton > button {
    background-color: rgba(11, 15, 25, 0.7) !important;
    color: #00e5ff !important;
    border: 1px solid #00e5ff !important;
    border-radius: 12px !important;
    font-weight: bold !important;
    letter-spacing: 1px !important;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.2), inset 0 0 5px rgba(0, 229, 255, 0.1) !important;
    transition: all 0.3s ease-in-out !important;
}

div.stButton > button:hover {
    background-color: #00e5ff !important;
    color: #0b0f19 !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.6) !important;
}

h1, h2, h3, label, p, .st-emotion-cache-16idsys p { color: #4cc9f0 !important; }
</style>
""", unsafe_allow_html=True)

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 2. Conexión a Base de Datos
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
CARPETA_RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ruta_db = os.path.join(CARPETA_RAIZ, "database", "proyecto_analitica.db")
conexion = sqlite3.connect(ruta_db)

st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
        <h1 style="margin: 0; padding: 0; line-height: 1;"> Consultor Interactivo</h1>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Regresión (Jugadores de Fútbol)", "Clasificación (Táctica Ajedrez)"])

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# PESTAÑA 1: JUGADORES (REGRESIÓN)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
with tab1:
    st.markdown("""<h2 style="margin: 0; padding: 0; line-height: 1; color: #4cc9f0;"> Monitor de Jugadores (Scouting)</h2><br>""", unsafe_allow_html=True)
    
    with st.expander("[ Panel de Filtros Jugadores ]", expanded=True):
        col1_f, col2_f, col3_f, col4_f = st.columns(4)
        
        with col1_f:
            try:
                opciones_liga = pd.read_sql_query("SELECT DISTINCT liga_actual FROM jugadores WHERE liga_actual IS NOT NULL", conexion)
                filtro_liga = st.multiselect("Liga Actual:", opciones_liga['liga_actual'].tolist(), default=opciones_liga['liga_actual'].tolist()[:3])
            except:
                filtro_liga = []
            
            columna_orden_f = st.selectbox("Ordenar por:", ["valor_mercado_eur_TARGET", "edad_al_momento", "goles_12m", "asistencias_12m"])
            tipo_orden_f = st.radio("Dirección:", ["Descendente", "Ascendente"], key="dir_f")
            limite_f = st.number_input("Límite de registros:", 1, 5000, 100, key="lim_f")
            
        with col2_f:
            val_min, val_max = st.slider("Valor Mercado (Millones €):", 0.0, 200.0, (0.0, 200.0), 0.5)
            age_min, age_max = st.slider("Edad al momento:", 15.0, 45.0, (15.0, 45.0), 1.0)
            altura_min, altura_max = st.slider("Altura (cm):", 150.0, 210.0, (150.0, 210.0), 1.0)
            
        with col3_f:
            goles_min, goles_max = st.slider("Goles (12m):", 0, 100, (0, 100), 1)
            asist_min, asist_max = st.slider("Asistencias (12m):", 0, 50, (0, 50), 1)
            
        with col4_f:
            partidos_min, partidos_max = st.slider("Partidos Jugados (12m):", 0, 80, (0, 80), 1)
            rojas_min, rojas_max = st.slider("Tarjetas Rojas (12m):", 0, 10, (0, 10), 1)

    if st.button(" Consultar Jugadores ", type="primary", use_container_width=True, key="btn_football"):
        
        # Multiplicamos por 1,000,000 el valor del slider porque en la BD está en euros enteros
        where_cond_f = f"""CAST(valor_mercado_eur_TARGET AS REAL) BETWEEN {val_min * 1000000} AND {val_max * 1000000} 
                        AND CAST(edad_al_momento AS REAL) BETWEEN {age_min} AND {age_max}
                        AND CAST(altura_cm AS REAL) BETWEEN {altura_min} AND {altura_max}
                        AND CAST(goles_12m AS REAL) BETWEEN {goles_min} AND {goles_max}
                        AND CAST(asistencias_12m AS REAL) BETWEEN {asist_min} AND {asist_max}
                        AND CAST(partidos_jugados_12m AS REAL) BETWEEN {partidos_min} AND {partidos_max}
                        AND CAST(tarjetas_rojas_12m AS REAL) BETWEEN {rojas_min} AND {rojas_max}"""
        
        if filtro_liga:
            ligas_f_str = "', '".join(filtro_liga)
            where_cond_f += f"\n  AND liga_actual IN ('{ligas_f_str}')"
            
        dir_sql_f = "DESC" if tipo_orden_f == "Descendente" else "ASC"

        col_res1, col_res2 = st.columns(2)

        try:
            with col_res1:
                st.subheader("1. Base de Datos Filtrada")
                q1_f = f"SELECT id_observacion, player_id, posicion_principal, liga_actual, valor_mercado_eur_TARGET, edad_al_momento, goles_12m, asistencias_12m \nFROM jugadores \nWHERE {where_cond_f} \nORDER BY CAST({columna_orden_f} AS REAL) {dir_sql_f} \nLIMIT {limite_f};"
                # Mostramos la consulta SQL
                st.code(q1_f, language="sql") 
                st.dataframe(pd.read_sql_query(q1_f, conexion), use_container_width=True)

                st.subheader("3. Top 10 Jugadores más Valiosos")
                q3_f = f"SELECT id_observacion as Jugador, liga_actual as Liga, ROUND(CAST(valor_mercado_eur_TARGET AS REAL)/1000000, 2) as Valor_Millones \nFROM jugadores \nWHERE {where_cond_f} \nORDER BY valor_mercado_eur_TARGET DESC \nLIMIT 10;"
                st.code(q3_f, language="sql")
                st.dataframe(pd.read_sql_query(q3_f, conexion), use_container_width=True)

                st.subheader("5. Relación: Partidos de Selección vs Valor")
                q5_f = f"SELECT partidos_seleccion_12m as Partidos_Seleccion, COUNT(*) as Total_Jugadores, ROUND(AVG(CAST(valor_mercado_eur_TARGET AS REAL))/1000000, 2) as Valor_Promedio_M \nFROM jugadores \nWHERE {where_cond_f} \nGROUP BY partidos_seleccion_12m \nORDER BY Partidos_Seleccion DESC \nLIMIT 10;"
                st.code(q5_f, language="sql")
                st.dataframe(pd.read_sql_query(q5_f, conexion), use_container_width=True)
                
                st.subheader("7. Indisciplina (Tarjetas Rojas y Amarillas)")
                q7_f = f"SELECT id_observacion as Jugador, CAST(tarjetas_rojas_12m AS INTEGER) as Rojas, CAST(tarjetas_amarillas_12m AS INTEGER) as Amarillas, ROUND(CAST(valor_mercado_eur_TARGET AS REAL)/1000000, 2) as Valor_Millones \nFROM jugadores \nWHERE {where_cond_f} \nORDER BY Rojas DESC, Amarillas DESC \nLIMIT 10;"
                st.code(q7_f, language="sql")
                st.dataframe(pd.read_sql_query(q7_f, conexion), use_container_width=True)

                st.subheader("9. Días para Fin de Contrato vs Valor")
                q9_f = f"SELECT id_observacion as Jugador, CAST(dias_para_fin_contrato AS INTEGER) as Dias_Contrato, ROUND(CAST(valor_mercado_eur_TARGET AS REAL)/1000000, 2) as Valor_Millones \nFROM jugadores \nWHERE {where_cond_f} \nORDER BY Dias_Contrato DESC \nLIMIT 10;"
                st.code(q9_f, language="sql")
                st.dataframe(pd.read_sql_query(q9_f, conexion), use_container_width=True)

            with col_res2:
                st.subheader("2. Valoración Promedio por Liga")
                q2_f = f"SELECT liga_actual as Liga, COUNT(*) as Jugadores, ROUND(AVG(CAST(valor_mercado_eur_TARGET AS REAL))/1000000, 2) as Valor_Promedio_M \nFROM jugadores \nWHERE {where_cond_f} \nGROUP BY liga_actual \nORDER BY Valor_Promedio_M DESC \nLIMIT 10;"
                st.code(q2_f, language="sql")
                st.dataframe(pd.read_sql_query(q2_f, conexion), use_container_width=True)

                st.subheader("4. Eficiencia Ofensiva (Goles y Asistencias)")
                q4_f = f"SELECT id_observacion as Jugador, CAST(goles_12m AS INTEGER) as Goles, CAST(asistencias_12m AS INTEGER) as Asistencias, ROUND(CAST(valor_mercado_eur_TARGET AS REAL)/1000000, 2) as Valor_Millones \nFROM jugadores \nWHERE {where_cond_f} \nORDER BY Goles DESC \nLIMIT 10;"
                st.code(q4_f, language="sql")
                st.dataframe(pd.read_sql_query(q4_f, conexion), use_container_width=True)

                st.subheader("6. Físico (Altura y Edad Promedio por Liga)")
                q6_f = f"SELECT liga_actual as Liga, ROUND(AVG(CAST(altura_cm AS REAL)), 2) as Altura_Promedio_cm, ROUND(AVG(CAST(edad_al_momento AS REAL)), 2) as Edad_Promedio \nFROM jugadores \nWHERE {where_cond_f} \nGROUP BY liga_actual \nORDER BY Altura_Promedio_cm DESC \nLIMIT 10;"
                st.code(q6_f, language="sql")
                st.dataframe(pd.read_sql_query(q6_f, conexion), use_container_width=True)

                st.subheader("8. Valor Promedio por Nacionalidad")
                q8_f = f"SELECT nacionalidad as Pais, COUNT(*) as Jugadores, ROUND(AVG(CAST(valor_mercado_eur_TARGET AS REAL))/1000000, 2) as Valor_Promedio_M \nFROM jugadores \nWHERE {where_cond_f} \nGROUP BY nacionalidad \nORDER BY Valor_Promedio_M DESC \nLIMIT 10;"
                st.code(q8_f, language="sql")
                st.dataframe(pd.read_sql_query(q8_f, conexion), use_container_width=True)

                st.subheader("10. Impacto de Minutos Jugados (Top 10)")
                q10_f = f"SELECT id_observacion as Jugador, CAST(minutos_jugados_12m AS INTEGER) as Minutos_Jugados, ROUND(CAST(valor_mercado_eur_TARGET AS REAL)/1000000, 2) as Valor_Millones \nFROM jugadores \nWHERE {where_cond_f} \nORDER BY Minutos_Jugados DESC \nLIMIT 10;"
                st.code(q10_f, language="sql")
                st.dataframe(pd.read_sql_query(q10_f, conexion), use_container_width=True)
                
        except Exception as e:
            st.error(f"Detalle del error: {e}")

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# PESTAÑA 2: AJEDREZ (LICHESS PUZZLES)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# Inicializamos la memoria para guardar los puzzles consultados
with tab2:
    st.markdown("""<h2 style="margin: 0; padding: 0; line-height: 1; color: #4cc9f0;"> Explorador Táctico (Lichess)</h2><br>""", unsafe_allow_html=True)
    
    with st.expander("[ PANEL DE FILTROS AJEDREZ ]", expanded=True):
        col1_a, col2_a, col3_a = st.columns(3)
        
        with col1_a:
            # Extraídos de tu carpeta assets/boards
            opciones_tableros = [
                "brown", "burled_wood", "marble", "green", "glass", 
                "8_bit", "blue", "bubblegum", "dark_wood", "dash", 
                "graffiti", "icy_sea", "light", "lolz", "metal", 
                "neon", "newspaper", "orange", "parchment", "purple", 
                "red", "sand", "sky", "stone", "tan", "tournament", "walnut"
            ]
            estilo_tablero = st.selectbox("Estilo de Tablero", opciones_tableros, key="sb_board")
            
            # Extraídos de tu carpeta assets/pieces
            opciones_piezas = [
                "neo", "alpha", "3d_wood", "glass", "vintage", 
                "3d_chesskid", "3d_plastic", "3d_staunton", "8_bit", 
                "classic", "club", "condal", "game_room", "gothic", 
                "graffiti", "modern", "nature", "neo_wood", "neon", 
                "ocean", "space", "tigers", "tournament", "wood"
            ]
            estilo_piezas = st.selectbox("Estilo de Piezas", opciones_piezas, key="sb_pieces")

        with col2_a:
            rating_min, rating_max = st.slider("Rango de Rating (Elo):", 600, 3000, (1200, 2200), 50, key="sl_rating")

        with col3_a:
            # Lista de temas tácticos
            temas_comunes = [
                'advantage', 'atack', 'backRankMate', 'bishopEndgame', 'check', 'crushing', 
                'discoveredAttack', 'doubleCheck', 'endgame', 'equality', 'exposedKing', 
                'fork', 'interference', 'kingsideAttack', 'knightEndgame', 'long', 
                'master', 'mate', 'mateIn1', 'mateIn2', 'mateIn3', 'middlegame', 
                'oneMove', 'opening', 'overloading', 'passedPawn', 'pin', 'promotion', 
                'queenEndgame', 'queenRookEndgame', 'queensideAttack', 'quietMove', 
                'rookEndgame', 'sacrifice', 'short', 'skewer', 'smotheredMate', 
                'trappedPiece', 'veryLong', 'xRayAttack', 'zugzwang'
            ]
            temas_seleccionados = st.multiselect("Temas Tácticos", sorted(temas_comunes), key="ms_temas")
            limite_a = st.number_input("Límite de imágenes a renderizar:", 1, 20, 4, key="lim_a")

    col_btn, col_clean = st.columns([4, 1])
    with col_btn:
        btn_consultar_ajedrez = st.button(" Consultar y Renderizar", type="primary", use_container_width=True, key="btn_a")
    with col_clean:
        if st.button("🗑️ Limpiar Caché", use_container_width=True):
            if os.path.exists(session_temp_dir):
                shutil.rmtree(session_temp_dir)
                os.makedirs(session_temp_dir, exist_ok=True)
                st.session_state.ajedrez_df = pd.DataFrame()
                st.success("Caché limpiado.")

    # 1. DEFINICIÓN DEL FRAGMENTO 
    @st.fragment
    def renderizar_tarjeta_puzzle(row, tablero_estilo, piezas_estilo, tmp_dir):
        p_id = row['PuzzleId']
        movs = str(row['Moves']).split(" ")
        
        # Lógica de Orientación: Volteamos si el bando que soluciona es Negras
        # En Lichess, el FEN es la posición ANTES del error del rival.
        b_inicial = chess.Board(row['FEN'])
        debe_flipear = (b_inicial.turn == chess.WHITE) 
        v_tag = "flipped" if debe_flipear else "normal"
        
        # Estado local de cada puzzle
        s_key = f"paso_{p_id}"
        if s_key not in st.session_state:
            st.session_state[s_key] = 0
        
        paso = st.session_state[s_key]
        # El nombre debe coincidir con el generado en la consulta evidentemente
        nombre_img = f"{p_id}_{tablero_estilo}_{piezas_estilo}_{v_tag}_step{paso}"
        path_img = os.path.join(tmp_dir, f"{nombre_img}.png")
        
        if os.path.exists(path_img):
            st.image(path_img, use_container_width=True)
        else:
            st.error(f"No existe: {nombre_img}.png")
        
        # Info y Botones
        if paso == 0:
            st.markdown(f"<div style='text-align:center; color:#4cc9f0; font-weight:bold;'>Posición Inicial</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:center; color:#00e5ff;'>Paso {paso}/{len(movs)}: <b>{movs[paso-1]}</b></div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("◀", key=f"btn_p_{p_id}", use_container_width=True):
                if st.session_state[s_key] > 0:
                    st.session_state[s_key] -= 1
                    st.rerun(scope="fragment")
        with c2:
            if st.button("▶", key=f"btn_n_{p_id}", use_container_width=True):
                if st.session_state[s_key] < len(movs):
                    st.session_state[s_key] += 1
                    st.rerun(scope="fragment")
        
        st.caption(f"**Temas:** {str(row['Themes']).replace(' ', ', ')}")
        st.divider()

    # 2. LÓGICA DE CONSULTA
    if btn_consultar_ajedrez:
        where_cond_a = f"CAST(Rating AS REAL) BETWEEN {rating_min} AND {rating_max}"
        if temas_seleccionados:
            tema_conditions = [f"Themes LIKE '%{tema}%'" for tema in temas_seleccionados]
            where_cond_a += f" AND ({' OR '.join(tema_conditions)})"
            
        # --- LAS 5 CONSULTAS SEGURAS (Con saltos de línea \n para que se vean melas) ---
        query_ajedrez = f"SELECT PuzzleId, FEN, Rating, Popularity, NbPlays, Themes, Moves \nFROM muestra \nWHERE {where_cond_a} \nLIMIT {limite_a};"
        
        q2_a = f"SELECT ROUND(AVG(CAST(Rating AS REAL)), 2) as Rating_Promedio, \n       ROUND(AVG(CAST(Popularity AS REAL)), 2) as Popularidad_Promedio \nFROM muestra \nWHERE {where_cond_a};"
        
        q3_a = f"SELECT PuzzleId, CAST(NbPlays AS INTEGER) as Numero_Jugadas, Rating \nFROM muestra \nWHERE {where_cond_a} \nORDER BY Numero_Jugadas DESC \nLIMIT 5;"
        
        q4_a = f"SELECT Popularity, COUNT(*) as Cantidad_Puzzles, \n       ROUND(AVG(CAST(Rating AS REAL)), 2) as Rating_Promedio \nFROM muestra \nWHERE {where_cond_a} \nGROUP BY Popularity \nORDER BY Cantidad_Puzzles DESC \nLIMIT 5;"
        
        q5_a = f"SELECT RatingDeviation, COUNT(*) as Frecuencia \nFROM muestra \nWHERE {where_cond_a} \nGROUP BY RatingDeviation \nORDER BY Frecuencia DESC \nLIMIT 5;"

        # Guardamos TODAS las consultas en memoria para imprimirlas abajo
        st.session_state.query_chess_visual = query_ajedrez
        st.session_state.q2_sql = q2_a
        st.session_state.q3_sql = q3_a
        st.session_state.q4_sql = q4_a
        st.session_state.q5_sql = q5_a

        with st.spinner("Calculando perspectivas y ejecutando análisis estadístico..."):
            try:
                # Ejecutar y guardar en memoria
                df_temp = pd.read_sql_query(query_ajedrez, conexion)
                st.session_state.ajedrez_df = df_temp
                st.session_state.q2_a_df = pd.read_sql_query(q2_a, conexion)
                st.session_state.q3_a_df = pd.read_sql_query(q3_a, conexion)
                st.session_state.q4_a_df = pd.read_sql_query(q4_a, conexion)
                st.session_state.q5_a_df = pd.read_sql_query(q5_a, conexion)
                
                # Reset de pasos anteriores
                for k in list(st.session_state.keys()):
                    if k.startswith("paso_"): del st.session_state[k]
                
                # Generación física de archivos de imagen
                for _, r in df_temp.iterrows():
                    board = chess.Board(r['FEN'])
                    flip_needed = (board.turn == chess.WHITE)
                    tag_v = "flipped" if flip_needed else "normal"
                    
                    nombre_base = f"{r['PuzzleId']}_{estilo_tablero}_{estilo_piezas}_{tag_v}"
                    generate_puzzle_image(f"{nombre_base}_step0", board.fen(), session_temp_dir, estilo_tablero, estilo_piezas, flip=flip_needed)
                    
                    movimientos_lista = str(r['Moves']).split(" ")
                    for j, m in enumerate(movimientos_lista):
                        board.push_uci(m)
                        generate_puzzle_image(f"{nombre_base}_step{j+1}", board.fen(), session_temp_dir, estilo_tablero, estilo_piezas, flip=flip_needed)
                
                st.success(f"¡{len(df_temp)} puzzles listos para resolver!")
            except Exception as e:
                st.error(f"Error en consulta: {e}")

    # 3. MOSTRAMOS RESULTADOS
    df_actual = st.session_state.get("ajedrez_df", pd.DataFrame())

    if not df_actual.empty:
        # A. Mostramos Consola SQL Principal
        if st.session_state.get("query_chess_visual"):
            st.markdown("### 🖥️ Consola SQL: Consulta Ejecutada")
            st.code(st.session_state.query_chess_visual, language="sql")
        
        st.dataframe(df_actual, use_container_width=True)
        st.divider()

        # B. Mostrar Estadísticas 
        st.markdown("### 📊 Análisis Estadístico")
        col_stats1, col_stats2 = st.columns(2)

        with col_stats1:
            st.subheader("2. Promedios de la Muestra")
            st.code(st.session_state.get("q2_sql", ""), language="sql")
            st.dataframe(st.session_state.get("q2_a_df"), use_container_width=True)
            
            st.subheader("4. Agrupación por Popularidad")
            st.code(st.session_state.get("q4_sql", ""), language="sql")
            st.dataframe(st.session_state.get("q4_a_df"), use_container_width=True)

        with col_stats2:
            st.subheader("3. Top 5 Más Jugados (NbPlays)")
            st.code(st.session_state.get("q3_sql", ""), language="sql")
            st.dataframe(st.session_state.get("q3_a_df"), use_container_width=True)
            
            st.subheader("5. Frecuencia de Desviación (Elo)")
            st.code(st.session_state.get("q5_sql", ""), language="sql")
            st.dataframe(st.session_state.get("q5_a_df"), use_container_width=True)

        st.divider()
        st.markdown("### ♟️ Tableros Tácticos")
        
        cols_por_fila = 4
        # Dibujamos la grilla
        for i in range(0, len(df_actual), cols_por_fila):
            cols = st.columns(cols_por_fila)
            for j in range(cols_por_fila):
                if i + j < len(df_actual):
                    with cols[j]:
                        renderizar_tarjeta_puzzle(df_actual.iloc[i+j], estilo_tablero, estilo_piezas, session_temp_dir)

# Fin del script
conexion.close()