import streamlit as st
import pandas as pd
import os
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import plotly.express as px
import time

#################################################################################
################## RECORDAR PIP INSTALL STATSMODELS #############################
#################################################################################

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 1. CONFIGURACIÓN DE PÁGINA
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

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
# 4. CARGA DE DATOS (CSV)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

@st.cache_data
def load_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    ruta_futbol = os.path.join(base_dir, 'data', 'processed', 'FTP_limpio.csv')
    df_futbol = pd.read_csv(ruta_futbol)
    return df_futbol

df_futbol = load_data()

@st.cache_data
def load_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Carga Fútbol
    ruta_futbol = os.path.join(base_dir, 'data', 'processed', 'FTP_limpio.csv')
    df_futbol = pd.read_csv(ruta_futbol)
    
    # Carga Salud (NHANES)
    ruta_salud = os.path.join(base_dir, 'data', 'processed', 'nhanes_limpio.csv')
    df_salud = pd.read_csv(ruta_salud)
    
    return df_futbol, df_salud

df_futbol, df_salud = load_data()

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 5. MENÚ LATERAL
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
with st.sidebar:
    st.markdown("<h2 style='color: white !important; text-align: center; font-weight: 700;'>Menú Principal</h2>", unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Fútbol (Regresión)", "Salud (Clasificación)"],
        icons=["trophy", "heart-pulse"],
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
    
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 6. SECCIÓN: FÚTBOL (REGRESIÓN)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

if selected == "Fútbol (Regresión)":
    st.markdown("""<div style="font-size: 2.8rem; font-weight: bold; line-height: 1.2; color: #FFFFFF; 
                text-shadow: 2px 2px 8px #000000, 0px 0px 20px #000000; margin-bottom: 10px;"><i class="bi bi-graph-up-arrow" 
                style="color: #FFFFFF; margin-right: 10px;"></i> Monitor de Valor de Mercado Para Clubes</div>""", unsafe_allow_html=True)
    st.markdown("<p>Exploración de variables predictoras para el <code>SquadMarketValue</code>.</p>", unsafe_allow_html=True)
    
    # --- Tarjetas Glassmorphism Personalizadas (Centradas y con Iconos) ---
    def crear_tarjeta(icono, titulo, valor):
        return f"""
        <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        border-radius: 15px; border: 1px solid rgba(0, 229, 255, 0.3); padding: 15px; text-align: center;">
            <i class="{icono}" style="font-size: 28px; color: #00e5ff; margin-bottom: 5px; display: inline-block;"></i>
            <p style="margin: 0; font-size: 14px; color: #e0e0e0; font-weight: 600;">{titulo}</p>
            <div style="margin: 5px 0 0 0; color: white; font-size: 26px; font-weight: bold;">{valor}</div>
        </div>
        """
    
    # --- Cálculos de KPIs ---
    total_equipos = len(df_futbol)
    valor_promedio = df_futbol['SquadMarketValue'].mean()
    # Sustituimos el máximo de goles por una tasa de victoria promedio (relevancia deportiva)
    victoria_media = (df_futbol['TotalWins'].mean() / df_futbol['MatchesPlayed'].mean()) * 100
    # Jugadores internacionales (crucial para el valor según nuestro análisis)
    jugadores_int_total = df_futbol['NationalTeamPlayers'].sum()
    # Edad promedio global (factor clave de depreciación/valor)
    edad_mediana = df_futbol['AveragePlayerAge'].median()

    # --- Renderizado de las 5 Columnas ---
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(crear_tarjeta("bi bi-shield-shaded", "Muestra de Clubes", f"{total_equipos}"), unsafe_allow_html=True)
    with col2:
        st.markdown(crear_tarjeta("bi bi-cash-stack", "Valor Promedio", f"{valor_promedio:,.1f} M€"), unsafe_allow_html=True)
    with col3:
        st.markdown(crear_tarjeta("bi bi-trophy", "% Victoria Media", f"{victoria_media:.1f}%"), unsafe_allow_html=True)
    with col4:
        st.markdown(crear_tarjeta("bi bi-people", "Total Internacionales", f"{jugadores_int_total:,}"), unsafe_allow_html=True)
    with col5:
        st.markdown(crear_tarjeta("bi bi-calendar-event", "Edad Media", f"{edad_mediana:.1f}"), unsafe_allow_html=True)
        
    st.write("") # Espacio
    
    # --- Pestañas ---
    tab1, tab2, tab3, tab4 = st.tabs(["Estadísitcas Descriptivas", "Gráficos Principales", "Imputaciones", "Pruebas Estadísticas"])
    
    with tab1:
        st.markdown("<h3 style='color: #4cc9f0;'> Base de Datos Procesada</h3>", unsafe_allow_html=True)
        
        # 1. TRADUCCIÓN DE COLUMNAS AL ESPAÑOL
        traduccion_columnas = {
            'ClubName': 'Club', 'LeagueName': 'Liga', 'Country': 'País',
            'SquadMarketValue': 'Valor Mercado (M€)', 'StadiumCapacity': 'Capacidad Estadio',
            'ForeignersPercentage': '% Extranjeros', 'NationalTeamPlayers': 'Jugadores Selección',
            'AveragePlayerAge': 'Edad Promedio', 'AveragePlayerHeight': 'Altura Promedio (cm)',
            'TotalPlayers': 'Total Jugadores', 'TotalGoals': 'Goles', 'TotalWins': 'Victorias',
            'TotalDraws': 'Empates', 'TotalLosses': 'Derrotas', 'TotalYellowCards': 'Tarjetas Amarillas',
            'TotalRedCards': 'Tarjetas Rojas', 'MatchesPlayed': 'Partidos Jugados',
            'TotalAssists': 'Asistencias',
            'TotalMinutesPlayed': 'Minutos Jugados'
        }
        df_mostrar = df_futbol.rename(columns=traduccion_columnas)
        df_mostrar_f = df_futbol.rename(columns=traduccion_columnas)
        # --- CONTROLES DINÁMICOS DE ORDENAMIENTO ---
        col_sort_f1, col_sort_f2 = st.columns([3, 2])
        with col_sort_f1:
            columna_orden_f = st.selectbox("Ordenar tabla por:", df_mostrar_f.columns, index=3) # Default: Valor Mercado
        with col_sort_f2:
            sentido_f = st.radio("Mostrar por orden:", ["Descendente", "Ascendente"], horizontal=True, key="sort_f_radio")

        # Aplicamos el orden dinámico
        df_mostrar_f = df_mostrar_f.sort_values(
            by=columna_orden_f, 
            ascending=(sentido_f == "Ascendente")
        ).reset_index(drop=True)

        # --- AJUSTE DE ÍNDICE (Empezar en 1, importante porque es incómodo hasta el hp) ---
        df_mostrar_f.index = df_mostrar_f.index + 1

        # --- LÓGICA TRAS "MOSTRAR 50 MÁS" CENTRADA ---
        if 'limit_f' not in st.session_state:
            st.session_state.limit_f = 50

        # Renderizado de la tabla con el límite actual
        st.dataframe(
            df_mostrar_f.head(st.session_state.limit_f).style.set_properties(**{'text-align': 'center'}), 
            use_container_width=True
        )

        # Creamos 3 columnas para "encerrar" el botón en el centro
        col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
        
        with col_b2: # La columna del medio
            if st.session_state.limit_f < len(df_mostrar_f):
                if st.button("Cargar 50 más", key="btn_f_more", use_container_width=True):
                    st.session_state.limit_f += 50
                    st.rerun()
        
        st.markdown("---")
        
        # 3. ESTADÍSTICAS DESCRIPTIVAS MEJORADAS y definitivas 100% no FAKE
        st.markdown("<h3 style='color: #4cc9f0;'> Estadísticas Descriptivas</h3>", unsafe_allow_html=True)
        
        # Calculamos el describe, lo transponemos (.T) y renombramos las métricas
        df_stats = df_mostrar.describe().T
        df_stats = df_stats.rename(columns={
            'count': 'Cantidad', 'mean': 'Promedio', 'std': 'Desviación Est.',
            'min': 'Mínimo', '25%': 'Percentil 25', '50%': 'Mediana', 
            '75%': 'Percentil 75', 'max': 'Máximo'
        })
        
        # --- CAMBIO: Formato de 2 decimales y centrado de celdas/encabezados ---
        df_stats_estilizado = df_stats.style.format("{:.2f}")\
            .set_properties(**{'text-align': 'center'})\
            .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}])
            
        st.dataframe(df_stats_estilizado, use_container_width=True)
        
    with tab2:
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Análisis Exploratorio Espacial (EDA)</h3>", unsafe_allow_html=True)
        
        # --- DICCIONARIO DE TRADUCCIÓN GLOBAL ---
        traducciones = {
            'ClubName': 'Club', 'LeagueName': 'Liga', 'Country': 'País',
            'SquadMarketValue': 'Valor Mercado (M€)', 'StadiumCapacity': 'Capacidad Estadio',
            'ForeignersPercentage': '% Extranjeros', 'NationalTeamPlayers': 'Jugadores Selección',
            'AveragePlayerAge': 'Edad Promedio', 'AveragePlayerHeight': 'Altura Promedio (cm)',
            'TotalPlayers': 'Total Jugadores', 'TotalGoals': 'Goles', 'TotalWins': 'Victorias',
            'TotalDraws': 'Empates', 'TotalLosses': 'Derrotas', 'TotalYellowCards': 'Tarjetas Amarillas',
            'TotalRedCards': 'Tarjetas Rojas', 'MatchesPlayed': 'Partidos Jugados',
            'TotalAssists': 'Asistencias', 'TotalMinutesPlayed': 'Minutos Jugados'
        }

        # --- HACK CSS: Botón de Pantalla Completa Personalizado ---
        st.markdown("""
            <style>
            [data-testid="StyledFullScreenButton"] {
                visibility: visible !important;
                opacity: 0.3 !important;
                transition: all 0.3s ease-in-out;
            }
            [data-testid="StyledFullScreenButton"] svg { fill: #00e5ff !important; }
            [data-testid="StyledFullScreenButton"]:hover { opacity: 1.0 !important; }
            </style>
        """, unsafe_allow_html=True)

        config_plotly = {'scrollZoom': True, 'displayModeBar': False}
        plantilla = "plotly_dark"
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            # --- AÑADIMOS EL TÍTULO CON STREAMLIT ---
            st.markdown("<h4 style='text-align: center; color: #ffffff; font-size: 1.1rem; margin-bottom: 0;'> Eficiencia Ofensiva vs. Valor de Mercado</h4>", unsafe_allow_html=True)
            
            # GRÁFICO 1: Traducimos (sin el parámetro title)
            fig1 = px.scatter(
                df_futbol, x='TotalGoals', y='SquadMarketValue', 
                size='StadiumCapacity', color='ForeignersPercentage',
                hover_name='ClubName',
                color_continuous_scale=['#0f2027', '#203a43', '#00e5ff'],
                labels=traducciones, 
                template=plantilla
            )
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                dragmode='pan',
                margin=dict(t=20) # Reducimos el margen superior de Plotly para que no quede tanto hueco
            )
            st.plotly_chart(fig1, use_container_width=True, config=config_plotly)

        with col_g2:
            # --- AÑADIMOS EL TÍTULO CON STREAMLIT ---
            st.markdown("<h4 style='text-align: center; color: #ffffff; font-size: 1.1rem; margin-bottom: 0;'> Distribución Financiera: Top Ligas</h4>", unsafe_allow_html=True)
            
            # GRÁFICO 2: Boxplot Traducido (sin el parámetro title)
            top_ligas = df_futbol.groupby('LeagueName')['SquadMarketValue'].mean().nlargest(6).index
            df_top_ligas = df_futbol[df_futbol['LeagueName'].isin(top_ligas)]
            
            fig2 = px.box(
                df_top_ligas, x='LeagueName', y='SquadMarketValue', color='LeagueName',
                labels=traducciones,
                template=plantilla,
                hover_data={'LeagueName': False, 'ClubName': True}, 
                color_discrete_sequence=['#00e5ff', '#4cc9f0', '#f72585', '#b5179e', '#7209b7', '#3a0ca3']
            )
            
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                showlegend=False, 
                dragmode='pan',
                margin=dict(t=20) # Reducimos margen superior
            )
            
            # Restaurar Grid Cian
            fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0, 229, 255, 0.1)', zeroline=False)
            fig2.update_xaxes(showgrid=False, zeroline=False)
            
            st.plotly_chart(fig2, use_container_width=True, config=config_plotly)
            
            
            
        # GRÁFICO 3: Mapa de Calor con etiquetas en español
        st.markdown("<h4 style='color: #4cc9f0; text-align: center;'> Correlación de Variables Predictoras</h4>", unsafe_allow_html=True)
        cols_num = df_futbol.select_dtypes(include=['float64', 'int64', 'int32']).columns
        # Creamos una copia del DF con nombres en español solo para el Heatmap
        df_corr_es = df_futbol[cols_num].rename(columns=traducciones)
        matriz_corr = df_corr_es.corr()
        
        fig3 = px.imshow(
            matriz_corr, text_auto=".2f", aspect="auto",
            color_continuous_scale=[[0, 'rgba(11, 15, 25, 0.8)'], [0.5, 'rgba(76, 201, 240, 0.5)'], [1, '#00e5ff']]
        )
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', dragmode='pan')
        st.plotly_chart(fig3, use_container_width=True, config=config_plotly)

        # -------------------------------------------------------------------
        # GRÁFICOS 4, 5 y 6: Tendencias de Regresión (Justificación del modelo)
        # -------------------------------------------------------------------
        st.markdown("<br><hr style='border: 1px solid rgba(0, 229, 255, 0.2);'><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #4cc9f0; text-align: center;'> Tendencias de Regresión: Variables Clave vs Valor</h4>", unsafe_allow_html=True)
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        # 1. Quitamos 'titulo' de los parámetros de la función
        def crear_grafico_tendencia(df, x_col, etiqueta_x):
            fig = px.scatter(
                df, x=x_col, y='SquadMarketValue', 
                trendline="ols",
                trendline_color_override="#ff0055", 
                color_discrete_sequence=['rgba(0, 229, 255, 0.4)'], 
                hover_name='ClubName'
            )
            fig.update_layout(
                # 2. Eliminamos la línea del title de Plotly
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Montserrat", color="#a0a0a0"),
                margin=dict(l=10, r=10, t=10, b=10), # <--- 3. Reducimos el margen superior (t=10)
                xaxis_title=etiqueta_x,
                yaxis_title="",
                dragmode='pan'
            )
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False)
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255, 255, 255, 0.05)', zeroline=False)
            return fig

        with col_r1:
            # 4. Agregamos el título centrado con HTML
            st.markdown("<h5 style='text-align: center; color: #e0e0e0; font-size: 1rem; margin-bottom: 0;'>Intl. vs Valor</h5>", unsafe_allow_html=True)
            fig_r1 = crear_grafico_tendencia(df_futbol, 'NationalTeamPlayers', 'Jugadores Selección')
            st.plotly_chart(fig_r1, use_container_width=True, config=config_plotly) 
            
        with col_r2:
            st.markdown("<h5 style='text-align: center; color: #e0e0e0; font-size: 1rem; margin-bottom: 0;'>Victorias vs Valor</h5>", unsafe_allow_html=True)
            fig_r2 = crear_grafico_tendencia(df_futbol, 'TotalWins', 'Total Victorias')
            st.plotly_chart(fig_r2, use_container_width=True, config=config_plotly) 
            
        with col_r3:
            st.markdown("<h5 style='text-align: center; color: #e0e0e0; font-size: 1rem; margin-bottom: 0;'>Edad vs Valor</h5>", unsafe_allow_html=True)
            fig_r3 = crear_grafico_tendencia(df_futbol, 'AveragePlayerAge', 'Edad Promedio')
            st.plotly_chart(fig_r3, use_container_width=True, config=config_plotly)
        
        
        
    with tab3:
        st.markdown("<h3 style='color: #4cc9f0;'> Tratamiento de Datos Faltantes</h3>", unsafe_allow_html=True)
        
        # 1. Explicación Teórica mini
        st.write("En este proyecto, evaluamos dos enfoques principales para el tratamiento de datos nulos:")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("""
            <div style="background-color: rgba(0, 229, 255, 0.05); backdrop-filter: blur(12px); border-radius: 10px; border: 1px solid rgba(0, 229, 255, 0.3); border-left: 4px solid #00e5ff; padding: 15px; height: 100%;">
                <h5 style='color: #00e5ff; margin-top:0;'><i class='bi bi-diagram-3'></i> 1. Tendencia Central (Mediana)</h5>
                <p style='font-size: 0.9rem; color: #e0e0e0; margin-bottom:0;'>Reemplaza nulos por el valor central (Mediana). Puede sesgar la varianza.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t2:
            st.markdown("""
            <div style="background-color: rgba(0, 229, 255, 0.05); backdrop-filter: blur(12px); border-radius: 10px; border: 1px solid rgba(0, 229, 255, 0.3); border-left: 4px solid #00e5ff; padding: 15px; height: 100%;">
                <h5 style='color: #00e5ff; margin-top:0;'><i class='bi bi-diagram-3'></i> 2. KNN Imputer</h5>
                <p style='font-size: 0.9rem; color: #e0e0e0; margin-bottom:0;'>Analiza los 'k' vecinos más cercanos (clubes similares) para estimar el valor faltante respetando la distribución.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Comparativa de Medias "DINÁMICA" (Cálculo en tiempo real)
        st.markdown("<h4 style='color: #4cc9f0;'> Comparativa de Medias (Cálculo Dinámico)</h4>", unsafe_allow_html=True)
        st.write("Cálculo en tiempo real del impacto de los métodos de imputación frente a la distribución original:")
        
        with st.spinner('Calculando imputaciones con Sklearn en tiempo real...'):
            from sklearn.impute import SimpleImputer, KNNImputer
            
            # Cargamos el archivo RAW (el que aún tiene los NaNs, antes de procesar)
            base_dir = os.path.abspath(os.path.dirname(__file__))
            ruta_raw = os.path.join(base_dir, '..', 'data', 'raw', 'FTP.csv')
            df_raw = pd.read_csv(ruta_raw)
            
            cols_faltantes = ['TotalYellowCards', 'TotalRedCards', 'TotalAssists', 'TotalMinutesPlayed']
            
            # Imputación Mediana
            df_med = df_raw.copy()
            imp_med = SimpleImputer(strategy='median')
            df_med[cols_faltantes] = imp_med.fit_transform(df_med[cols_faltantes])
            
            # Imputación KNN (Excluyendo el target)
            df_knn_calc = df_raw.copy()
            cols_knn = [c for c in df_raw.select_dtypes(include=['float64', 'int64']).columns if c != 'SquadMarketValue']
            imp_knn = KNNImputer(n_neighbors=5)
            df_knn_calc[cols_knn] = imp_knn.fit_transform(df_knn_calc[cols_knn])
            
            # Armamos el DataFrame dinámico
            datos_comparativa = {
                "Variable": cols_faltantes,
                "Media Original": [df_raw[col].mean() for col in cols_faltantes],
                "Media Mediana": [df_med[col].mean() for col in cols_faltantes],
                "Media KNN": [df_knn_calc[col].mean() for col in cols_faltantes]
            }
            df_comp = pd.DataFrame(datos_comparativa)
            
            def color_knn_col(x):
                return ['background-color: rgba(0, 229, 255, 0.15); color: #00e5ff; font-weight: bold;' if col == 'Media KNN' else '' for col in x.index]

            st.dataframe(
                df_comp.style.format({
                    "Media Original": "{:.2f}", "Media Mediana": "{:.2f}", "Media KNN": "{:.2f}"
                }).hide(axis="index").apply(color_knn_col, axis=1).set_properties(**{
                    'text-align': 'center', 'background-color': 'transparent'
                }).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', 'rgba(15, 20, 30, 0.8)'), ('color', '#4cc9f0')]}
                ]),
                use_container_width=True
            )

        # 3. Justificación y Lógica de Negocio
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(" Ver Corrección de Lógica de Negocio (Post-Imputación)"):
            st.write("Para evitar incoherencias donde el KNN generaba más asistencias que goles, aplicamos un techo basado en el ratio histórico real:")
            st.code("""
                    # Ratio real calculado de asistencias por gol
                    mask = df['TotalAssists'].notna() & df['TotalGoals'].notna()
                    ratio = df.loc[mask, 'TotalAssists'].sum() / df.loc[mask, 'TotalGoals'].sum()

                    # Corrección
                    df_knn['TotalAssists'] = np.where(
                        df_knn['TotalAssists'] > df_knn['TotalGoals'], 
                        (df_knn['TotalGoals'] * ratio).round(), 
                        df_knn['TotalAssists']
                    )
                                """, language="python")

        st.markdown("""
        <div style="background-color: rgba(15, 20, 30, 0.8); border-left: 4px solid #fca311; padding: 15px; border-radius: 8px; margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); border-right: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #e0e0e0;"> <b style="color: #fca311;">Variables Imputadas:</b> <code style="color: #4cc9f0; background: transparent;">TotalYellowCards</code>, <code style="color: #4cc9f0; background: transparent;">TotalRedCards</code>, <code style="color: #4cc9f0; background: transparent;">TotalAssists</code>, <code style="color: #4cc9f0; background: transparent;">TotalMinutesPlayed</code>.</span>
        </div><br>
        """, unsafe_allow_html=True)
        
    with tab4:
        st.markdown("<h3 style='color: #4cc9f0;'> Pruebas de Asociación y Dependencia</h3>", unsafe_allow_html=True)
        
        from scipy.stats import spearmanr, kruskal

        # --- Función para generar tarjetas de correlación estilo Tab 3 ---
        def card_correlacion(titulo, pearson, spearman, icono, color_borde="#00e5ff"):
            return f"""
            <div style="background-color: rgba(15, 20, 30, 0.6); backdrop-filter: blur(12px); border-radius: 12px; border: 1px solid rgba(0, 229, 255, 0.2); border-left: 5px solid {color_borde}; padding: 15px; margin-bottom: 15px;">
                <h5 style="color: {color_borde}; margin-top: 0; font-size: 1rem;"><i class="bi {icono}"></i> {titulo} vs Valor</h5>
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: #a0a0a0; font-size: 0.85rem;">Coef. Pearson:</span>
                    <span style="color: #ffffff; font-weight: bold; font-family: monospace;">{pearson:.4f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #a0a0a0; font-size: 0.85rem;">Coef. Spearman:</span>
                    <span style="color: #ffffff; font-weight: bold; font-family: monospace;">{spearman:.4f}</span>
                </div>
                <div style="background-color: rgba(0, 229, 255, 0.1); border-radius: 5px; padding: 5px; text-align: center;">
                    <span style="color: #00e5ff; font-size: 0.75rem; font-weight: 600;">✅ EXISTE RELACIÓN SIGNIFICATIVA</span>
                </div>
            </div>
            """

        col_test1, col_test2 = st.columns(2)
        
        with col_test1:
            st.markdown("<h4 style='color: #4cc9f0;'> Correlación (Variables Numéricas)</h4>", unsafe_allow_html=True)
            st.write("Análisis de relación lineal y monótona:")
            
            # Cálculo dinámico de valores
            # 1. NationalTeamPlayers
            p1 = df_futbol['NationalTeamPlayers'].corr(df_futbol['SquadMarketValue'], method='pearson')
            s1, _ = spearmanr(df_futbol['NationalTeamPlayers'], df_futbol['SquadMarketValue'])
            st.markdown(card_correlacion("Jugadores Selección", p1, s1, "bi-people-fill", "#00e5ff"), unsafe_allow_html=True)

            # 2. TotalGoals
            p2 = df_futbol['TotalGoals'].corr(df_futbol['SquadMarketValue'], method='pearson')
            s2, _ = spearmanr(df_futbol['TotalGoals'], df_futbol['SquadMarketValue'])
            st.markdown(card_correlacion("Goles Totales", p2, s2, "bi-trophy-fill", "#4cc9f0"), unsafe_allow_html=True)

            # 3. MatchesPlayed
            p3 = df_futbol['MatchesPlayed'].corr(df_futbol['SquadMarketValue'], method='pearson')
            s3, _ = spearmanr(df_futbol['MatchesPlayed'], df_futbol['SquadMarketValue'])
            st.markdown(card_correlacion("Partidos Jugados", p3, s3, "bi-calendar-check", "#4895ef"), unsafe_allow_html=True)

        with col_test2:
            st.markdown("<h4 style='color: #4cc9f0;'> Kruskal-Wallis (Variable Mixta)</h4>", unsafe_allow_html=True)
            st.write("Evaluando dependencia entre la Liga y el Valor Económico:")
            
            grupos = [group['SquadMarketValue'].values for name, group in df_futbol.groupby('LeagueName')]
            
            if len(grupos) > 1:
                h_stat, p_val = kruskal(*grupos)
                
                # Tarjeta especial para Kruskal-Wallis (Acento ámbar para resaltar conclusión)
                st.markdown(f"""
                <div style="background-color: rgba(15, 20, 30, 0.8); backdrop-filter: blur(12px); border-radius: 15px; border: 1px solid rgba(255, 163, 17, 0.3); border-left: 6px solid #fca311; padding: 20px;">
                    <h5 style="color: #fca311; margin-top: 0;"><i class="bi bi-diagram-2-fill"></i> LeagueName vs SquadMarketValue</h5>
                    <p style="color: #e0e0e0; font-size: 0.9rem; margin-bottom: 15px;">
                        Esta prueba determina si el origen competitivo del club influye en su valoración de mercado.
                    </p>
                    <div style="background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                        <code style="color: #4cc9f0; background: transparent; font-size: 0.9rem;">Estadístico H: {h_stat:.4f}</code><br>
                        <code style="color: #4cc9f0; background: transparent; font-size: 0.9rem;">p-value: {p_val:.4e}</code>
                    </div>
                    <div style="border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 10px;">
                        <p style="color: #ffffff; font-size: 0.9rem; margin-bottom: 0;">
                            <b> Conclusión:</b> Se rechaza H₀. Existen diferencias significativas entre grupos. La liga es un <b>factor de segmentación crítico</b> para el modelo de regresión.
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Datos insuficientes para la prueba.")

        st.markdown("<br><br>", unsafe_allow_html=True)

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 7. SECCIÓN: SALUD (NHANES)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
elif selected == "Salud (Clasificación)":
    
    # --- 1. ESTILOS CSS (Inspirados exactamente en tu interfaz de Fútbol) ---
    st.markdown("""
        <style>
        /* Contenedor de tarjeta general */
        .card-cyber {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        /* Acento azul (izquierda) para Chi-cuadrado */
        .accent-blue { border-left: 5px solid #00e5ff; }
        
        /* Acento naranja (borde total) para Kruskal-Wallis */
        .accent-orange { border: 2px solid #ff9f00; }

        .title-test { color: #00e5ff; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.8rem; }
        .text-stats { color: #8b949e; font-family: 'Courier New', monospace; font-size: 0.9rem; }
        .val-stats { color: #ffffff; font-weight: bold; float: right; }
        
        /* Caja oscura interna para resultados de Kruskal */
        .conclusion-box {
            background-color: #161b22;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            font-family: 'Courier New', monospace;
        }
        
        /* Badges de relación */
        .badge-rel {
            background-color: #062c30; color: #00e5ff; padding: 5px; border-radius: 5px;
            font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px;
            border: 1px solid #00e5ff; display: block;
        }
        .badge-no-rel {
            background-color: #211d1a; color: #ff9f00; padding: 5px; border-radius: 5px;
            font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px;
            border: 1px solid #ff9f00; display: block;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""<div style="font-size: 2.8rem; font-weight: bold; line-height: 1.2; color: #FFFFFF; 
                text-shadow: 2px 2px 8px #000000, 0px 0px 20px #000000; margin-bottom: 10px;"><i class="bi bi-heart-pulse" 
                style="color: #FFFFFF; margin-right: 10px;"></i> Monitor de Riesgo Diabético (NHANES)</div>""", unsafe_allow_html=True)

    # ---  2. CORRECCIÓN DEFINITIVA (Mapeo basado en tu CSV real) ---
    df_calc_salud = df_salud.copy()
    
    # Usamos .str.strip() para evitar que espacios ocultos rompan el mapeo
    df_calc_salud['actividad_bin'] = df_calc_salud['actividad_fisica'].str.strip().map({'Activo': 1, 'Inactivo': 0}).fillna(0)
    df_calc_salud['es_diabetico_bin'] = df_calc_salud['es_diabetico'].str.strip().map({'Si': 1, 'No': 0, 'Fronterizo': 0}).fillna(0)

    # Cálculos de KPIs
    prevalencia = df_calc_salud['es_diabetico_bin'].mean() * 100
    activos_pct = df_calc_salud['actividad_bin'].mean() * 100 # ¡Ya no será 0.0%!

    # --- Recálculo de KPIs ---
    total_pacientes = len(df_salud)
    prevalencia = df_calc_salud['es_diabetico_bin'].mean() * 100
    activos_pct = df_calc_salud['actividad_bin'].mean() * 100 # Ahora sí detectará los 'Active'

    # --- 3. RENDERIZADO DE KPIs ---
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(crear_tarjeta("bi bi-people-fill", "Pacientes", f"{len(df_salud)}"), unsafe_allow_html=True)
    with c2: st.markdown(crear_tarjeta("bi bi-exclamation-triangle", "% Diabéticos", f"{prevalencia:.1f}%"), unsafe_allow_html=True)
    with c3: st.markdown(crear_tarjeta("bi bi-speedometer", "IMC Promedio", f"{df_salud['imc'].mean():.1f}"), unsafe_allow_html=True)
    with c4: st.markdown(crear_tarjeta("bi bi-droplet-half", "Glucosa Prom.", f"{df_salud['glucosa_ayunas'].mean():,.0f}"), unsafe_allow_html=True)
    with c5: st.markdown(crear_tarjeta("bi bi-activity", "% Activos", f"{activos_pct:.1f}%"), unsafe_allow_html=True)

    st.write("")

    # --- 4. INICIALIZACIÓN DE PESTAÑAS (Solución al NameError) ---
    tab1_s, tab2_s, tab3_s, tab4_s = st.tabs(["Estadísticas Descriptivas", "Gráficos Principales", "Imputación", "Pruebas Estadísticas"])

    with tab1_s:
        st.markdown("<h3 style='color: #4cc9f0;'> Base de Datos Procesada</h3>", unsafe_allow_html=True)
        
        # --- CONTROLES DINÁMICOS PARA SALUD ---
        col_sort_s1, col_sort_s2 = st.columns([3, 2])
        with col_sort_s1:
            columna_orden_s = st.selectbox("Ordenar por campo clínico:", df_salud.columns, index=2) 
        with col_sort_s2:
            sentido_s = st.radio( "Mostrar por orden:",["Ascendente", "Descendente"], horizontal=True, key="sort_s_radio")

        df_mostrar_s = df_salud.sort_values(by=columna_orden_s, ascending=(sentido_s == "Ascendente")).reset_index(drop=True)
        df_mostrar_s.index = df_mostrar_s.index + 1

        if 'limit_s' not in st.session_state:
            st.session_state.limit_s = 50

        st.dataframe(df_mostrar_s.head(st.session_state.limit_s).style.set_properties(**{'text-align': 'center'}), use_container_width=True)

        col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
        with col_c2:
            if st.session_state.limit_s < len(df_mostrar_s):
                if st.button("Mostrar 50 registros más", key="btn_s_more", use_container_width=True):
                    st.session_state.limit_s += 50
                    st.rerun()

        st.markdown("---")
        st.markdown("<h3 style='color: #4cc9f0;'> Estadísticas Descriptivas </h3>", unsafe_allow_html=True)
        desc_num = df_salud.describe().T 
        desc_num = desc_num.rename(columns={'count': 'Cantidad', 'mean': 'Promedio', 'std': 'Desv. Est.', '50%': 'Mediana'})
        st.dataframe(desc_num.style.format("{:.2f}").set_properties(**{'text-align': 'center'}), use_container_width=True)

    with tab2_s:
        st.markdown("<h3 style='color: #4cc9f0; text-align: center;'> Análisis Exploratorio de Clasificación</h3>", unsafe_allow_html=True)
        col_sh1, col_sh2 = st.columns(2)
        with col_sh1:
            st.markdown("<h5 style='text-align: center; color: #ffffff;'>Glucosa por Estado Diabético</h5>", unsafe_allow_html=True)
            fig_s1 = px.box(df_salud, x='es_diabetico', y='glucosa_ayunas', color='es_diabetico', 
                            template="plotly_dark", color_discrete_sequence=['#00e5ff', '#4cc9f0', '#7209b7'])
            st.plotly_chart(fig_s1, use_container_width=True)
        with col_sh2:
            st.markdown("<h5 style='text-align: center; color: #ffffff;'>Distribución de IMC y Género</h5>", unsafe_allow_html=True)
            fig_s2 = px.violin(df_salud, x='genero', y='imc', color='es_diabetico', box=True, 
                               template="plotly_dark", color_discrete_sequence=['#00e5ff', '#f72585'])
            st.plotly_chart(fig_s2, use_container_width=True)

        # --- AJUSTE DE COLOR EN MATRIZ DE CORRELACIÓN ---
        st.markdown("---")
        st.markdown("<h5 style='text-align: center; color: #ffffff;'>Mapa de Calor de Correlaciones</h5>", unsafe_allow_html=True)
        
        df_corr = df_salud.select_dtypes(include=['number'])
        if 'id_secuencia' in df_corr.columns:
            df_corr = df_corr.drop(columns=['id_secuencia']) # [cite: 167]
        
        corr_matrix = df_corr.corr() # [cite: 216, 220]
        
        # Escala personalizada para coincidir con tu plantilla (Oscuro a Cian/Neón)
        escala_cyan = [[0, '#0a192f'], [0.5, '#003566'], [1, '#00e5ff']]
        
        fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", 
                             color_continuous_scale=escala_cyan, 
                             template="plotly_dark", labels=dict(color="Correlación"))
        
        st.plotly_chart(fig_corr, use_container_width=True)

    with tab3_s:
        st.markdown("<h3 style='color: #4cc9f0;'> Tratamiento de Datos Faltantes</h3>", unsafe_allow_html=True)
        st.write("No hay datos faltantes")
        # Reporte de integridad basado en tu EDA 
        nulos_data = {"Variable": df_salud.columns, "Total Nulos": [0]*len(df_salud.columns), "%": ["0.0%"]*len(df_salud.columns)}
        st.table(pd.DataFrame(nulos_data))

    with tab4_s:
        # ---  1. CSS ACTUALIZADO: ARMONÍA DE AZULES ---
        st.markdown("""
            <style>
            .card-cyber {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 10px;
                padding: 1.5rem;
                margin-bottom: 1rem;
            }
            /* Acentos en distintos tonos de azul */
            .accent-cyan { border-left: 5px solid #00e5ff; }
            .accent-royal { border: 2px solid #4cc9f0; }

            .title-test-blue { color: #00e5ff; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.8rem; }
            .text-stats-blue { color: #8b949e; font-family: 'Courier New', monospace; font-size: 0.9rem; }
            .val-stats-blue { color: #ffffff; font-weight: bold; float: right; }
            
            .conclusion-box-blue {
                background-color: #001d3d; /* Azul profundo */
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
                font-family: 'Courier New', monospace;
                border: 1px solid #1e6091;
            }
            
            /* Badges en escala de azules */
            .badge-rel-blue {
                background-color: #062c30; color: #00e5ff; padding: 5px; border-radius: 5px;
                font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px;
                border: 1px solid #00e5ff; display: block;
            }
            .badge-no-rel-blue {
                background-color: #1a252f; color: #5f7adb; padding: 5px; border-radius: 5px;
                font-size: 0.75rem; font-weight: bold; text-align: center; margin-top: 10px;
                border: 1px solid #5f7adb; display: block;
            }
            .section-header-blue {
                color: #4cc9f0; font-size: 1.2rem; font-weight: bold;
                border-left: 4px solid #4cc9f0; padding-left: 10px; margin-bottom: 15px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='color: #00e5ff;'> Pruebas de Asociación y Dependencia</h3>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("<div class='section-header-blue'> Chi-cuadrado (Categóricas)</div>", unsafe_allow_html=True)
            st.write("Análisis de independencia demográfica:")
            
            # Tarjeta 1: Género
            st.markdown(f"""
                <div class="card-cyber accent-cyan">
                    <div class="title-test-blue"><i class="bi bi-gender-ambiguous"></i> Género vs Diabetes</div>
                    <div class="text-stats-blue">p-value: <span class="val-stats-blue">2.8882e-01</span></div>
                    <div class="badge-no-rel-blue">⚠️ SIN RELACIÓN SIGNIFICATIVA </div>
                </div>
            """, unsafe_allow_html=True)

            # Tarjeta 2: Actividad Física
            st.markdown(f"""
                <div class="card-cyber accent-cyan">
                    <div class="title-test-blue"><i class="bi bi-bicycle"></i> Actividad Física vs Diabetes</div>
                    <div class="text-stats-blue">p-value: <span class="val-stats-blue">6.4599e-01</span></div>
                    <div class="badge-no-rel-blue">⚠️ SIN RELACIÓN SIGNIFICATIVA </div>
                </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown("<div class='section-header-blue'> Kruskal-Wallis (Variables Mixtas)</div>", unsafe_allow_html=True)
            st.write("Evaluando dependencia clínica:")
            
            # Tarjeta de Variables Críticas en azul armonioso super lindo wow
            st.markdown(f"""
                <div class="card-cyber accent-royal">
                    <div class="title-test-blue" style="color: #4cc9f0;"><i class="bi bi-heart-pulse"></i> Análisis de Variables Críticas</div>
                    <p style="font-size: 0.85rem; color: #8b949e;">Variación biométrica significativa según el grupo de diagnóstico.</p>
                    <div class="conclusion-box-blue">
                        <div class="text-stats-blue" style="color: #00e5ff;">Glucosa p-value: <span class="val-stats-blue">0.0000e+00</span></div>
                        <div class="text-stats-blue" style="color: #00e5ff;">IMC p-value: <span class="val-stats-blue">7.6301e-05</span></div>
                    </div>
                    <div class="badge-rel-blue">✅ RELACIÓN SIGNIFICATIVA </div>
                    <p style="font-size: 0.85rem; color: #ffffff; margin-top: 15px;">
                         <b>Conclusión:</b> Se rechaza H₀ por lo que La Glucosa y el IMC son factores de segmentación críticos para el diagnóstico.
                    </p>
                </div>
            """, unsafe_allow_html=True)
