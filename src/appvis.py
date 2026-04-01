import streamlit as st
import streamlit.components.v1 as components
import base64
import pandas as pd
import sqlite3
import os

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 1. Configuración de página
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="collapsed")

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
        <h1 style="margin: 0; padding: 0; line-height: 1;"> Consultor interactivo: FTP y NHANES</h1>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Regresión (Valor club)", "Clasificación (Salud NHANES)"])

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# PESTAÑA 1: FÚTBOL (NUEVA VERSIÓN TRANSFERMARKT)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
with tab1:
    st.markdown("""<h2 style="margin: 0; padding: 0; line-height: 1; color: #4cc9f0;"> Monitor Financiero de Clubes (Transfermarkt)</h2><br>""", unsafe_allow_html=True)
    
    with st.expander("[ Panel de Filtros Fútbol ]", expanded=True):
        col1_f, col2_f, col3_f, col4_f = st.columns(4)
        
        with col1_f:
            opciones_liga = pd.read_sql_query("SELECT DISTINCT LeagueName FROM regresion_football", conexion)
            filtro_liga = st.multiselect("Liga Competitiva:", opciones_liga['LeagueName'].dropna().tolist(), default=opciones_liga['LeagueName'].dropna().tolist()[:3])
            columna_orden_f = st.selectbox("Ordenar por:", ["SquadMarketValue", "TotalGoals", "TotalWins", "StadiumCapacity"])
            tipo_orden_f = st.radio("Dirección:", ["Descendente", "Ascendente"], key="dir_f")
            limite_f = st.number_input("Límite de registros:", 1, 5000, 100, key="lim_f")
            
        with col2_f:
            val_min, val_max = st.slider("Valor Plantilla (Millones):", 0.0, 1500.0, (0.0, 1500.0), 10.0)
            cap_min, cap_max = st.slider("Capacidad del Estadio:", 0, 100000, (0, 100000), 5000)
            age_min, age_max = st.slider("Edad Promedio:", 16.0, 40.0, (16.0, 40.0), 0.5)
            
        with col3_f:
            goles_min, goles_max = st.slider("Goles Anotados:", 0, 150, (0, 150), 5)
            ganados_min, ganados_max = st.slider("Partidos Ganados:", 0, 50, (0, 50), 1)
            
        with col4_f:
            empates_min, empates_max = st.slider("Partidos Empatados:", 0, 50, (0, 50), 1)
            perdidos_min, perdidos_max = st.slider("Partidos Perdidos:", 0, 50, (0, 50), 1)

    if st.button(" Consultar ", type="primary", use_container_width=True, key="btn_football"):
        
        # Conectamos ABSOLUTAMENTE TODOS los deslizadores al WHERE del SQL adaptado al nuevo Dataset
        where_cond_f = f"""CAST(SquadMarketValue AS REAL) BETWEEN {val_min} AND {val_max} 
                        AND CAST(StadiumCapacity AS REAL) BETWEEN {cap_min} AND {cap_max} 
                        AND CAST(AveragePlayerAge AS REAL) BETWEEN {age_min} AND {age_max}
                        AND CAST(TotalGoals AS REAL) BETWEEN {goles_min} AND {goles_max}
                        AND CAST(TotalWins AS REAL) BETWEEN {ganados_min} AND {ganados_max}
                        AND CAST(TotalDraws AS REAL) BETWEEN {empates_min} AND {empates_max}
                        AND CAST(TotalLosses AS REAL) BETWEEN {perdidos_min} AND {perdidos_max}"""
        
        if filtro_liga:
            ligas_f_str = "', '".join(filtro_liga)
            where_cond_f += f"\n  AND LeagueName IN ('{ligas_f_str}')"
            
        dir_sql_f = "DESC" if tipo_orden_f == "Descendente" else "ASC"

        col_res1, col_res2 = st.columns(2)

        with col_res1:
            st.subheader("1. Base de Datos Filtrada")
            q1_f = f"SELECT * \nFROM regresion_football \nWHERE {where_cond_f} \nORDER BY CAST({columna_orden_f} AS REAL) {dir_sql_f} \nLIMIT {limite_f};"
            st.code(q1_f, language="sql")
            st.dataframe(pd.read_sql_query(q1_f, conexion), use_container_width=True)

            st.subheader("3. Top 10 Clubes más Valiosos")
            q3_f = f"SELECT ClubName as Club, LeagueName as Liga, ROUND(CAST(SquadMarketValue AS REAL), 2) as Valor_Millones \nFROM regresion_football \nWHERE {where_cond_f} \nORDER BY Valor_Millones DESC \nLIMIT 10;"
            st.code(q3_f, language="sql")
            st.dataframe(pd.read_sql_query(q3_f, conexion), use_container_width=True)

            st.subheader("5. Relación: Jugadores de Selección vs Valor")
            q5_f = f"SELECT NationalTeamPlayers as Jugadores_Seleccion, COUNT(*) as Total_Equipos, ROUND(AVG(CAST(SquadMarketValue AS REAL)), 2) as Valor_Promedio_Millones \nFROM regresion_football \nWHERE {where_cond_f} \nGROUP BY NationalTeamPlayers \nORDER BY Jugadores_Seleccion DESC \nLIMIT 10;"
            st.code(q5_f, language="sql")
            st.dataframe(pd.read_sql_query(q5_f, conexion), use_container_width=True)
            
            st.subheader("7. Indisciplina (Tarjetas Rojas y Amarillas)")
            q7_f = f"SELECT ClubName as Club, CAST(TotalRedCards AS INTEGER) as Rojas, CAST(TotalYellowCards AS INTEGER) as Amarillas, ROUND(CAST(SquadMarketValue AS REAL), 2) as Valor_Millones \nFROM regresion_football \nWHERE {where_cond_f} \nORDER BY Rojas DESC, Amarillas DESC \nLIMIT 10;"
            st.code(q7_f, language="sql")
            st.dataframe(pd.read_sql_query(q7_f, conexion), use_container_width=True)

            st.subheader("9. Estadios más Gigantes y su Cotización")
            q9_f = f"SELECT ClubName as Club, CAST(StadiumCapacity AS INTEGER) as Capacidad_Estadio, ROUND(CAST(SquadMarketValue AS REAL), 2) as Valor_Millones \nFROM regresion_football \nWHERE {where_cond_f} \nORDER BY Capacidad_Estadio DESC \nLIMIT 10;"
            st.code(q9_f, language="sql")
            st.dataframe(pd.read_sql_query(q9_f, conexion), use_container_width=True)

        with col_res2:
            st.subheader("2. Valoración Promedio por Liga")
            q2_f = f"SELECT LeagueName as Liga, COUNT(*) as Equipos_Analizados, ROUND(AVG(CAST(SquadMarketValue AS REAL)),2) as Valor_Promedio_Millones \nFROM regresion_football \nWHERE {where_cond_f} \nGROUP BY LeagueName \nORDER BY Valor_Promedio_Millones DESC \nLIMIT 10;"
            st.code(q2_f, language="sql")
            st.dataframe(pd.read_sql_query(q2_f, conexion), use_container_width=True)

            st.subheader("4. Eficiencia Ofensiva (Goles y Asistencias)")
            q4_f = f"SELECT ClubName as Club, CAST(TotalGoals AS INTEGER) as Goles, CAST(TotalAssists AS INTEGER) as Asistencias, ROUND(CAST(SquadMarketValue AS REAL), 2) as Valor_Millones \nFROM regresion_football \nWHERE {where_cond_f} \nORDER BY Goles DESC \nLIMIT 10;"
            st.code(q4_f, language="sql")
            st.dataframe(pd.read_sql_query(q4_f, conexion), use_container_width=True)

            st.subheader("6. Físico de la Plantilla (Altura y Edad Media)")
            q6_f = f"SELECT LeagueName as Liga, ROUND(AVG(CAST(AveragePlayerHeight AS REAL)), 2) as Altura_Promedio_cm, ROUND(AVG(CAST(AveragePlayerAge AS REAL)), 2) as Edad_Promedio \nFROM regresion_football \nWHERE {where_cond_f} \nGROUP BY LeagueName \nORDER BY Altura_Promedio_cm DESC \nLIMIT 10;"
            st.code(q6_f, language="sql")
            st.dataframe(pd.read_sql_query(q6_f, conexion), use_container_width=True)

            st.subheader("8. Valor Promedio por País")
            q8_f = f"SELECT Country as Pais, COUNT(*) as Equipos, ROUND(AVG(CAST(SquadMarketValue AS REAL)), 2) as Valor_Promedio_Millones \nFROM regresion_football \nWHERE {where_cond_f} \nGROUP BY Country \nORDER BY Valor_Promedio_Millones DESC \nLIMIT 10;"
            st.code(q8_f, language="sql")
            st.dataframe(pd.read_sql_query(q8_f, conexion), use_container_width=True)

            st.subheader("10. Impacto de Partidos Jugados en Resultados")
            q10_f = f"SELECT CAST(MatchesPlayed AS INTEGER) as Partidos_Jugados, ROUND(AVG(CAST(TotalGoals AS REAL)), 2) as Goles_Promedio, ROUND(AVG(CAST(TotalWins AS REAL)), 2) as Victorias_Promedio \nFROM regresion_football \nWHERE {where_cond_f} \nGROUP BY MatchesPlayed \nORDER BY Partidos_Jugados DESC \nLIMIT 10;"
            st.code(q10_f, language="sql")
            st.dataframe(pd.read_sql_query(q10_f, conexion), use_container_width=True)

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# PESTAÑA 2: NHANES (Intacta como la pediste)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
with tab2:
    st.markdown("""<h2 style="margin: 0; padding: 0; line-height: 1; color: #4cc9f0;"> Explorador Metabólico (NHANES)</h2><br>""", unsafe_allow_html=True)
    
    with st.expander("[ PANEL DE FILTROS NHANES ]", expanded=True):
        col1_n, col2_n, col3_n = st.columns(3)
        with col1_n:
            opciones_edad = pd.read_sql_query("SELECT DISTINCT age_group FROM clasificacion_nhanes", conexion)
            filtro_edad = st.multiselect("Grupo de Edad:", opciones_edad['age_group'].tolist(), default=opciones_edad['age_group'].tolist(), key="ms_edad")
            col_orden_n = st.selectbox("Ordenar por:", ["BMXBMI", "LBXGLU", "LBXIN", "RIDAGEYR"], key="sb_n")
            dir_orden_n = st.radio("Dirección:", ["Descendente", "Ascendente"], key="rd_n")
        with col2_n:
            bmi_min, bmi_max = st.slider("IMC (BMI):", 10.0, 60.0, (10.0, 60.0), 1.0, key="bmi_s")
            glu_min, glu_max = st.slider("Glucosa en ayunas:", 50, 250, (50, 250), 5, key="glu_s")
        with col3_n:
            ins_min, ins_max = st.slider("Insulina:", 1.0, 100.0, (1.0, 100.0), 1.0, key="ins_s")
            limite_n = st.number_input("Cantidad:", 1, 6000, 100, key="lim_n")

    if st.button(" Consultar", type="primary", use_container_width=True, key="btn_n"):
        where_cond_n = f"""CAST(BMXBMI AS REAL) BETWEEN {bmi_min} AND {bmi_max} 
                        AND CAST(LBXGLU AS REAL) BETWEEN {glu_min} AND {glu_max} 
                        AND CAST(LBXIN AS REAL) BETWEEN {ins_min} AND {ins_max}"""

        if filtro_edad:
            edades_f = "', '".join(filtro_edad)
            where_cond_n += f"\n  AND age_group IN ('{edades_f}')"
            
        dir_sql_n = "DESC" if dir_orden_n == "Descendente" else "ASC"

        st.subheader("1. Expedientes Clínicos")
        q1_n = f"SELECT * \nFROM clasificacion_nhanes \nWHERE {where_cond_n} \nORDER BY CAST({col_orden_n} AS REAL) {dir_sql_n} \nLIMIT {limite_n};"
        st.code(q1_n, language="sql")
        st.dataframe(pd.read_sql_query(q1_n, conexion), use_container_width=True)

        st.subheader("2. Comparativa por Diagnóstico (DIQ010)")
        q2_n = f"SELECT DIQ010 as Diagnostico, ROUND(AVG(CAST(LBXGLU AS REAL)), 2) as Glucosa_Media, ROUND(AVG(CAST(LBXIN AS REAL)), 2) as Insulina_Media \nFROM clasificacion_nhanes \nWHERE {where_cond_n} \nGROUP BY DIQ010;"
        st.code(q2_n, language="sql")
        st.dataframe(pd.read_sql_query(q2_n, conexion), use_container_width=True)

        st.subheader("3. Impacto del Deporte (PAQ605)")
        q3_n = f"SELECT PAQ605 as Hace_Deporte, COUNT(*) as Pacientes, ROUND(AVG(CAST(BMXBMI AS REAL)), 2) as IMC_Promedio \nFROM clasificacion_nhanes \nWHERE {where_cond_n} \nGROUP BY PAQ605;"
        st.code(q3_n, language="sql")
        st.dataframe(pd.read_sql_query(q3_n, conexion), use_container_width=True)

        st.subheader("4. Distribución por Género y Grupo de Edad")
        q4_n = f"SELECT age_group, RIAGENDR, COUNT(*) as Total \nFROM clasificacion_nhanes \nWHERE {where_cond_n} \nGROUP BY age_group, RIAGENDR \nORDER BY Total DESC;"
        st.code(q4_n, language="sql")
        st.dataframe(pd.read_sql_query(q4_n, conexion), use_container_width=True)

        st.subheader("5. Glucosa Promedio por Edad Exacta")
        q5_n = f"SELECT RIDAGEYR as Edad, ROUND(AVG(CAST(LBXGLU AS REAL)), 2) as Glucosa_Promedio, COUNT(*) as Muestra \nFROM clasificacion_nhanes \nWHERE {where_cond_n} \nGROUP BY RIDAGEYR \nORDER BY CAST(RIDAGEYR AS REAL) ASC;"
        st.code(q5_n, language="sql")
        st.dataframe(pd.read_sql_query(q5_n, conexion), use_container_width=True)

conexion.close()