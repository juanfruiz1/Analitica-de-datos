import streamlit as st
import pandas as pd
import sqlite3
import os
import subprocess
import tempfile
import shutil
import sys
import chess
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import plotly.express as px
import time

#################################################################################
################## RECORDAR PIP INSTALL STATSMODELS #############################
#################################################################################

#⠄⢠⣿⣿⣿⣿⣿⣿⣿⣿⢹⣿⣿⣿⣿⣿⣿⢧⠸⣿⣿⣿⣿⣿
#⠄⡞⢁⡟⣿⣿⣿⡿⡏⣥⣥⣭⢻⣿⣿⡟⠛⡘⠷⢻⣏⢿⣿⣿
#⠄⠄⣼⠇⣿⣿⡟⢿⡹⠿⠿⣿⡆⢿⣿⡇⢰⣿⣿⣷⡲⢸⣿⡿
#⠄⢀⠟⠄⢻⣟⣧⠉⡰⠄⠄⢈⣟⣎⣿⡇⣯⠄⠄⠈⠳⠃⣿⡇
#⠄⠈⠄⢰⠘⣿⡜⣶⣿⣿⣿⣽⣿⣿⣿⣿⣿⣥⣤⣆⣧⡀⢸⣿
#⡄⠄⠄⠸⡄⢻⡇⢘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠘⢿
#⣿⠄⠄⠄⢷⠘⢿⠄⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠄⠄⠘
#⠃⠄⠄⠄⠈⠄⠘⠄⠄⠈⠙⢿⣿⣿⣿⣿⣿⣿⠿⠋       
#⠠⠊⠄⠄⠄⠄⠄⠄⠄⠄⢠⣸⢾⣽⣟⣫⣭⡇      
#⣠⣶⣾⣷⣶⡄⠄⠲⢶⣤⣿⣿⣷⣯⣽⡿⣻⣵⣄
#⣿⣿⣿⣿⣿⣿⣆⠄⠈⢿⡏⣰⣶⠂⠄⠐⠐⠊⠄⠄⠄⠄⠄⠄⡀
#⣿⣿⣿⣿⣿⣿⣿⡆⠄⠄⢻⠘⡃⢀⠄⠄⢀⡀⠄⠄⠄⠄⣆⠄⠘
#⣿⣿⣿⣿⣿⣿⣿⣿⡄⠄⠈⣥⡈⠁⠄⢀⣾⣿⣦⡀⠄⠄⢹⡄⠄
#⣿⣿⣿⣿⣿⣿⣿⣿⣇⠄⢀⠙⣿⣦⣴⣿⣿⣿⣿⣿⣿⣶⣼⣧⠄

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 1. CONFIGURACIÓN DE PÁGINA
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#


# --- FUNCIONES Y DIRECTORIO PARA RENDERIZADO DE AJEDREZ ---
@st.cache_resource
def get_session_temp_dir():
    """Crea un directorio temporal único para esta sesión."""
    temp_dir = tempfile.mkdtemp(prefix="chess_session_")
    return temp_dir

session_temp_dir = get_session_temp_dir()

def generate_puzzle_image(nombre_archivo, fen, temp_dir, board_style, pieces_style, flip=False):
    output_path = os.path.join(temp_dir, f"{nombre_archivo}.png")
    if os.path.exists(output_path):
        return output_path
    lado = "black" if flip else "white"
    command = [
        sys.executable, "src/render_position.py",
        "--fen", fen, "--board", board_style, "--pieces", pieces_style,
        "--size", "60", "--side", lado, "--output", output_path
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        return None


st.set_page_config(page_title="Dashboard ", page_icon="🔵", layout="wide")

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 2. INYECCIÓN DEL FONDO VANTA.JS (HACK NATIVO)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
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
    }
</script>
"""
components.html(vanta_html, width=0, height=0)

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#  
# 3. DISEÑO CSS (GLASSMORPHISM Y ACENTOS NEÓN)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#



#──────────────▒█████▓░
#────────────██▓░░░░░░█▓▓▓█
#──────────██░░░░██▓▓▓██░░░██
#────────▒█░░░▒░██▒░░░░██░░░█░
#────────█░░░███▓▓███░░░██░░░█
#───────██▒██░██░░░██░░░██░░░█
#──────▓█░░██░██░░░▓█▒░░██░░░█
#─────██░░░███░░██░░██░░██░░░██
#───██▓█░░██▒██▓███▓█░░██░░░██▒█─█
#──██░██░░▒███▓▒░░██░▒███░░▓█░░█─██
#─██░░██░░░█▒░░▒░░█░████░░▓█▒░░██▒█░
#─█░░░███░░░█░░░░█░██░█░░▒█░░░░▓█▒██
#█▓░░█▓░███░▒█░░░███░░█░░█░░░░░██▒██
#█░░░█▓░▒██████▓██░░▓█░░▒░░▓░░░█▒█▒█
#█░░░░███░░░▒▒▒░░░██░█░░░░░░░░███▒█▓
#█▒░░░░████░░░░░███░░█░░░░░░░███▒██
#─█░░░░░░████████░░░░█░░░░░░▒█▓▓█
#──█░░░░░░░░░░▓░░░░░░▒█░░░░████
#───██████████▓░██░░░░░██░████
#────────────██▓████░░████▒▒██──░
#───────────█░░░████████▒▒▒▒█▓░██
#──────────█░░░█▓────██▓▓███▓▓██
#──────────█░▓█────────────▓█▓▓█
#───────────██────────────────██▓█░
#──────────────────────────█████▓█░
#────────────────────────────░▒██▓█─▒█
#────────────────────────────────█▓██▒
#─────────────────────────────────█▓█▒
#─────────────────────────────────▒█▓█
#──────────────────────────────────█▓██
#────────────────────────────────░███▓█░
#───────────────────────────────────██▓█
#────────────────────────────────────░█▓█

st.markdown("""
<style>

/* --- CAMBIO: IMPORTAMOS LA FUENTE MONTSERRAT --- */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');

/* --- NUEVO: IMPORTAMOS BOOTSTRAP ICONS --- */
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

/* Hacer transparente el contenedor principal para que se vea la animación */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: transparent !important;
}

/* MENÚ LATERAL SÓLIDO (Excluir del fondo) */
[data-testid="stSidebar"] {
    background-color: #0b0f19 !important; /* Color oscuro sólido */
    border-right: 1px solid rgba(0, 229, 255, 0.2) !important;
    min-width: 280px !important; /* <--- AQUÍ: Forzamos a que el menú sea más ancho */
}

