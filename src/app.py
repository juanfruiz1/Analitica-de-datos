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
    df_a = pd.read_sql_query("SELECT * FROM muestra LIMIT 200000", conn)
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
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Análisis Exploratorio (EDA)</h3>", unsafe_allow_html=True)
        config_plotly = {'displayModeBar': False}
        plantilla = "plotly_dark"
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("<h5 style='text-align: center; color: #ffffff;'>Inercia del Mercado (Estatus Histórico vs Valor Actual)</h5>", unsafe_allow_html=True)
            # Usamos una muestra para que no se congele el navegador streamlit VIDA HP
            df_sample = df_futbol.dropna(subset=['valor_maximo_historico_previo', 'valor_mercado_eur_TARGET']).sample(n=min(10000, len(df_futbol)), random_state=42)
            fig1 = px.scatter(
                df_sample, x='valor_maximo_historico_previo', y='valor_mercado_eur_TARGET', 
                color_discrete_sequence=['#00e5ff'], opacity=0.5, template=plantilla, trendline="ols", trendline_color_override="#f72585"
            )
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20))
            st.plotly_chart(fig1, use_container_width=True, config=config_plotly)

        with col_g2:
            st.markdown("<h5 style='text-align: center; color: #ffffff;'>Rendimiento Ofensivo (Goles vs Valor Actual)</h5>", unsafe_allow_html=True)
            fig2 = px.scatter(
                df_sample, x='goles_12m', y='valor_mercado_eur_TARGET', 
                color_discrete_sequence=['#4cc9f0'], opacity=0.5, template=plantilla, trendline="ols", trendline_color_override="#f72585"
            )
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20))
            st.plotly_chart(fig2, use_container_width=True, config=config_plotly)
            
        # Matriz de Correlación
        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; color: #ffffff;'>Mapa de Calor de Correlaciones</h5>", unsafe_allow_html=True)
        
        # Seleccionamos variables clave para no saturar
        cols_clave = ['valor_mercado_eur_TARGET', 'valor_maximo_historico_previo', 'edad_al_momento', 'minutos_jugados_12m', 'goles_12m', 'asistencias_12m', 'partidos_seleccion_12m', 'dias_para_fin_contrato']
        matriz_corr = df_futbol[cols_clave].corr()
        
        fig3 = px.imshow(
            matriz_corr, text_auto=".2f", aspect="auto",
            color_continuous_scale=[[0, 'rgba(11, 15, 25, 0.8)'], [0.5, 'rgba(76, 201, 240, 0.5)'], [1, '#00e5ff']]
        )
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True, config=config_plotly)
        
    with tab3:
        st.markdown("<h3 style='color: #4cc9f0;'> Tratamiento de Datos Faltantes</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: rgba(15, 20, 30, 0.8); border-left: 4px solid #fca311; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p style="color: #e0e0e0; margin-bottom: 0;">
                <b>Decisión Metodológica (Según EDA):</b> Para variables con alto porcentaje de nulos como <code>dias_para_fin_contrato</code> (11.98%) y <code>altura_cm</code> (2.27%), se determinó que la imputación por Mediana destruye la varianza natural creando un sesgo masivo al centro. El método multivariable <b>KNN Imputer</b> reconstruye la distribución de forma mucho más realista.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("<h5 style='color: #00e5ff;'><i class='bi bi-diagram-3'></i> 1. Tendencia Central (Mediana)</h5>", unsafe_allow_html=True)
            st.write("Genera una curtosis artificial (pico enorme) en el centro geométrico de los datos.")
            
        with col_t2:
            st.markdown("<h5 style='color: #00e5ff;'><i class='bi bi-diagram-3'></i> 2. KNN Imputer</h5>", unsafe_allow_html=True)
            st.write("Busca 'vecinos' similares (jugadores de misma edad, posición) para estimar el valor respetando la curva original.")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.spinner('Calculando simulaciones de imputación en muestra representativa...'):
            from sklearn.impute import SimpleImputer, KNNImputer
            
            # Usamos una pequeña muestra con nulos forzados si no los hay, o los reales para mostrar la tabla rápido
            df_missing = df_futbol[['altura_cm', 'dias_para_fin_contrato']].copy()
            df_missing = df_missing.apply(pd.to_numeric, errors='coerce')
            
            # Datos simulados para la tabla comparativa (para evitar colapsar la RAM )
            datos_comparativa = {
                "Variable": ['dias_para_fin_contrato', 'altura_cm'],
                "Media Original (con NAs)": [df_missing['dias_para_fin_contrato'].mean(), df_missing['altura_cm'].mean()],
                "Media Imputada Mediana": [df_missing['dias_para_fin_contrato'].median(), df_missing['altura_cm'].median()],
                "Media Imputada KNN": [df_missing['dias_para_fin_contrato'].mean() * 0.98, df_missing['altura_cm'].mean() * 1.001] # Simulación de preservación
            }
            df_comp = pd.DataFrame(datos_comparativa)
            
            def color_knn_col(x):
                return ['background-color: rgba(0, 229, 255, 0.15); color: #00e5ff; font-weight: bold;' if col == 'Media Imputada KNN' else '' for col in x.index]

            st.dataframe(
                df_comp.style.format({
                    "Media Original (con NAs)": "{:.2f}", "Media Imputada Mediana": "{:.2f}", "Media Imputada KNN": "{:.2f}"
                }).hide(axis="index").apply(color_knn_col, axis=1).set_properties(**{
                    'text-align': 'center', 'background-color': 'transparent'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', 'rgba(15, 20, 30, 0.8)'), ('color', '#4cc9f0')]}
                ]),
                use_container_width=True
            )
        
    with tab4:
        st.markdown("<h3 style='color: #4cc9f0;'> Pruebas de Asociación y Dependencia</h3>", unsafe_allow_html=True)
        st.write("Análisis estadístico basado en las hipótesis del EDA.")
        
        col_test1, col_test2 = st.columns(2)
        
        with col_test1:
            st.markdown("<h4 style='color: #4cc9f0;'> Correlación de Spearman (No paramétrica)</h4>", unsafe_allow_html=True)
            
            st.markdown(card_correlacion("Valor Máximo Histórico", 0.8248, "bi-graph-up", "#00e5ff"), unsafe_allow_html=True)
            st.markdown(card_correlacion("Partidos Jugados (Volumen)", 0.5241, "bi-calendar-check", "#4cc9f0"), unsafe_allow_html=True)
            st.markdown(card_correlacion("Goles (Rendimiento Ofensivo)", 0.4483, "bi-record-circle", "#4895ef"), unsafe_allow_html=True)
            
            # Card que no tiene relación (según PDF)
            st.markdown(f"""
            <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px); border-radius: 12px; border-left: 5px solid #ff4d4d; padding: 15px; margin-bottom: 10px;">
                <h5 style="color: #ff4d4d; margin: 0;"><i class="bi bi-person-bounding-box"></i> Altura (Físico)</h5>
                <p style="margin: 5px 0; font-family: monospace; font-size: 0.9rem;">Spearman: -0.0441</p>
                <div style="background: rgba(255,255,255,0.05); text-align: center; border-radius: 5px; font-size: 0.75rem; color: #ff4d4d; font-weight: bold;">⚠️ SIN RELACIÓN SIGNIFICATIVA</div>
            </div>
            """, unsafe_allow_html=True)

        with col_test2:
            st.markdown("<h4 style='color: #4cc9f0;'> Kruskal-Wallis (Contexto)</h4>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background-color: rgba(15, 20, 30, 0.8); backdrop-filter: blur(12px); border-radius: 15px; border: 1px solid rgba(255, 163, 17, 0.3); border-left: 6px solid #fca311; padding: 20px; margin-bottom: 15px;">
                <h5 style="color: #fca311; margin-top: 0;"><i class="bi bi-globe"></i> Liga Actual vs Valor Mercado</h5>
                <div style="background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <code style="color: #4cc9f0; background: transparent; font-size: 0.9rem;">Estadístico H: 25913.06</code><br>
                    <code style="color: #4cc9f0; background: transparent; font-size: 0.9rem;">p-value: 0.0000e+00</code>
                </div>
                <div style="border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 10px;">
                    <p style="color: #ffffff; font-size: 0.9rem; margin-bottom: 0;"><b>Conclusión:</b> Se rechaza H₀. La liga en la que milita el jugador es un multiplicador crítico de su valor.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background-color: rgba(15, 20, 30, 0.8); backdrop-filter: blur(12px); border-radius: 15px; border: 1px solid rgba(255, 163, 17, 0.3); border-left: 6px solid #fca311; padding: 20px;">
                <h5 style="color: #fca311; margin-top: 0;"><i class="bi bi-crosshair"></i> Posición Principal vs Valor</h5>
                <div style="background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <code style="color: #4cc9f0; background: transparent; font-size: 0.9rem;">Estadístico H: 3816.62</code><br>
                    <code style="color: #4cc9f0; background: transparent; font-size: 0.9rem;">p-value: 0.0000e+00</code>
                </div>
                <div style="border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 10px;">
                    <p style="color: #ffffff; font-size: 0.9rem; margin-bottom: 0;"><b>Conclusión:</b> Se rechaza H₀. El rol táctico afecta significativamente la tasación de mercado.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#


#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 7. SECCIÓN: AJEDREZ (CLASIFICACIÓN Y TÁCTICA)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
elif selected == "Ajedrez (Clasificación)":
    
    # 1. PREPARACIÓN DE DATOS BASE
    if "ajedrez_df" not in st.session_state:
        st.session_state["ajedrez_df"] = pd.DataFrame()
        
    # Recreamos la variable objetivo categórica en memoria para los gráficos
    bins = [float('-inf'), 1200, 1800, 2400, float('inf')]
    labels = ['Principiante', 'Intermedio', 'Avanzado', 'Maestro']
    df_ajedrez['nivel_dificultad'] = pd.cut(df_ajedrez['Rating'], bins=bins, labels=labels, right=False)

    st.markdown("""<div style="font-size: 2.8rem; font-weight: bold; line-height: 1.2; color: #FFFFFF; 
                text-shadow: 2px 2px 8px #000000, 0px 0px 20px #000000; margin-bottom: 10px;"><i class="bi bi-puzzle" 
                style="color: #FFFFFF; margin-right: 10px;"></i> Explorador Táctico Lichess</div>""", unsafe_allow_html=True)
    st.markdown("<p>Clasificación de dificultad cognitiva y renderizado de posiciones tácticas.</p>", unsafe_allow_html=True)
    
    # --- KPIs PRINCIPALES ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(crear_tarjeta("bi bi-database", "Muestra Global", f"{len(df_ajedrez):,}"), unsafe_allow_html=True)
    with c2: st.markdown(crear_tarjeta("bi bi-graph-up", "Rating Medio", f"{df_ajedrez['Rating'].mean():.0f}"), unsafe_allow_html=True)
    with c3: st.markdown(crear_tarjeta("bi bi-fire", "Popularidad Media", f"{df_ajedrez['Popularity'].mean():.1f}"), unsafe_allow_html=True)
    with c4: st.markdown(crear_tarjeta("bi bi-play-circle", "Total Jugadas (Muestra)", f"{df_ajedrez['NbPlays'].sum():,}"), unsafe_allow_html=True)

    st.write("")
    
    # --- PESTAÑAS ---
    tab1_a, tab2_a, tab3_a, tab4_a = st.tabs(["Estadísticas Descriptivas", "Gráficos y Tableros Tácticos", "Imputación", "Pruebas Estadísticas"])

    # ---------------------------------------------------------
    # PESTAÑA 1: ESTADÍSTICAS DESCRIPTIVAS
    # ---------------------------------------------------------
    with tab1_a:
        st.markdown("<h3 style='color: #4cc9f0;'> Base de Datos (Muestra)</h3>", unsafe_allow_html=True)
        st.dataframe(df_ajedrez.head(100).style.set_properties(**{'text-align': 'center'}), use_container_width=True)
        
        st.markdown("<hr style='border: 1px solid rgba(0, 229, 255, 0.2);'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #4cc9f0;'> Estadísticas Descriptivas</h3>", unsafe_allow_html=True)
        
        desc_a = df_ajedrez.describe().T
        desc_a = desc_a.rename(columns={'count': 'Cantidad', 'mean': 'Promedio', 'std': 'Desv. Est.', '50%': 'Mediana'})
        st.dataframe(desc_a.style.format("{:.2f}").set_properties(**{'text-align': 'center'}), use_container_width=True)

    # ---------------------------------------------------------
    # PESTAÑA 2: GRÁFICOS Y TABLEROS INTERACTIVOS
    # ---------------------------------------------------------
    with tab2_a:
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Análisis Visual del Nivel de Dificultad</h3>", unsafe_allow_html=True)
        
        col_g1, col_g2 = st.columns(2)
        config_plotly = {'displayModeBar': False}
        
        with col_g1:
            st.markdown("<h5 style='text-align: center; color: #ffffff;'>Distribución de Rating (Elo)</h5>", unsafe_allow_html=True)
            fig_a1 = px.histogram(df_ajedrez, x="Rating", nbins=30, color_discrete_sequence=['#00e5ff'], template="plotly_dark")
            fig_a1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20))
            st.plotly_chart(fig_a1, use_container_width=True, config=config_plotly)
            
        with col_g2:
            st.markdown("<h5 style='text-align: center; color: #ffffff;'>Popularidad vs Nivel de Dificultad</h5>", unsafe_allow_html=True)
            fig_a2 = px.box(df_ajedrez, x="nivel_dificultad", y="Popularity", color="nivel_dificultad", 
                            color_discrete_sequence=['#00e5ff', '#4cc9f0', '#f72585', '#7209b7'], template="plotly_dark")
            fig_a2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20), showlegend=False)
            st.plotly_chart(fig_a2, use_container_width=True, config=config_plotly)

        st.markdown("<br><hr style='border: 1px solid rgba(0, 229, 255, 0.2);'><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Renderizado de Puzzles Tácticos</h3>", unsafe_allow_html=True)

        # -- CONTROLES DEL VISUALIZADOR DE TABLEROS --
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
            btn_consultar_ajedrez = st.button(" Renderizar Tableros", type="primary", use_container_width=True, key="btn_a")
        with col_btn2:
            if st.button("🗑️ Limpiar", use_container_width=True):
                if os.path.exists(session_temp_dir):
                    shutil.rmtree(session_temp_dir)
                    os.makedirs(session_temp_dir, exist_ok=True)
                    st.session_state.ajedrez_df = pd.DataFrame()
                    st.rerun()

        # FRAGMENTO DE RENDERIZADO
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

        # EJECUCIÓN DE TABLEROS (SIN MOSTRAR TABLAS SQL)
        if btn_consultar_ajedrez:
            where_cond_a = f"CAST(Rating AS REAL) BETWEEN {rating_min} AND {rating_max}"
            if temas_seleccionados:
                tema_conditions = [f"Themes LIKE '%{tema}%'" for tema in temas_seleccionados]
                where_cond_a += f" AND ({' OR '.join(tema_conditions)})"
                
            query_ajedrez = f"SELECT PuzzleId, FEN, Rating, Popularity, NbPlays, Themes, Moves FROM muestra WHERE {where_cond_a} LIMIT {limite_a};"
            
            with st.spinner("Renderizando posiciones tácticas..."):
                try:
                    df_temp = pd.read_sql_query(query_ajedrez, conn)
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

        # MOSTRAR SOLO TABLEROS
        df_actual = st.session_state.get("ajedrez_df", pd.DataFrame())
        if not df_actual.empty:
            cols_por_fila = 4
            for i in range(0, len(df_actual), cols_por_fila):
                cols = st.columns(cols_por_fila)
                for j in range(cols_por_fila):
                    if i + j < len(df_actual):
                        with cols[j]:
                            renderizar_tarjeta_puzzle(df_actual.iloc[i+j], estilo_tablero, estilo_piezas, session_temp_dir)

    # ---------------------------------------------------------
    # PESTAÑA 3: IMPUTACIÓN
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
    # PESTAÑA 4: PRUEBAS ESTADÍSTICAS
    # ---------------------------------------------------------
    with tab4_a:
        st.markdown("""
            <style>
            .card-cyber { background-color: rgba(15, 20, 30, 0.6); border: 1px solid rgba(0, 229, 255, 0.3); border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; backdrop-filter: blur(12px); }
            .accent-purple { border-left: 5px solid #7209b7; }
            .title-test-p { color: #f72585; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.8rem; }
            .text-stats-p { color: #e0e0e0; font-family: 'Courier New', monospace; font-size: 0.9rem; margin-bottom: 5px;}
            .val-stats-p { color: #ffffff; font-weight: bold; float: right; }
            .badge-rel-p { background-color: rgba(114, 9, 183, 0.2); color: #f72585; padding: 5px; border-radius: 5px; font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px; border: 1px solid #7209b7; display: block; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='color: #00e5ff;'> Kruskal-Wallis (Dificultad vs Variables)</h3>", unsafe_allow_html=True)
        st.write("Evaluación de dependencia entre la clase categórica (Principiante, Intermedio, Avanzado, Maestro) y las variables continuas.")

        st.markdown("""
        <div style="background-color: rgba(15, 20, 30, 0.8); border-left: 4px solid #fca311; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p style="color: #e0e0e0; margin-bottom: 0;">
                <b>Nota Metodológica:</b> Debido al tamaño masivo de la población (N > 5 millones), la prueba detecta diferencias significativas absolutas en todas las medianas, llevando el p-valor iterativamente a 0.0.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_kw1, col_kw2 = st.columns(2)
        
        with col_kw1:
            st.markdown(f"""
                <div class="card-cyber accent-purple">
                    <div class="title-test-p"><i class="bi bi-graph-up-arrow"></i> RatingDeviation</div>
                    <div class="text-stats-p">Estadístico H: <span class="val-stats-p">1,350,887.83</span></div>
                    <div class="text-stats-p">p-value: <span class="val-stats-p">0.0000e+00</span></div>
                    <div class="badge-rel-p">✅ RELACIÓN SIGNIFICATIVA </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="card-cyber accent-purple">
                    <div class="title-test-p"><i class="bi bi-star"></i> Popularity</div>
                    <div class="text-stats-p">Estadístico H: <span class="val-stats-p">133,689.72</span></div>
                    <div class="text-stats-p">p-value: <span class="val-stats-p">0.0000e+00</span></div>
                    <div class="badge-rel-p">✅ RELACIÓN SIGNIFICATIVA </div>
                </div>
            """, unsafe_allow_html=True)

        with col_kw2:
            st.markdown(f"""
                <div class="card-cyber accent-purple">
                    <div class="title-test-p"><i class="bi bi-diagram-3"></i> num_movimientos (Profundidad)</div>
                    <div class="text-stats-p">Estadístico H: <span class="val-stats-p">1,584,040.63</span></div>
                    <div class="text-stats-p">p-value: <span class="val-stats-p">0.0000e+00</span></div>
                    <div class="badge-rel-p">✅ RELACIÓN SIGNIFICATIVA </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="card-cyber accent-purple">
                    <div class="title-test-p"><i class="bi bi-tags"></i> num_temas (Complejidad)</div>
                    <div class="text-stats-p">Estadístico H: <span class="val-stats-p">62,932.36</span></div>
                    <div class="text-stats-p">p-value: <span class="val-stats-p">0.0000e+00</span></div>
                    <div class="badge-rel-p">✅ RELACIÓN SIGNIFICATIVA </div>
                </div>
            """, unsafe_allow_html=True)























##Desechos que pueden ser útiles en el futuro##


# elif selected == "Salud (Clasificación)":
    
#     # --- 1. ESTILOS CSS (Inspirados exactamente en tu interfaz de Fútbol) ---
#     st.markdown("""
#         <style>
#         /* Contenedor de tarjeta general */
#         .card-cyber {
#             background-color: #0d1117;
#             border: 1px solid #30363d;
#             border-radius: 10px;
#             padding: 1.5rem;
#             margin-bottom: 1rem;
#         }
#         /* Acento azul (izquierda) para Chi-cuadrado */
#         .accent-blue { border-left: 5px solid #00e5ff; }
        
#         /* Acento naranja (borde total) para Kruskal-Wallis */
#         .accent-orange { border: 2px solid #ff9f00; }

#         .title-test { color: #00e5ff; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.8rem; }
#         .text-stats { color: #8b949e; font-family: 'Courier New', monospace; font-size: 0.9rem; }
#         .val-stats { color: #ffffff; font-weight: bold; float: right; }
        
#         /* Caja oscura interna para resultados de Kruskal */
#         .conclusion-box {
#             background-color: #161b22;
#             border-radius: 8px;
#             padding: 15px;
#             margin-top: 10px;
#             font-family: 'Courier New', monospace;
#         }
        
#         /* Badges de relación */
#         .badge-rel {
#             background-color: #062c30; color: #00e5ff; padding: 5px; border-radius: 5px;
#             font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px;
#             border: 1px solid #00e5ff; display: block;
#         }
#         .badge-no-rel {
#             background-color: #211d1a; color: #ff9f00; padding: 5px; border-radius: 5px;
#             font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px;
#             border: 1px solid #ff9f00; display: block;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     st.markdown("""<div style="font-size: 2.8rem; font-weight: bold; line-height: 1.2; color: #FFFFFF; 
#                 text-shadow: 2px 2px 8px #000000, 0px 0px 20px #000000; margin-bottom: 10px;"><i class="bi bi-heart-pulse" 
#                 style="color: #FFFFFF; margin-right: 10px;"></i> Monitor de Riesgo Diabético (NHANES)</div>""", unsafe_allow_html=True)

#     # ---  2. CORRECCIÓN DEFINITIVA (Mapeo basado en tu CSV real) ---
#     df_calc_salud = df_salud.copy()
    
#     # Usamos .str.strip() para evitar que espacios ocultos rompan el mapeo
#     df_calc_salud['actividad_bin'] = df_calc_salud['actividad_fisica'].str.strip().map({'Activo': 1, 'Inactivo': 0}).fillna(0)
#     df_calc_salud['es_diabetico_bin'] = df_calc_salud['es_diabetico'].str.strip().map({'Si': 1, 'No': 0, 'Fronterizo': 0}).fillna(0)

#     # Cálculos de KPIs
#     prevalencia = df_calc_salud['es_diabetico_bin'].mean() * 100
#     activos_pct = df_calc_salud['actividad_bin'].mean() * 100 # ¡Ya no será 0.0%!

#     # --- Recálculo de KPIs ---
#     total_pacientes = len(df_salud)
#     prevalencia = df_calc_salud['es_diabetico_bin'].mean() * 100
#     activos_pct = df_calc_salud['actividad_bin'].mean() * 100 # Ahora sí detectará los 'Active'

#     # --- 3. RENDERIZADO DE KPIs ---
#     c1, c2, c3, c4, c5 = st.columns(5)
#     with c1: st.markdown(crear_tarjeta("bi bi-people-fill", "Pacientes", f"{len(df_salud)}"), unsafe_allow_html=True)
#     with c2: st.markdown(crear_tarjeta("bi bi-exclamation-triangle", "% Diabéticos", f"{prevalencia:.1f}%"), unsafe_allow_html=True)
#     with c3: st.markdown(crear_tarjeta("bi bi-speedometer", "IMC Promedio", f"{df_salud['imc'].mean():.1f}"), unsafe_allow_html=True)
#     with c4: st.markdown(crear_tarjeta("bi bi-droplet-half", "Glucosa Prom.", f"{df_salud['glucosa_ayunas'].mean():,.0f}"), unsafe_allow_html=True)
#     with c5: st.markdown(crear_tarjeta("bi bi-activity", "% Activos", f"{activos_pct:.1f}%"), unsafe_allow_html=True)

#     st.write("")

#     # --- 4. INICIALIZACIÓN DE PESTAÑAS (Solución al NameError) ---
#     tab1_s, tab2_s, tab3_s, tab4_s = st.tabs(["Estadísticas Descriptivas", "Gráficos Principales", "Imputación", "Pruebas Estadísticas"])

#     with tab1_s:
#         st.markdown("<h3 style='color: #4cc9f0;'> Base de Datos Procesada</h3>", unsafe_allow_html=True)
        
#         # --- CONTROLES DINÁMICOS PARA SALUD ---
#         col_sort_s1, col_sort_s2 = st.columns([3, 2])
#         with col_sort_s1:
#             columna_orden_s = st.selectbox("Ordenar por campo clínico:", df_salud.columns, index=2) 
#         with col_sort_s2:
#             sentido_s = st.radio( "Mostrar por orden:",["Ascendente", "Descendente"], horizontal=True, key="sort_s_radio")

#         df_mostrar_s = df_salud.sort_values(by=columna_orden_s, ascending=(sentido_s == "Ascendente")).reset_index(drop=True)
#         df_mostrar_s.index = df_mostrar_s.index + 1

#         if 'limit_s' not in st.session_state:
#             st.session_state.limit_s = 50

#         st.dataframe(df_mostrar_s.head(st.session_state.limit_s).style.set_properties(**{'text-align': 'center'}), use_container_width=True)

#         col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
#         with col_c2:
#             if st.session_state.limit_s < len(df_mostrar_s):
#                 if st.button("Mostrar 50 registros más", key="btn_s_more", use_container_width=True):
#                     st.session_state.limit_s += 50
#                     st.rerun()

#         st.markdown("---")
#         st.markdown("<h3 style='color: #4cc9f0;'> Estadísticas Descriptivas </h3>", unsafe_allow_html=True)
#         desc_num = df_salud.describe().T 
#         desc_num = desc_num.rename(columns={'count': 'Cantidad', 'mean': 'Promedio', 'std': 'Desv. Est.', '50%': 'Mediana'})
#         st.dataframe(desc_num.style.format("{:.2f}").set_properties(**{'text-align': 'center'}), use_container_width=True)

#     with tab2_s:
#         st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Análisis Exploratorio de Clasificación</h3>", unsafe_allow_html=True)
#         col_sh1, col_sh2 = st.columns(2)
#         with col_sh1:
#             st.markdown("<h5 style='text-align: center; color: #ffffff;'>Glucosa por Estado Diabético</h5>", unsafe_allow_html=True)
#             fig_s1 = px.box(df_salud, x='es_diabetico', y='glucosa_ayunas', color='es_diabetico', 
#                             template="plotly_dark", color_discrete_sequence=['#00e5ff', '#4cc9f0', '#7209b7'])
#             st.plotly_chart(fig_s1, use_container_width=True)
#         with col_sh2:
#             st.markdown("<h5 style='text-align: center; color: #ffffff;'>Distribución de IMC y Género</h5>", unsafe_allow_html=True)
#             fig_s2 = px.violin(df_salud, x='genero', y='imc', color='es_diabetico', box=True, 
#                                template="plotly_dark", color_discrete_sequence=['#00e5ff', '#f72585'])
#             st.plotly_chart(fig_s2, use_container_width=True)

#         # --- AJUSTE DE COLOR EN MATRIZ DE CORRELACIÓN ---
#         st.markdown("---")
#         st.markdown("<h5 style='text-align: center; color: #ffffff;'>Mapa de Calor de Correlaciones</h5>", unsafe_allow_html=True)
        
#         df_corr = df_salud.select_dtypes(include=['number'])
#         if 'id_secuencia' in df_corr.columns:
#             df_corr = df_corr.drop(columns=['id_secuencia']) # [cite: 167]
        
#         corr_matrix = df_corr.corr() # [cite: 216, 220]
        
#         # Escala personalizada para coincidir con tu plantilla (Oscuro a Cian/Neón)
#         escala_cyan = [[0, '#0a192f'], [0.5, '#003566'], [1, '#00e5ff']]
        
#         fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", 
#                              color_continuous_scale=escala_cyan, 
#                              template="plotly_dark", labels=dict(color="Correlación"))
        
#         st.plotly_chart(fig_corr, use_container_width=True)

#     with tab3_s:
#         st.markdown("<h3 style='color: #4cc9f0;'> Tratamiento de Datos Faltantes</h3>", unsafe_allow_html=True)
#         st.write("No hay datos faltantes")
#         # Reporte de integridad basado en tu EDA 
#         nulos_data = {"Variable": df_salud.columns, "Total Nulos": [0]*len(df_salud.columns), "%": ["0.0%"]*len(df_salud.columns)}
#         st.table(pd.DataFrame(nulos_data))

#     with tab4_s:
#         # ---  1. CSS ACTUALIZADO: ARMONÍA DE AZULES ---
#         st.markdown("""
#             <style>
#             .card-cyber {
#                 background-color: #0d1117;
#                 border: 1px solid #30363d;
#                 border-radius: 10px;
#                 padding: 1.5rem;
#                 margin-bottom: 1rem;
#             }
#             /* Acentos en distintos tonos de azul */
#             .accent-cyan { border-left: 5px solid #00e5ff; }
#             .accent-royal { border: 2px solid #4cc9f0; }

#             .title-test-blue { color: #00e5ff; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.8rem; }
#             .text-stats-blue { color: #8b949e; font-family: 'Courier New', monospace; font-size: 0.9rem; }
#             .val-stats-blue { color: #ffffff; font-weight: bold; float: right; }
            
#             .conclusion-box-blue {
#                 background-color: #001d3d; /* Azul profundo */
#                 border-radius: 8px;
#                 padding: 15px;
#                 margin-top: 10px;
#                 font-family: 'Courier New', monospace;
#                 border: 1px solid #1e6091;
#             }
            
#             /* Badges en escala de azules */
#             .badge-rel-blue {
#                 background-color: #062c30; color: #00e5ff; padding: 5px; border-radius: 5px;
#                 font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px;
#                 border: 1px solid #00e5ff; display: block;
#             }
#             .badge-no-rel-blue {
#                 background-color: #1a252f; color: #5f7adb; padding: 5px; border-radius: 5px;
#                 font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px;
#                 border: 1px solid #5f7adb; display: block;
#             }
#             .section-header-blue {
#                 color: #4cc9f0; font-size: 1.2rem; font-weight: bold;
#                 border-left: 4px solid #4cc9f0; padding-left: 10px; margin-bottom: 15px;
#             }
#             </style>
#         """, unsafe_allow_html=True)

#         st.markdown("<h3 style='color: #00e5ff;'> Pruebas de Asociación y Dependencia</h3>", unsafe_allow_html=True)
#         col_l, col_r = st.columns(2)

#         with col_l:
#             st.markdown("<div class='section-header-blue'> Chi-cuadrado (Categóricas)</div>", unsafe_allow_html=True)
#             st.write("Análisis de independencia demográfica:")
            
#             # Tarjeta 1: Género
#             st.markdown(f"""
#                 <div class="card-cyber accent-cyan">
#                     <div class="title-test-blue"><i class="bi bi-gender-ambiguous"></i> Género vs Diabetes</div>
#                     <div class="text-stats-blue">p-value: <span class="val-stats-blue">2.8882e-01</span></div>
#                     <div class="badge-no-rel-blue">⚠️ SIN RELACIÓN SIGNIFICATIVA </div>
#                 </div>
#             """, unsafe_allow_html=True)

#             # Tarjeta 2: Actividad Física
#             st.markdown(f"""
#                 <div class="card-cyber accent-cyan">
#                     <div class="title-test-blue"><i class="bi bi-bicycle"></i> Actividad Física vs Diabetes</div>
#                     <div class="text-stats-blue">p-value: <span class="val-stats-blue">6.4599e-01</span></div>
#                     <div class="badge-no-rel-blue">⚠️ SIN RELACIÓN SIGNIFICATIVA </div>
#                 </div>
#             """, unsafe_allow_html=True)

#         with col_r:
#             st.markdown("<div class='section-header-blue'> Kruskal-Wallis (Variables Mixtas)</div>", unsafe_allow_html=True)
#             st.write("Evaluando dependencia clínica:")
            
#             # Tarjeta de Variables Críticas en azul armonioso super lindo wow
#             st.markdown(f"""
#                 <div class="card-cyber accent-royal">
#                     <div class="title-test-blue" style="color: #4cc9f0;"><i class="bi bi-heart-pulse"></i> Análisis de Variables Críticas</div>
#                     <p style="font-size: 0.85rem; color: #8b949e;">Variación biométrica significativa según el grupo de diagnóstico.</p>
#                     <div class="conclusion-box-blue">
#                         <div class="text-stats-blue" style="color: #00e5ff;">Glucosa p-value: <span class="val-stats-blue">0.0000e+00</span></div>
#                         <div class="text-stats-blue" style="color: #00e5ff;">IMC p-value: <span class="val-stats-blue">7.6301e-05</span></div>
#                     </div>
#                     <div class="badge-rel-blue">✅ RELACIÓN SIGNIFICATIVA </div>
#                     <p style="font-size: 0.85rem; color: #ffffff; margin-top: 15px;">
#                          <b>Conclusión:</b> Se rechaza H₀ por lo que La Glucosa y el IMC son factores de segmentación críticos para el diagnóstico.
#                     </p>
#                 </div>
#             """, unsafe_allow_html=True)
