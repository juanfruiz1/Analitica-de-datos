import streamlit as st
import streamlit.components.v1 as components
import base64
import pandas as pd
import sqlite3
import os

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 1. Configuración de página
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

st.set_page_config(page_title="Dashboard Clínico", layout="wide", initial_sidebar_state="collapsed")

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
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# Diseño CSS
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: transparent !important;
}

/* 1. Contenedores de "cristal" con contorno AZUL NEÓN */
[data-testid="stExpander"], .stDataFrame, div[data-testid="stMetric"], .stTabs {
    background-color: rgba(15, 20, 30, 0.6) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 15px !important; 
    /* Cambiamos el gris por un azul neón sutil (0.3 de opacidad para que no perturbe la vista y me de algo) */
    border: 1px solid rgba(0, 229, 255, 0.3) !important; 
}

/* 2. ESPACIADO PARA LAS PESTAÑAS (Tabs) */
/* Añadimos margen arriba y a la izquierda para que el texto no choque y se vea horrible */
.stTabs {
    padding-top: 15px !important;
    padding-left: 15px !important;
    padding-right: 15px !important;
}

/* Opcional: Cambiar la línea inferior de las pestañas que suele ser gris */
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
        <h1 style="margin: 0; padding: 0; line-height: 1;"> Consultor de Análisis Clínico: BPN y NHANES</h1>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Regresión (Bajo Peso al Nacer)", "Clasificación (Salud NHANES)"])

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# PESTAÑA 1: BPN
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
with tab1:
    st.markdown("""<h2 style="margin: 0; padding: 0; line-height: 1; color: #4cc9f0;"> Monitor de Partos (BPN)</h2><br>""", unsafe_allow_html=True)
    
    with st.expander("[ Panel de Filtros BPN ]", expanded=True):
        col1_b, col2_b, col3_b = st.columns(3)
        with col1_b:
            opciones_sexo = pd.read_sql_query("SELECT DISTINCT sexo_ FROM regresion_bpn", conexion)
            filtro_sexo = st.multiselect("Sexo del Bebé:", opciones_sexo['sexo_'].dropna().tolist(), default=opciones_sexo['sexo_'].dropna().tolist())
            columna_orden_b = st.selectbox("Ordenar por:", ["peso_nacer", "talla_nacer", "sem_gest", "edad_"])
            tipo_orden_b = st.radio("Dirección:", ["Descendente", "Ascendente"], key="dir_b")
        with col2_b:
            peso_min, peso_max = st.slider("Peso al nacer (gramos):", 500, 5000, (500, 5000), 100)
            edad_min, edad_max = st.slider("Edad de la Madre (Años):", 10, 55, (10, 55), 1)
        with col3_b:
            sem_min, sem_max = st.slider("Semanas de Gestación:", 20, 45, (20, 45), 1)
            limite_b = st.number_input("Límite de registros:", 1, 5000, 100)

    if st.button(" Consultar ", type="primary", use_container_width=True, key="btn_bpn"):
        
        #⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
        # APLICAMOS EL CAST(columna AS REAL) PARA EVITAR EL ERRORES QUE SURGIERON (ME KIERO MATAR)
        #⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
        
        where_cond_b = f"""CAST(peso_nacer AS REAL) BETWEEN {peso_min} AND {peso_max} 
                        AND CAST(edad_ AS REAL) BETWEEN {edad_min} AND {edad_max} 
                        AND CAST(sem_gest AS REAL) BETWEEN {sem_min} AND {sem_max}"""
        
        if filtro_sexo:
            sexos_f = "', '".join(filtro_sexo)
            where_cond_b += f"\n  AND sexo_ IN ('{sexos_f}')"
            
        dir_sql_b = "DESC" if tipo_orden_b == "Descendente" else "ASC"

        #⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
        #ESTAS SON REALMENTE NUESTRAS CONSULTAS
        #⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
        
        st.subheader("1. Base de Datos Filtrada")
        q1_b = f"SELECT * \nFROM regresion_bpn \nWHERE {where_cond_b} \nORDER BY CAST({columna_orden_b} AS REAL) {dir_sql_b} \nLIMIT {limite_b};"
        st.code(q1_b, language="sql")
        st.dataframe(pd.read_sql_query(q1_b, conexion), use_container_width=True)

        st.subheader("2. Frecuencia de Casos por Comuna")
        q2_b = f"SELECT comuna, COUNT(*) as Total_Nacimientos, ROUND(AVG(CAST(peso_nacer AS REAL)),2) as Peso_Medio \nFROM regresion_bpn \nWHERE {where_cond_b} \nGROUP BY comuna \nORDER BY Total_Nacimientos DESC \nLIMIT 5;"
        st.code(q2_b, language="sql")
        st.dataframe(pd.read_sql_query(q2_b, conexion), use_container_width=True)

        st.subheader("3. Impacto del Tipo de Seguridad Social")
        q3_b = f"SELECT tipo_ss_, COUNT(*) as Registros, ROUND(AVG(CAST(sem_gest AS REAL)), 1) as Promedio_Semanas \nFROM regresion_bpn \nWHERE {where_cond_b} \nGROUP BY tipo_ss_;"
        st.code(q3_b, language="sql")
        st.dataframe(pd.read_sql_query(q3_b, conexion), use_container_width=True)

        st.subheader("4. Relación: Edad de Madre vs Peso (Ordenado por Edad)")
        q4_b = f"SELECT edad_, COUNT(*) as Casos, ROUND(AVG(CAST(peso_nacer AS REAL)), 2) as Peso_Promedio \nFROM regresion_bpn \nWHERE {where_cond_b} \nGROUP BY edad_ \nORDER BY CAST(edad_ AS REAL) ASC;"
        st.code(q4_b, language="sql")
        st.dataframe(pd.read_sql_query(q4_b, conexion), use_container_width=True)

        st.subheader("5. Casos por Nivel Educativo de la Madre")
        q5_b = f"SELECT niv_edu_ma, COUNT(*) as Total_Casos \nFROM regresion_bpn \nWHERE {where_cond_b} \nGROUP BY niv_edu_ma \nORDER BY Total_Casos DESC;"
        st.code(q5_b, language="sql")
        st.dataframe(pd.read_sql_query(q5_b, conexion), use_container_width=True)


#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# PESTAÑA 2: NHANES
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

    if st.button(" Ejecutar Consultas Médicas", type="primary", use_container_width=True, key="btn_n"):
        
        # APLICAMOS EL CAST(columna AS REAL) TAMBIÉN AQUÍ
        where_cond_n = f"""CAST(BMXBMI AS REAL) BETWEEN {bmi_min} AND {bmi_max} 
                        AND CAST(LBXGLU AS REAL) BETWEEN {glu_min} AND {glu_max} 
                        AND CAST(LBXIN AS REAL) BETWEEN {ins_min} AND {ins_max}"""

        if filtro_edad:
            edades_f = "', '".join(filtro_edad)
            where_cond_n += f"\n  AND age_group IN ('{edades_f}')"
            
        dir_sql_n = "DESC" if dir_orden_n == "Descendente" else "ASC"

        #⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
        #ESTAS SON REALMENTE NUESTRAS CONSULTAS
        #⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
        
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