/* Efecto Glassmorphism para Tarjetas, DataFrames y Pestañas */
[data-testid="stExpander"], .stDataFrame, div[data-testid="stMetric"], .stTabs, div.css-1r6slb0, div.css-12oz5g7 {
    background-color: rgba(15, 20, 30, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 15px !important; 
    border: 1px solid rgba(0, 229, 255, 0.3) !important; 
}

/* Espaciado interno de las pestañas */
.stTabs {
    padding: 15px !important;
}

/* Barra de pestaña activa */
div[data-baseweb="tab-highlight"] {
    background-color: #00e5ff !important;
}

/* Colores de textos y títulos */
h1, h2, h3, label, .st-emotion-cache-16idsys p { 
    color: #4cc9f0 !important; 
}

p {
    color: #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# ⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘ #
# FUNCIONES GLOBALES DE DISEÑO 
# ⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘ #

def crear_tarjeta(icono, titulo, valor):
    return f"""
    <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px); border-radius: 15px; border: 1px solid rgba(0, 229, 255, 0.3); padding: 15px; text-align: center;">
        <i class="{icono}" style="font-size: 28px; color: #00e5ff; display: inline-block;"></i>
        <p style="margin: 5px 0 0 0; font-size: 14px; color: #e0e0e0; font-weight: 600;">{titulo}</p>
        <div style="font-size: 24px; font-weight: bold; color: white;">{valor}</div>
    </div>
    """

def card_correlacion(titulo, p_value, icono, color_borde="#00e5ff"):
    resultado = "✅ RELACIÓN SIGNIFICATIVA" if p_value < 0.05 else "⚠️ SIN RELACIÓN"
    return f"""
    <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px); border-radius: 12px; border-left: 5px solid {color_borde}; padding: 15px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1);">
        <h5 style="color: {color_borde}; margin: 0;"><i class="bi {icono}"></i> {titulo}</h5>
        <p style="margin: 5px 0; font-family: monospace; font-size: 0.9rem;">p-value: {p_value:.4e}</p>
        <div style="background: rgba(255,255,255,0.05); text-align: center; border-radius: 5px; font-size: 0.75rem; color: {color_borde}; font-weight: bold;">{resultado}</div>
    </div>
    """



#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 4. CARGA DE DATOS (SQLITE)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
@st.cache_resource
def init_connection():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ruta_db = os.path.join(base_dir, 'database', 'proyecto_analitica.db')
    return sqlite3.connect(ruta_db, check_same_thread=False)

conn = init_connection()

@st.cache_data
def load_data():
    # Cargamos el dataset 
    df_f = pd.read_sql_query("SELECT * FROM jugadores", conn)
    # Para ajedrez, cargamos una muestra general inicial para estadísticas descriptivas (evita colapsar RAM)
    df_a = pd.read_sql_query("SELECT * FROM muestra_procesada", conn)
    #df_a = pd.read_sql_query("SELECT * FROM muestra_procesada LIMIT 200000", conn)
    return df_f, df_a

df_futbol, df_ajedrez = load_data()

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 5. MENÚ LATERAL
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
with st.sidebar:
    st.markdown("<h2 style='color: white !important; text-align: center; font-weight: 700;'>Menú Principal</h2>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Fútbol (Regresión)", "Ajedrez (Clasificación)"], # <--- Modificado
        icons=["trophy", "puzzle"], # <--- Modificado
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#00e5ff", "font-size": "18px"}, 
            "nav-link": {"color": "white", "font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "rgba(0, 229, 255, 0.2)"},
            "nav-link-selected": {"background-color": "rgba(0, 229, 255, 0.3)", "border-left": "4px solid #00e5ff"},
        }
        
    )

    st.markdown("<br><hr style='border: 1px solid rgba(0, 229, 255, 0.2);'><br>", unsafe_allow_html=True)
    
    # --- INFORMACIÓN DEL PROYECTO ---
    st.markdown("""
    <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 
    15px; border: 1px solid rgba(0, 229, 255, 0.3); padding: 15px;">
        <h4 style="color: #4cc9f0; margin-top: 0; text-align: center;"> Contexto del Proyecto</h4>
        <p style="font-size: 13px; color: #e0e0e0; margin-bottom: 5px;"><b>Laboratorio:</b> #3</p>
        <p style="font-size: 13px; color: #e0e0e0; margin-bottom: 5px;"><b>Curso:</b> Analítica de Datos</p>
        <p style="font-size: 13px; color: #e0e0e0; margin-bottom: 5px;"><b>Profesor:</b> Duván Cataño</p>
        <p style="font-size: 13px; color: #e0e0e0; margin-bottom: 0;"><b>Institución:</b> Universidad de Antioquia</p>
        <p style="font-size: 13px; color: #e0e0e0; margin-bottom: 5px;"><b>Integrante 1:</b> Juan Fernando</p>
        <p style="font-size: 13px; color: #e0e0e0; margin-bottom: 5px;"><b>Integrante 2:</b> Julián David</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BADGE ADICIONAL ---
    st.markdown("""
    <div style="background-color: rgba(0, 229, 255, 0.1); padding: 10px; border-radius: 10px; border: 1px solid rgba(0, 229, 255, 0.3); text-align: center;">
        <span style="color: #e0e0e0; font-size: 12px;"><i class="bi bi-cpu" style="color: #00e5ff;"></i> Modelos implementados con scikit-learn y SQLite</span>
    </div>
    """, unsafe_allow_html=True)
    


#█████████████████████████████████████
#██████▓████████████████████████████▓▓
#████▓─███████████████████████▓▒▒─▒▒▓█
#███▓─▓██████████████████▓▒────▒▓█████
#██▓──▓███████████▓▓▒──────▒▓█████████
#█▓────██████▓▒▒───────▒██████████████
#█─────────────────▓██████████████████
#█─────────────▒▓█████████████████████
#█▓────────▒▓█████████████████████████
#███▓▒▒▒▒▓████████████████████████████
    
    

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 6. SECCIÓN: FÚTBOL (REGRESIÓN - JUGADORES INDIVIDUALES)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

if selected == "Fútbol (Regresión)":
    st.markdown("""<div style="font-size: 2.8rem; font-weight: bold; line-height: 1.2; color: #FFFFFF; 
                text-shadow: 2px 2px 8px #000000, 0px 0px 20px #000000; margin-bottom: 10px;"><i class="bi bi-graph-up-arrow" 
                style="color: #FFFFFF; margin-right: 10px;"></i> Monitor de Valor de Mercado (Jugadores)</div>""", unsafe_allow_html=True)
    st.markdown("<p>Exploración de variables predictoras para el <code>valor_mercado_eur_TARGET</code>.</p>", unsafe_allow_html=True)
    
    # --- Cálculos de KPIs (Adaptados a Jugadores) ---
    total_jugadores = len(df_futbol)
    
    # Convertimos a numérico por si SQLite lo trajo como texto SE PONE HIJODEPUTA AVECES
    df_futbol['valor_mercado_eur_TARGET'] = pd.to_numeric(df_futbol['valor_mercado_eur_TARGET'], errors='coerce')
    df_futbol['edad_al_momento'] = pd.to_numeric(df_futbol['edad_al_momento'], errors='coerce')
    df_futbol['goles_12m'] = pd.to_numeric(df_futbol['goles_12m'], errors='coerce')
    
    valor_promedio = df_futbol['valor_mercado_eur_TARGET'].mean() / 1e6 # En millones
    edad_mediana = df_futbol['edad_al_momento'].median()
    goles_totales = df_futbol['goles_12m'].sum()
    valor_maximo = df_futbol['valor_mercado_eur_TARGET'].max() / 1e6

    # --- Renderizado de las 5 Columnas de KPIs ---
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(crear_tarjeta("bi bi-people", "Total Jugadores", f"{total_jugadores:,}"), unsafe_allow_html=True)
    with col2:
        st.markdown(crear_tarjeta("bi bi-cash-stack", "Valor Medio", f"{valor_promedio:,.2f} M€"), unsafe_allow_html=True)
    with col3:
        st.markdown(crear_tarjeta("bi bi-trophy", "Valor Máximo", f"{valor_maximo:,.1f} M€"), unsafe_allow_html=True)
    with col4:
        st.markdown(crear_tarjeta("bi bi-calendar-event", "Edad Mediana", f"{edad_mediana:.1f} años"), unsafe_allow_html=True)
    with col5:
        st.markdown(crear_tarjeta("bi bi-record-circle", "Goles (Últ. 12m)", f"{goles_totales:,.0f}"), unsafe_allow_html=True)
        
    st.write("") # Espaciesito
    
    # --- Pestañas ---
    tab1, tab2, tab3, tab4 = st.tabs(["Estadísticas Descriptivas", "Gráficos Principales", "Imputaciones", "Pruebas Estadísticas"])
    
    with tab1:
        st.markdown("<h3 style='color: #4cc9f0;'> Base de Datos Procesada</h3>", unsafe_allow_html=True)
        
        # 1. ORDENAR POR VALOR DE MERCADO (Mas valiosos primero)
        # Usamos la columna exacta de tu base de datos: valor_mercado_eur_TARGET
        df_top_valiosos = df_futbol.sort_values(by='valor_mercado_eur_TARGET', ascending=False)
        
        # 2. MOSTRAR LOS TOP 100 JUGADORES
        st.dataframe(df_top_valiosos.head(100).style.set_properties(**{'text-align': 'center'}), use_container_width=True)
        
        st.markdown("---")
        st.markdown("<h3 style='color: #4cc9f0;'> Estadísticas Descriptivas</h3>", unsafe_allow_html=True)
        
        # Seleccionamos solo numéricas 
        num_cols = df_futbol.select_dtypes(include=['float64', 'int64']).columns
        df_stats = df_futbol[num_cols].describe().T
        df_stats = df_stats.rename(columns={
            'count': 'Cantidad', 'mean': 'Promedio', 'std': 'Desviación Est.',
            'min': 'Mínimo', '25%': 'Percentil 25', '50%': 'Mediana', 
            '75%': 'Percentil 75', 'max': 'Máximo'
        })
        
        df_stats_estilizado = df_stats.style.format("{:.2f}").set_properties(**{'text-align': 'center'})
        st.dataframe(df_stats_estilizado, use_container_width=True)
        
    with tab2:
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'><i class='bi bi-bar-chart-steps'></i> Análisis Exploratorio (EDA) - Fútbol</h3>", unsafe_allow_html=True)
        
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
        import math

        # --- FUNCIÓN DE ESTILO NEÓN ---
        def aplicar_estilo_neon(ax, titulo, xlabel="", ylabel=""):
            ax.set_facecolor('none')
            ax.tick_params(colors='#e0e0e0', labelsize=8)
            ax.set_xlabel(xlabel, color='#4cc9f0', fontsize=10, fontweight='bold')
            ax.set_ylabel(ylabel, color='#4cc9f0', fontsize=10, fontweight='bold')
            ax.set_title(titulo, color='#ffffff', fontsize=12, fontweight='bold', pad=10)
            for spine in ax.spines.values():
                spine.set_color((1.0, 1.0, 1.0, 0.2))
        
        # Variables numéricas completas de tu base de datos
        num_cols = ['valor_mercado_eur_TARGET', 'edad_al_momento', 'mes_de_nacimiento', 'altura_cm', 
                    'minutos_jugados_12m', 'partidos_jugados_12m', 'goles_12m', 'asistencias_12m', 
                    'tarjetas_amarillas_12m', 'tarjetas_rojas_12m', 'participacion_goles_p90', 
                    'partidos_seleccion_12m', 'convocatorias_historicas_seleccion', 
                    'dias_para_fin_contrato', 'valor_maximo_historico_previo']
        plantilla = "plotly_dark"
        config_plotly = {
            'displayModeBar': False, 
            'scrollZoom': True, 
            'displaylogo': False
        }
        # Muestra optimizada para las gráficas de dispersión (evita que el dashboard colapse)
        df_sample = df_futbol.dropna(subset=['valor_maximo_historico_previo', 'valor_mercado_eur_TARGET']).sample(n=min(30000, len(df_futbol)), random_state=42)

        # ==========================================
        # 1. DISTRIBUCIONES COMPLETAS (Como en tu Notebook)
        # ==========================================
        # ==========================================
        # 1. HISTOGRAMAS (2 por fila)
        # ==========================================
        st.markdown("<h5 style='text-align: center; color: #ffffff;'>1. Distribuciones (Variables Numéricas)</h5>", unsafe_allow_html=True)
        cols_hist = ['edad_al_momento', 'mes_de_nacimiento', 'altura_cm', 'minutos_jugados_12m', 'partidos_jugados_12m', 'goles_12m', 'asistencias_12m', 'tarjetas_amarillas_12m']
        
        for i in range(0, len(cols_hist), 2):
            c1, c2 = st.columns(2)
            with c1:
                v1 = cols_hist[i]
                f1 = px.histogram(df_sample, x=v1, nbins=30, template=plantilla, color_discrete_sequence=['#4cc9f0'])
                f1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, l=0, r=0, b=0), height=350, title_text=v1, title_x=0.5, hovermode=False, dragmode='pan')
                st.plotly_chart(f1, use_container_width=True, config=config_plotly, key=f"h_{v1}")
            with c2:
                if i + 1 < len(cols_hist):
                    v2 = cols_hist[i+1]
                    f2 = px.histogram(df_sample, x=v2, nbins=30, template=plantilla, color_discrete_sequence=['#4cc9f0'])
                    f2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, l=0, r=0, b=0), height=350, title_text=v2, title_x=0.5, hovermode=False, dragmode='pan')
                    st.plotly_chart(f2, use_container_width=True, config=config_plotly, key=f"h_{v2}")

        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)

        # ==========================================
        # 2. DETECCIÓN DE OUTLIERS (Variables Principales)
        # ==========================================
        with st.expander("📈 2. Detección de Outliers (IQR)", expanded=False):
            main_cols_out = ['valor_mercado_eur_TARGET', 'edad_al_momento', 'minutos_jugados_12m', 'goles_12m', 'valor_maximo_historico_previo']
            fig_out, axes_out = plt.subplots(1, 5, figsize=(20, 5))
            fig_out.patch.set_alpha(0.0)
            
            flierprops = dict(marker='o', markerfacecolor="#4ddbff", markeredgecolor='none', alpha=0.3, markersize=3)
            
            for i, col in enumerate(main_cols_out):
                sns.boxplot(y=df_futbol[col], color="#2164f7", ax=axes_out[i], flierprops=flierprops)
                aplicar_estilo_neon(axes_out[i], col)
                
            plt.tight_layout()
            st.pyplot(fig_out, transparent=True)

        # ==========================================
        # 3. MAPA DE CALOR (Matriz Completa)
        # ==========================================
        # 3. MATRIZ DE CORRELACIÓN
        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; color: #ffffff;'>3. Mapa de Calor de Correlaciones</h5>", unsafe_allow_html=True)
        cols_clave = ['valor_mercado_eur_TARGET', 'valor_maximo_historico_previo', 'edad_al_momento', 'minutos_jugados_12m', 'goles_12m', 'asistencias_12m', 'partidos_seleccion_12m', 'dias_para_fin_contrato']
        matriz_corr = df_futbol[cols_clave].corr()
        fig3 = px.imshow(matriz_corr, text_auto=".2f", aspect="auto", color_continuous_scale=[[0, 'rgba(11, 15, 25, 0.8)'], [0.5, 'rgba(76, 201, 240, 0.5)'], [1, '#00e5ff']])
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True, config=config_plotly)
        

        # ==========================================
        # 4. TOP RELACIONES VS TARGET (Scatters según el PDF)
        # ==========================================
        
        
        
        
        st.markdown("<h4 style='text-align: center; color: #ffffff;'>4. Relaciones Principales vs Valor de Mercado</h4>", unsafe_allow_html=True)
        
        # Las 3 variables con mayor correlación según tu documento
        top_3_vars = ['valor_maximo_historico_previo', 'goles_12m', 'asistencias_12m']
        
        fig_scat, axes_scat = plt.subplots(1, 3, figsize=(18, 5))
        fig_scat.patch.set_alpha(0.0)
        
        for i, col in enumerate(top_3_vars):
            sns.regplot(data=df_sample, x=col, y='valor_mercado_eur_TARGET', 
                        scatter_kws={'color': '#00e5ff', 'alpha': 0.15, 's': 15}, 
                        line_kws={'color': '#f72585', 'linewidth': 2}, ax=axes_scat[i])
            aplicar_estilo_neon(axes_scat[i], f"{col} vs Target", col, "Valor Mercado")
            
        plt.tight_layout()
        st.pyplot(fig_scat, transparent=True)

        # ==========================================
        # 5. INFLUENCIA CATEGÓRICA (Kruskal-Wallis Context)
        # ==========================================
        st.markdown("<h4 style='text-align: center; color: #ffffff;'>5. Impacto de Variables Categóricas</h4>", unsafe_allow_html=True)
        
        # CAMBIO 1: 4 filas, 1 columna. Aumentamos el alto de 12 a 28 para que queden gigantes.
        fig_cat, axes_cat = plt.subplots(4, 1, figsize=(18, 28)) 
        fig_cat.patch.set_alpha(0.0)
        flierprops_c = dict(marker='o', markerfacecolor='white', markeredgecolor='none', alpha=0.1, markersize=2)

        # 5.1 Posición
        sns.boxplot(data=df_sample, x='posicion_principal', y='valor_mercado_eur_TARGET', ax=axes_cat[0], palette="viridis", flierprops=flierprops_c)
        aplicar_estilo_neon(axes_cat[0], "Impacto por Posición", "Posición Principal", "Valor Mercado")
        axes_cat[0].tick_params(axis='x', rotation=45)
        # --- OPCIÓN 1 (Activa): Límite visual en 60 Millones ---
        axes_cat[0].set_ylim(-2e6, 60e6) 
        # --- OPCIÓN 2 (Inactiva): Escala Logarítmica ---
        # axes_cat[0].set_yscale('symlog')

        # 5.2 Pie Hábil
        sns.boxplot(data=df_sample, x='pie_habil', y='valor_mercado_eur_TARGET', ax=axes_cat[1], palette="magma", flierprops=flierprops_c)
        aplicar_estilo_neon(axes_cat[1], "Impacto por Pie Hábil", "Pie Hábil", "Valor Mercado")
        # --- OPCIÓN 1 (Activa): Límite visual en 60 Millones ---
        axes_cat[1].set_ylim(-2e6, 60e6)
        # --- OPCIÓN 2 (Inactiva): Escala Logarítmica ---
        # axes_cat[1].set_yscale('symlog')

        # 5.3 Liga Actual (Top 15)
        top_ligas = df_sample['liga_actual'].value_counts().index[:15]
        sns.boxplot(data=df_sample[df_sample['liga_actual'].isin(top_ligas)], x='liga_actual', y='valor_mercado_eur_TARGET', ax=axes_cat[2], palette="plasma", flierprops=flierprops_c)
        aplicar_estilo_neon(axes_cat[2], "Top 15 Ligas", "Liga", "Valor Mercado")
        axes_cat[2].tick_params(axis='x', rotation=90)
        # --- OPCIÓN 1 (Activa): Límite visual en 60 Millones ---
        axes_cat[2].set_ylim(-2e6, 60e6)
        # --- OPCIÓN 2 (Inactiva): Escala Logarítmica ---
        # axes_cat[2].set_yscale('symlog')

        # 5.4 Nacionalidad (Top 15) 
        top_nac = df_sample['nacionalidad'].value_counts().index[:15]
        sns.boxplot(data=df_sample[df_sample['nacionalidad'].isin(top_nac)], x='nacionalidad', y='valor_mercado_eur_TARGET', ax=axes_cat[3], palette="cool", flierprops=flierprops_c)
        aplicar_estilo_neon(axes_cat[3], "Top 15 Nacionalidades", "Nacionalidad", "Valor Mercado")
        axes_cat[3].tick_params(axis='x', rotation=90)
        # --- OPCIÓN 1 (Activa): Límite visual en 60 Millones ---
        axes_cat[3].set_ylim(-2e6, 60e6)
        # --- OPCIÓN 2 (Inactiva): Escala Logarítmica ---
        # axes_cat[3].set_yscale('symlog')

        # CAMBIO 3: Añadimos 'pad' al tight_layout para asegurar que las etiquetas en X no se solapen con el título del gráfico de abajo
        plt.tight_layout(pad=4.0) 
        st.pyplot(fig_cat, transparent=True)
        
        # --- CONCLUSIONES FINALES ---
        
        
        

            
        
    with tab3:
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Tratamiento de Datos Faltantes</h3>", unsafe_allow_html=True)
        
        from sklearn.impute import SimpleImputer, KNNImputer
        import plotly.graph_objects as go
        
        plantilla = "plotly_dark"
        config_plotly = {'displayModeBar': False, 'scrollZoom': True, 'displaylogo': False}

        # ====================================================================
        # 1. IMPUTACIÓN DE VARIABLES CATEGÓRICAS (VÍA MODA - PLOTLY)
        # ====================================================================
        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        
        # --- AQUÍ ESTÁ EL CAMBIO: Título Centrado ---
        st.markdown("<h4 style='text-align: center; color: #ffffff;'>1. Imputación de Variables Categóricas (Vía Moda)</h4>", unsafe_allow_html=True)
        
        cols_cat = ['pie_habil', 'nacionalidad', 'liga_actual']
        df_cat_original = df_futbol[cols_cat].copy()
        df_cat_imputado = df_futbol[cols_cat].copy()
        
        # Imputación real
        for col in cols_cat:
            if col in df_cat_imputado.columns:
                moda_val = df_cat_imputado[col].mode()[0]
                df_cat_imputado[col] = df_cat_imputado[col].fillna(moda_val)

        @st.fragment
        def render_categorica_plotly(columna):
            
            nulos_iniciales = df_cat_original[columna].isna().sum()
            moda_usada = df_cat_imputado[columna].mode()[0]
            
            # --- NUEVOS KPIS CENTRADOS (HTML PURO) ---
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            estilo_kpi = "text-align: center; background-color: rgba(15,20,30,0.6); padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 229, 255, 0.3);"
            
            with col_kpi1:
                st.markdown(f"<div style='{estilo_kpi}'><p style='color:#8b949e; margin-bottom:5px; font-size:14px;'>Valores Imputados</p><h3 style='color:#4cc9f0; margin-top:0;'>{nulos_iniciales:,}</h3></div>", unsafe_allow_html=True)
            with col_kpi2:
                st.markdown(f"<div style='{estilo_kpi}'><p style='color:#8b949e; margin-bottom:5px; font-size:14px;'>Valor Usado (Moda)</p><h3 style='color:#4cc9f0; margin-top:0;'>{moda_usada}</h3></div>", unsafe_allow_html=True)
            with col_kpi3:
                st.markdown(f"<div style='{estilo_kpi}'><p style='color:#8b949e; margin-bottom:5px; font-size:14px;'>Nulos Restantes</p><h3 style='color:#4cc9f0; margin-top:0;'>0</h3></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- Preparación de datos (Top 15 para evitar lag) ---
            top_n = 15
            conteo_antes = df_cat_original[columna].fillna('FALTANTES').value_counts().head(top_n).reset_index()
            conteo_antes.columns = [columna, 'Cantidad']
            
            # Reindexamos el 'Después' para comparar exactamente las mismas barras
            conteo_despues = df_cat_imputado[columna].value_counts().reindex(conteo_antes[columna]).fillna(0).reset_index()
            conteo_despues.columns = [columna, 'Cantidad']

            # --- Gráficos Plotly ---
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                fig1 = px.bar(conteo_antes, x=columna, y='Cantidad', template=plantilla, color_discrete_sequence=['#4cc9f0'])
                fig1.update_layout(title_text=f"ANTES: {columna} (Con Nulos)", title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=0, l=0, r=0), height=350, dragmode='pan')
                st.plotly_chart(fig1, use_container_width=True, config=config_plotly)
                
            with col_b2:
                fig2 = px.bar(conteo_despues, x=columna, y='Cantidad', template=plantilla, color_discrete_sequence=['#f72585'])
                fig2.update_layout(title_text=f"DESPUÉS: {columna} (Imputado)", title_x=0.5, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=40, b=0, l=0, r=0), height=350, dragmode='pan')
                st.plotly_chart(fig2, use_container_width=True, config=config_plotly)

        # Pestañas para cargar los gráficos solo si el usuario los pide
        tab_cat1, tab_cat2, tab_cat3 = st.tabs(["Pie Hábil", "Nacionalidad", "Liga Actual"])
        with tab_cat1: render_categorica_plotly('pie_habil')
        with tab_cat2: render_categorica_plotly('nacionalidad')
        with tab_cat3: render_categorica_plotly('liga_actual')


        # ====================================================================
        # 2. IMPUTACIÓN DE VARIABLES NUMÉRICAS (MEDIANA VS KNN)
        # ====================================================================

        with st.spinner('Calculando imputaciones numéricas (Mediana y KNN)...'):
            cols_imputar_num = ['edad_al_momento', 'mes_de_nacimiento', 'altura_cm', 'dias_para_fin_contrato']
            df_missing = df_futbol[cols_imputar_num].copy().apply(pd.to_numeric, errors='coerce')
            
            # Método A: Mediana
            imputer_mediana = SimpleImputer(strategy='median')
            df_mediana = pd.DataFrame(imputer_mediana.fit_transform(df_missing), columns=cols_imputar_num)
            
            # Método B: KNN Imputer
            imputer_knn = KNNImputer(n_neighbors=5)
            df_knn = pd.DataFrame(imputer_knn.fit_transform(df_missing), columns=cols_imputar_num)

            # --- TABLAS COMPARATIVAS NATIVAS ---
            st.markdown("<h5 style='text-align: center; color: #4cc9f0;'>Tablas Descriptivas (Describe)</h5>", unsafe_allow_html=True)
            
            col_t1, col_t2 = st.columns(2)
            col_t3, col_t4 = st.columns(2)
            columnas_grid = [col_t1, col_t2, col_t3, col_t4]
            
            for idx, col in enumerate(cols_imputar_num):
                with columnas_grid[idx]:
                    st.markdown(f"<h6 style='color: #00e5ff; text-align: center;'>Variable: {col}</h6>", unsafe_allow_html=True)
                    comp_df = pd.DataFrame({
                        'Original (NAs)': df_missing[col].describe(),
                        'Mediana': df_mediana[col].describe(),
                        'KNN': df_knn[col].describe()
                    })
                    st.dataframe(comp_df.round(2), use_container_width=True)

            # --- GRÁFICOS KDE SUPERPUESTOS (Matplotlib Ultraligero) ---
            st.markdown("<br><h5 style='text-align: center; color: #4cc9f0;'>Impacto en la Distribución (KDE Superpuestos)</h5>", unsafe_allow_html=True)

            @st.fragment
            def graficar_kde_comparativo(columna, titulo):
                plt.style.use('dark_background')
                fig, ax = plt.subplots(figsize=(8, 5))
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)

                sns.kdeplot(data=df_missing[columna].dropna(), fill=True, alpha=0.3, color='#4cc9f0', label='Original', ax=ax)
                sns.kdeplot(data=df_mediana[columna], fill=False, color='#ff4d4d', linewidth=2.5, linestyle='--', label='Mediana', ax=ax)
                sns.kdeplot(data=df_knn[columna], fill=False, color='#00ffcc', linewidth=2.5, linestyle=':', label='KNN', ax=ax)
                
                ax.set_title(titulo, fontsize=12, fontweight='bold', color='#ffffff', pad=10)
                ax.set_xlabel(columna)
                ax.set_ylabel("Densidad")
                ax.legend(fontsize=9, facecolor='none', edgecolor='none', labelcolor='#e0e0e0')
                ax.grid(axis='y', alpha=0.1)

                st.pyplot(fig, transparent=True)
                plt.close(fig)

            col_k1, col_k2 = st.columns(2)
            with col_k1: graficar_kde_comparativo('edad_al_momento', "Distribución de 'edad_al_momento'")
            with col_k2: graficar_kde_comparativo('mes_de_nacimiento', "Distribución de 'mes_de_nacimiento'")
            
            col_k3, col_k4 = st.columns(2)
            with col_k3: graficar_kde_comparativo('altura_cm', "Distribución de 'altura_cm'")
            with col_k4: graficar_kde_comparativo('dias_para_fin_contrato', "Distribución de 'dias_para_fin_contrato'")
           
        st.markdown("<br><hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #ffffff;'>2. Imputación de Variables Numéricas (Comparativa)</h4>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: rgba(15, 20, 30, 0.8); border-left: 4px solid #fca311; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p style="color: #e0e0e0; margin-bottom: 0;">
                <b>Decisión :</b> Se analiza la imputación de las 4 variables numéricas con nulos (<code>edad_al_momento</code>, <code>mes_de_nacimiento</code>, <code>altura_cm</code>, <code>dias_para_fin_contrato</code>). donde claramente KNN es mucho mejor.
            </p>
        </div>
        """, unsafe_allow_html=True) 
        
    with tab4:
        st.markdown("<h3 style='color: #4cc9f0;'> Pruebas de Asociación y Dependencia</h3>", unsafe_allow_html=True)
        st.write("Análisis estadístico basado en las hipótesis del EDA.")

        st.markdown("""
<div style="background-color: rgba(15, 20, 30, 0.8); backdrop-filter: blur(12px); border-radius: 12px; border: 1px solid rgba(247, 37, 133, 0.3); border-left: 5px solid #f72585; padding: 20px; margin-top: 30px;">
<h4 style="color: #ffffff; margin-top: 0; margin-bottom: 15px;">9. Conclusiones Finales del Análisis Exploratorio (EDA)</h4>
<p style="color: #e0e0e0; font-size: 0.95rem;">Conclusiones:</p>

<ul style="color: #e0e0e0; font-size: 0.95rem; line-height: 1.6;">
<li style="margin-bottom: 12px;"><strong style="color: #00e5ff;">La "Inercia" del Mercado:</strong> La correlación de Spearman confirma la Hipótesis 1. El <code>valor_maximo_historico_previo</code> es, con muchísima diferencia, el mejor predictor numérico del valor de un jugador (0.82). Por lo tanto el estatus previo de un jugador amortigua las caídas de precio frente a un mal rendimiento reciente o posterior.</li>

<li style="margin-bottom: 12px;"><strong style="color: #00e5ff;">Regularidad vs. Explosividad:</strong> variables de volumen de juego (<code>partidos_jugados_12m</code>, <code>minutos_jugados_12m</code> con ~0.52) tienen mayor correlación con el precio que las variables asociadas al rendimiento en el terreno de juego (<code>goles_12m</code>, <code>asistencias_12m</code> con ~0.45). El mercado valora más la constancia física que actuaciones destacadas puntuales.</li>

<li style="margin-bottom: 12px;"><strong style="color: #00e5ff;">Desmitificación de variables físicas y demográficas:</strong> Atributos como la <code>altura_cm</code> (-0.04) o el <code>mes_de_nacimiento</code> (0.02) son irrelevantes a la hora de explicar la varianza del precio, descartando efectos como el sesgo de edad relativa (NFL).</li>

<li><strong style="color: #00e5ff;">El Contexto como Multiplicador del Valor:</strong> La prueba de Kruskal-Wallis arrojó un p-valor de 0.0 para todas las variables categóricas (<code>liga_actual</code>, <code>nacionalidad</code>, <code>posicion_principal</code>). Esto valida la Hipótesis 3: el valor de un jugador está fuertemente segmentado por la jerarquía económica de la liga en la que juega y posiblemente la escasez táctica de su rol.</li>
</ul>
</div>
""", unsafe_allow_html=True)
            
            

            
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 7. SECCIÓN: AJEDREZ (CLASIFICACIÓN Y TÁCTICA)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
elif selected == "Ajedrez (Clasificación)":
    import numpy as np
    import re # Necesario para el nuevo filtro de temas
    
    # 1. PREPARACIÓN DE DATOS BASE Y FEATURE ENGINEERING
    if "ajedrez_df" not in st.session_state:
        st.session_state["ajedrez_df"] = pd.DataFrame()
        
    # Recreamos la variable objetivo categórica
    bins = [float('-inf'), 1200, 1800, 2400, float('inf')]
    labels = ['Principiante', 'Intermedio', 'Avanzado', 'Maestro']
    df_ajedrez['nivel_dificultad'] = pd.cut(df_ajedrez['Rating'], bins=bins, labels=labels, right=False)
    
    # Feature Engineering del PDF
    if 'Moves' in df_ajedrez.columns and 'num_movimientos' not in df_ajedrez.columns:
        df_ajedrez['num_movimientos'] = df_ajedrez['Moves'].str.split().str.len()
    if 'Themes' in df_ajedrez.columns and 'num_temas' not in df_ajedrez.columns:
        df_ajedrez['num_temas'] = df_ajedrez['Themes'].str.split().str.len()

    # Definir columnas numéricas dinámicamente
    cols_esperadas = ['Rating', 'RatingDeviation', 'Popularity', 'NbPlays', 'num_movimientos', 'num_temas', 
                      'branching_factor', 'forcing_index', 'graph_density', 'tension_components', 
                      'spatial_entropy', 'com_chebyshev_dist']
    num_cols_ajedrez = [col for col in cols_esperadas if col in df_ajedrez.columns]

    st.markdown("""<div style="font-size: 2.8rem; font-weight: bold; line-height: 1.2; color: #FFFFFF; 
                text-shadow: 2px 2px 8px #000000, 0px 0px 20px #000000; margin-bottom: 10px;"><i class="bi bi-puzzle" 
                style="color: #FFFFFF; margin-right: 10px;"></i> Explorador Táctico Lichess</div>""", unsafe_allow_html=True)
    st.markdown("<p>Clasificación de dificultad cognitiva y renderizado de posiciones tácticas.</p>", unsafe_allow_html=True)
    
    # --- KPIs PRINCIPALES ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(crear_tarjeta("bi bi-database", "Muestra Global", f"{len(df_ajedrez):,}"), unsafe_allow_html=True)
    with c2: st.markdown(crear_tarjeta("bi bi-graph-up", "Rating Medio", f"{df_ajedrez['Rating'].mean():.0f}"), unsafe_allow_html=True)
    with c3: st.markdown(crear_tarjeta("bi bi-fire", "Popularidad Media", f"{df_ajedrez['Popularity'].mean():.1f}"), unsafe_allow_html=True)
    with c4: st.markdown(crear_tarjeta("bi bi-play-circle", "Total Jugadas", f"{df_ajedrez['NbPlays'].sum():,}"), unsafe_allow_html=True)

    st.write("")
    
    # =========================================================
    # NAVEGACIÓN POR PESTAÑAS (Fluidez Instantánea)
    # =========================================================
    tab1_a, tab_eda_a, tab2_a, tab3_a, tab4_a = st.tabs([
        "Estadísticas Descriptivas", 
        "Análisis Exploratorio (EDA)", 
        "Gráficos y Tableros", 
        "Imputación", 
        "Pruebas Estadísticas"
    ])

    # ---------------------------------------------------------
    # PESTAÑA 1: ESTADÍSTICAS DESCRIPTIVAS
    # ---------------------------------------------------------
    with tab1_a:
        st.markdown("<h3 style='color: #4cc9f0;'> Base de Datos (Muestra)</h3>", unsafe_allow_html=True)
        st.dataframe(df_ajedrez.head(100).style.set_properties(**{'text-align': 'center'}), use_container_width=True)
        
        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #4cc9f0;'> Estadísticas Descriptivas</h3>", unsafe_allow_html=True)
        
        desc_a = df_ajedrez[num_cols_ajedrez].describe().T
        desc_a['mediana'] = df_ajedrez[num_cols_ajedrez].median()
        desc_a = desc_a[['mean', 'mediana', 'std', 'min', 'max']].rename(columns={'mean': 'Promedio', 'std': 'Desv. Est.', 'min': 'Mínimo', 'max':'Máximo', 'mediana':'Mediana'})
        st.dataframe(desc_a.style.format("{:.2f}").set_properties(**{'text-align': 'center'}), use_container_width=True)
        
        st.markdown("<br><hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #4cc9f0;'> Distribución de Nivel de Dificultad</h3>", unsafe_allow_html=True)
        
        conteo_clases = df_ajedrez['nivel_dificultad'].value_counts(normalize=True) * 100
        st.markdown(f"""
        <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px); border-radius: 15px; border: 1px solid rgba(188, 19, 254, 0.3); padding: 20px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #e0e0e0;">Principiante:</span><strong style="color: #00e5ff;">{conteo_clases.get('Principiante', 0):.2f}%</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #e0e0e0;">Intermedio:</span><strong style="color: #4cc9f0;">{conteo_clases.get('Intermedio', 0):.2f}%</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #e0e0e0;">Avanzado:</span><strong style="color: #f72585;">{conteo_clases.get('Avanzado', 0):.2f}%</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #e0e0e0;">Maestro:</span><strong style="color: #7209b7;">{conteo_clases.get('Maestro', 0):.2f}%</strong>
            </div>
            <p style="font-size: 0.75rem; color: #8b949e; margin-top: 15px; margin-bottom: 0;">*Desbalance hacia Maestro típico de la curva ELO.</p>
        </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # PESTAÑA EDA: ANÁLISIS EXPLORATORIO
    # ---------------------------------------------------------
    with tab_eda_a:
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Análisis Exploratorio (EDA) - Ajedrez</h3>", unsafe_allow_html=True)
        
        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #ffffff; text-align: center;'>1. Distribuciones (Variables Numéricas)</h4>", unsafe_allow_html=True)
        
        cols_por_fila_hist = 3
        for i in range(0, len(num_cols_ajedrez), cols_por_fila_hist):
            cols_hist = st.columns(cols_por_fila_hist)
            for j in range(cols_por_fila_hist):
                if i + j < len(num_cols_ajedrez):
                    var_name = num_cols_ajedrez[i+j]
                    with cols_hist[j]:
                        st.markdown(f"<p style='text-align:center; color:#34e3fa; font-weight:bold; margin-bottom:0;'>{var_name}</p>", unsafe_allow_html=True)
                        data_clean = df_ajedrez[var_name].dropna()
                        counts, bins = np.histogram(data_clean, bins=30)
                        hist_df = pd.DataFrame({'Frecuencia': counts}, index=np.round((bins[:-1] + bins[1:]) / 2, 2))
                        st.bar_chart(hist_df, color="#33b6f3", height=200)

        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #ffffff; text-align: center;'>2. Detección de Outliers (IQR)</h4>", unsafe_allow_html=True)
        
        outliers_data = []
        for col in num_cols_ajedrez:
            Q1 = df_ajedrez[col].quantile(0.25)
            Q3 = df_ajedrez[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers_count = len(df_ajedrez[(df_ajedrez[col] < lower) | (df_ajedrez[col] > upper)])
            outliers_data.append({
                "Variable": col,
                "Outliers Detectados": outliers_count,
                "Porcentaje (%)": f"{(outliers_count / len(df_ajedrez)) * 100:.2f}%"
            })
            
        df_outliers = pd.DataFrame(outliers_data)
        st.dataframe(df_outliers.style.set_properties(**{'background-color': 'rgba(15, 20, 30, 0.6)', 'text-align': 'center'}), use_container_width=True)

        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #ffffff; text-align: center;'>3. Variables vs Nivel de Dificultad</h4>", unsafe_allow_html=True)
        
        @st.fragment
        def renderizar_boxplots_ajedrez():
            import matplotlib.pyplot as plt
            import seaborn as sns
            import math
            
            plt.style.use('dark_background')
            n_vars = len(num_cols_ajedrez)
            n_rows = math.ceil(n_vars / 3)
            
            fig_bx, axes_bx = plt.subplots(n_rows, 3, figsize=(18, n_rows * 4))
            fig_bx.patch.set_alpha(0.0) 
            axes_bx = axes_bx.flatten()
            
            paleta_cyber = ['#00e5ff', '#4cc9f0', '#f72585', '#7209b7']
            flierprops_a = dict(marker='o', markerfacecolor='white', markeredgecolor='none', alpha=0.1, markersize=2)
            
            for idx, col in enumerate(num_cols_ajedrez):
                sns.boxplot(data=df_ajedrez, x='nivel_dificultad', y=col, ax=axes_bx[idx], palette=paleta_cyber, flierprops=flierprops_a)
                axes_bx[idx].patch.set_alpha(0.0)
                axes_bx[idx].set_title(f"{col} por Dificultad", color='#ffffff', fontsize=11, pad=10)
                axes_bx[idx].set_xlabel("")
                axes_bx[idx].set_ylabel("")
                axes_bx[idx].tick_params(colors='#8b949e', labelsize=8)
                for spine in axes_bx[idx].spines.values():
                    spine.set_color((1.0, 1.0, 1.0, 0.2))
            
            for j in range(len(num_cols_ajedrez), len(axes_bx)):
                axes_bx[j].set_visible(False)
                
            plt.tight_layout(pad=3.0)
            st.pyplot(fig_bx, transparent=True)
            plt.close(fig_bx)

        with st.spinner("Generando Matriz de Boxplots..."):
            renderizar_boxplots_ajedrez()

        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #ffffff; text-align: center;'>4. Matriz de Correlación</h4>", unsafe_allow_html=True)
        
        corr_matrix_a = df_ajedrez[num_cols_ajedrez].corr()
        fig_corr_a = px.imshow(corr_matrix_a, text_auto=".2f", aspect="auto", color_continuous_scale=[[0, "#2bfdf3"], [0.5, "#0954b7"], [1, "#4813c5"]])
        fig_corr_a.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=600, margin=dict(t=20))
        st.plotly_chart(fig_corr_a, use_container_width=True, config={'displayModeBar': False})

    # ---------------------------------------------------------
    # PESTAÑA 3: PUZZLES TÁCTICOS Y TEORÍA MATEMÁTICA
    # ---------------------------------------------------------
    with tab2_a:
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Fundamentación Matemática y Modelado Topológico</h3>", unsafe_allow_html=True)
        
        # --- TEORÍA MATEMÁTICA ---
        with st.expander("📖 Ver Teoría: De la Geometría a la Teoría de Grafos", expanded=False):
            
            # EL SECRETO ESTÁ AQUÍ: Usamos r""" (Raw String) y Markdown puro (nada de <ul> o <li>)
            st.markdown(r"""
<div style="background-color: rgba(15, 20, 30, 0.8); backdrop-filter: blur(12px); border-radius: 12px; border-left: 5px solid #f72585; padding: 20px; margin-bottom: 20px;">
Dada la naturaleza del problema, es fundamental formalizar de alguna manera algunos de los datos que acabamos de extraer:

<h5 style="color: #4cc9f0; margin-top: 25px;">1. Variables Combinatorias y Espacio de Estados</h5>

Sea $S$ un estado válido del tablero de ajedrez (codificado por su FEN). Definimos $M(S) = \{m_1, m_2, \dots, m_n\}$ como el conjunto finito de todos los movimientos posibles (legales)  desde el estado $S$.

* <strong style="color: #00e5ff;">Factor de Ramificación (Branching Factor, $b$):</strong><br>
Es simplemente la cardinalidad del conjunto de movimientos legales:

$$b = |M(S)|$$

* <strong style="color: #00e5ff;">Índice de Forzamiento (Forcing Index, $I_f$):</strong><br>
Sea $M_F(S) \subseteq M(S)$ el subconjunto de movimientos que alteran drásticamente el estado material o que restringen considerablemente el espacio de estados del oponente (específicamente, jaques y capturas). Definimos el Índice de Forzamiento como una medida de probabilidad uniforme:
$$I_f = \frac{|M_F(S)|}{|M(S)|}$$
<em style="color: #8b949e;"> Interpretación: Si $I_f \to 1$, el árbol de cálculo es determinista y fácil. Si $I_f \to 0$, el problema es "combinatorio" y exige buscar juagadas mas "abstractas".</em>

<h5 style="color: #4cc9f0; Teoría de Grafos</h5>

Modelamos la interacción de las piezas como un grafo dirigido $G = (V, E)$.<br>
Sea $V$ el conjunto de casillas ocupadas en el tablero, es decir, $v_i \in V$ si y solo si la masa en la casilla $i$ es $m(v_i) > 0$.<br>
Sea $E$ el conjunto de aristas dirigidas, donde $(v_i, v_j) \in E$ si la pieza en $v_i$ ejerce una (pseudo-legalidad) de ataque o defensa sobre la casilla $v_j$.

* <strong style="color: #00e5ff;">Densidad del Grafo (Graph Density, $D$):</strong><br>
Mide la saturación de las interacciones frente al máximo posible en un grafo dirigido simple.
$$D = \frac{|E|}{|V|(|V| - 1)}$$
<em style="color: #8b949e;">Interpretación: Una densidad alta implica una posición "densa", con piezas fuertemente entrelazadas.</em>

* <strong style="color: #00e5ff;">Componentes de "Tensión" ($k$):</strong><br>
Corresponde al número de componentes débilmente conexas del grafo $G$. Si ignoramos la direccionalidad de las aristas, particionamos $V$ en clases de equivalencia.<br>
<em style="color: #8b949e;">Interpretación: Si $k = 1$, toda la tensión está centralizada. Si $k \ge 2$, existen múltiples mini-batallas locales e independientes, dificl de ver para el humano.</em>

<h5 style="color: #4cc9f0; margin-top: 25px;">3. Teoría de la Información (Entropía Espacial)</h5>

Evaluamos la distribución de la "masa" (valor material de las piezas, $m(v)$) sobre la geometría del tablero.<br>
Particionamos el tablero en cuatro conjuntos mutuamente excluyentes (los cuadrantes): $Q = \{Q_1, Q_2, Q_3, Q_4\}$.<br>
Definimos la masa total $M_T = \sum_{v \in V} m(v)$ y la masa por cuadrante $M_j = \sum_{v \in Q_j} m(v)$. Esto nos permite inducir una función de masa de probabilidad:
$$p_j = \frac{M_j}{M_T}$$

* <strong style="color: #00e5ff;">Entropía Espacial ($H_S$):</strong><br>
Calculamos la entropía de Shannon de esta distribución discreta:
$$H_S = - \sum_{j=1}^{4} p_j \ln(p_j)$$
<em style="color: #8b949e;">Interpretación: Si $H_S \to 0$, la batalla está altamente "localizada". Si $H_S$ es máxima ($\approx 1.386$), las piezas están distribuidas uniformemente en todo el tablero, exigiendo una visión periférica completa del tablero.</em>

<h5 style="color: #4cc9f0; margin-top: 25px;">4. Mecánica Clásica y Geometría Métrica</h5>

Asignamos a cada casilla $v \in V$ un vector de coordenadas afines $\vec{c}(v) = (x_v, y_v)$ en el espacio $\mathbb{R}^2$, con $x_v, y_v \in \{0, 1, \dots, 7\}$.<br>
Particionamos $V$ en $V_w$ (piezas blancas) y $V_b$ (piezas negras).

* <strong style="color: #00e5ff;">Distancia de Chebyshev entre Centros de Masa ($d_C$):</strong><br>
Primero, calculamos el vector centro de masa para cada bando:
$$\vec{C}_w = \frac{1}{\sum_{v \in V_w} m(v)} \sum_{v \in V_w} m(v) \vec{c}(v)$$,
$$\vec{C}_b = \frac{1}{\sum_{v \in V_b} m(v)} \sum_{v \in V_b} m(v) \vec{c}(v)$$
Dado el Rey en el ajedrez se rige por la norma del supremo ($L_\infty$), se usa la métrica de Chebyshev. Medimos la distancia geométrica como:
$$d_C = \|\vec{C}_w - \vec{C}_b\|_\infty = \max(|C_{w,x} - C_{b,x}|, |C_{w,y} - C_{b,y}|)$$
<em style="color: #8b949e;">Interpretación: Esta variable mapea si el estado del juego corresponde a un "cuerpo a cuerpo" ($d_C$ pequeña) o una guerra táctica a larga distancia ($d_C$ grande) Alfiles por ejemplo.</em>
</div>
            """, unsafe_allow_html=True)

        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Renderizado de Puzzles Tácticos</h3>", unsafe_allow_html=True)

        # LA MAGIA ESTÁ AQUÍ: Toda la lógica de interacción está dentro de un fragmento
        @st.fragment
        def aplicacion_puzzles_aislada():
            with st.expander("[ Configuración del Motor Gráfico ]", expanded=True):
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    estilo_tablero = st.selectbox("Tablero", ["brown", "burled_wood", "marble", "green", "blue", "newspaper", "purple", "tournament"], key="sb_board")
                    estilo_piezas = st.selectbox("Piezas", ["neo", "alpha", "glass", "vintage", "classic", "modern", "space", "wood"], key="sb_pieces")
                with col_f2:
                    rating_min, rating_max = st.slider("Dificultad (Elo):", 600, 3000, (1200, 2200), 50, key="sl_rating")
                with col_f3:
                    temas_comunes = ['mate', 'fork', 'pin', 'crushing', 'endgame', 'middlegame', 'sacrifice', 'advantage']
                    temas_seleccionados = st.multiselect("Temas (Opcional)", sorted(temas_comunes), key="ms_temas")
                    limite_a = st.number_input("Cantidad a renderizar:", 1, 40, 4, key="lim_a")

            col_btn1, col_btn2 = st.columns([4, 1])
            with col_btn1:
                # Este botón AHORA solo recarga este fragmento, no el resto de la app
                btn_consultar_ajedrez = st.button(" Renderizar Tableros", type="primary", use_container_width=True, key="btn_a")
            with col_btn2:
                if st.button("🗑️ Limpiar", use_container_width=True):
                    if os.path.exists(session_temp_dir):
                        shutil.rmtree(session_temp_dir)
                        os.makedirs(session_temp_dir, exist_ok=True)
                        st.session_state.ajedrez_df = pd.DataFrame()
                        st.rerun(scope="fragment") # Recarga solo el fragmento al limpiar

            if btn_consultar_ajedrez:
                with st.spinner("Buscando y renderizando posiciones tácticas..."):
                    try:
                        mask = (df_ajedrez['Rating'] >= rating_min) & (df_ajedrez['Rating'] <= rating_max)
                        
                        if temas_seleccionados:
                            # --- CAMBIO: Filtro "Y" (AND) en lugar de "O" (OR) ---
                            # Creamos una máscara individual para cada tema y las multiplicamos (intersección lógica)
                            for tema in temas_seleccionados:
                                # Escapamos el tema por si acaso y lo buscamos en toda la columna
                                mask = mask & df_ajedrez['Themes'].str.contains(re.escape(tema), case=False, na=False)
                        
                        df_temp = df_ajedrez[mask].head(limite_a)
                        
                        if df_temp.empty:
                            st.warning("⚠️ No se encontraron puzzles que cumplan con TODOS los temas seleccionados y en ese rango de ELO. Intenta reducir los temas o ampliar el ELO.")
                        else:
                            st.session_state.ajedrez_df = df_temp
                            
                            for k in list(st.session_state.keys()):
                                if k.startswith("paso_"): del st.session_state[k]
                            
                            for _, r in df_temp.iterrows():
                                board = chess.Board(r['FEN'])
                                flip_needed = (board.turn == chess.WHITE)
                                tag_v = "flipped" if flip_needed else "normal"
                                nombre_base = f"{r['PuzzleId']}_{estilo_tablero}_{estilo_piezas}_{tag_v}"
                                generate_puzzle_image(f"{nombre_base}_step0", board.fen(), session_temp_dir, estilo_tablero, estilo_piezas, flip=flip_needed)
                                
                                movs_list = str(r['Moves']).split(" ")
                                for j, m in enumerate(movs_list):
                                    board.push_uci(m)
                                    generate_puzzle_image(f"{nombre_base}_step{j+1}", board.fen(), session_temp_dir, estilo_tablero, estilo_piezas, flip=flip_needed)
                    except Exception as e:
                        st.error(f"Error renderizando: {e}")

            # DIBUJAR LOS TABLEROS OBTENIDOS
            df_actual = st.session_state.get("ajedrez_df", pd.DataFrame())
            if not df_actual.empty:
                cols_por_fila = 4
                for i in range(0, len(df_actual), cols_por_fila):
                    cols = st.columns(cols_por_fila)
                    for j in range(cols_por_fila):
                        if i + j < len(df_actual):
                            with cols[j]:
                                renderizar_tarjeta_puzzle(df_actual.iloc[i+j], estilo_tablero, estilo_piezas, session_temp_dir)

        # FUNCIÓN DE CADA TARJETA (Fragmento anidado para controles de paso)
        @st.fragment
        def renderizar_tarjeta_puzzle(row, tablero_estilo, piezas_estilo, tmp_dir):
            p_id = row['PuzzleId']
            movs = str(row['Moves']).split(" ")
            b_inicial = chess.Board(row['FEN'])
            debe_flipear = (b_inicial.turn == chess.WHITE) 
            v_tag = "flipped" if debe_flipear else "normal"
            
            s_key = f"paso_{p_id}"
            if s_key not in st.session_state:
                st.session_state[s_key] = 0
            
            paso = st.session_state[s_key]
            nombre_img = f"{p_id}_{tablero_estilo}_{piezas_estilo}_{v_tag}_step{paso}"
            path_img = os.path.join(tmp_dir, f"{nombre_img}.png")
            
            if os.path.exists(path_img):
                st.image(path_img, use_container_width=True)
            
            if paso == 0:
                st.markdown(f"<div style='text-align:center; color:#4cc9f0; font-weight:bold;'>Posición Inicial</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center; color:#00e5ff;'>Paso {paso}/{len(movs)}: <b style='color: white;'>{movs[paso-1]}</b></div>", unsafe_allow_html=True)
            
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
            
            st.caption(f"**Elo:** {row['Rating']} | **Temas:** {str(row['Themes']).split(' ')[0]}")
            st.divider()

        # EJECUTAR EL FRAGMENTO PRINCIPAL DE LA PESTAÑA
        aplicacion_puzzles_aislada()


    # ---------------------------------------------------------
    # PESTAÑA 4: IMPUTACIÓN
    # ---------------------------------------------------------
    with tab3_a:
        st.markdown("<h3 style='color: #4cc9f0;'> Tratamiento de Datos Faltantes (Lichess)</h3>", unsafe_allow_html=True)
        st.write("Análisis de integridad estructural de la base de datos de Lichess:")
        
        st.markdown("""
        <div style="background-color: rgba(0, 229, 255, 0.05); backdrop-filter: blur(12px); border-radius: 10px; border: 1px solid rgba(0, 229, 255, 0.3); border-left: 4px solid #00e5ff; padding: 15px; margin-bottom: 20px;">
            <h5 style='color: #00e5ff; margin-top:0;'><i class='bi bi-shield-check'></i> Integridad del Dataset Original</h5>
            <p style='font-size: 0.95rem; color: #e0e0e0; margin-bottom:0;'>
            A diferencia de bases de datos generadas manualmente (como los historiales médicos o financieros), la base de datos de Lichess es generada automáticamente por el motor <b>Stockfish 16</b> a partir de partidas digitales. Por la naturaleza de la extracción de datos desde el formato FEN y PGN, <b>no existen valores nulos</b> en las variables core del problema (Rating, Moves, FEN, Themes).
            </p>
        </div>
        """, unsafe_allow_html=True)

        nulos_ajedrez = pd.DataFrame({
            "Variable": ['PuzzleId', 'FEN', 'Moves', 'Rating', 'Themes', 'Popularity', 'NbPlays'],
            "Valores Faltantes": [0, 0, 0, 0, 0, 0, 0],
            "Porcentaje (%)": ["0.0%", "0.0%", "0.0%", "0.0%", "0.0%", "0.0%", "0.0%"]
        })
        st.dataframe(nulos_ajedrez.style.set_properties(**{'text-align': 'center'}), use_container_width=True)

    # ---------------------------------------------------------
    # PESTAÑA 5: PRUEBAS ESTADÍSTICAS
    # ---------------------------------------------------------
    with tab4_a:
        st.markdown("""
            <style>
            .card-cyber { background-color: rgba(15, 20, 30, 0.6); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; backdrop-filter: blur(12px); }
            .accent-purple { border-left: 5px solid #f72585; }
            .title-test-p { color: #f72585; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.8rem; }
            .text-stats-p { color: #e0e0e0; font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 5px;}
            .val-stats-p { color: #ffffff; font-weight: bold; float: right; }
            .badge-rel-p { background-color: rgba(247, 37, 133, 0.2); color: #f72585; padding: 5px; border-radius: 5px; font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px; border: 1px solid #f72585; display: block; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Conclusiones Finales del Análisis Exploratorio (EDA)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8b949e; margin-bottom: 30px;'>Tras evaluar la dependencia de las variables numéricas con la variable objetivo categórica (nivel_dificultad), se concluye lo siguiente:</p>", unsafe_allow_html=True)

        st.markdown("""
            <div class="card-cyber accent-purple">
                <div class="title-test-p"><i class="bi bi-bar-chart-fill"></i> Significancia Estadística Generalizada</div>
                <p style="font-size: 0.95rem; color: #e0e0e0; line-height: 1.5;">La prueba de Kruskal-Wallis rechaza contundentemente la hipótesis nula para todas las variables numéricas evaluadas (<code>RatingDeviation</code>, <code>Popularity</code>, <code>NbPlays</code>, <code>num_movimientos</code>, <code>num_temas</code>, <code>branching_factor</code>, <code>forcing_index</code>, <code>graph_density</code>, <code>tension_components</code>, <code>spatial_entropy</code>, <code>com_chebyshev_dist</code>), arrojando p-valores de <strong>0.0</strong>.</p>
            </div>
            
            <div class="card-cyber accent-purple">
                <div class="title-test-p"><i class="bi bi-bounding-box-circles"></i> Validación del Feature Engineering Topológico y Combinatorio</div>
                <p style="font-size: 0.95rem; color: #e0e0e0; line-height: 1.5;">El rechazo de H0 en las nuevas variables confirma la hipótesis central del proyecto: <strong>la dificultad cognitiva de un puzzle no solo depende de su longitud (num_movimientos), sino de la disposición física del tablero.</strong></p>
            </div>
            
            <div class="card-cyber accent-purple">
                <div class="title-test-p"><i class="bi bi-bezier2"></i> Naturaleza No Lineal del Problema</div>
                <p style="font-size: 0.95rem; color: #e0e0e0; line-height: 1.5;">Aunque la matriz de correlación de Pearson arrojó coeficientes bajos para las variables espaciales y de grafos, el test de Kruskal-Wallis demostró una dependencia absoluta. Esto evidencia que <strong>la relación entre la geometría del tablero y la dificultad percibida es altamente no lineal.</strong></p>
                <div class="badge-rel-p">✅ JUSTIFICA EL USO DE MODELOS BASADOS EN ÁRBOLES (RF/XGBoost)</div>
            </div>
        """, unsafe_allow_html=True)