import streamlit as st
import base64
from streamlit_option_menu import option_menu
import time  # Necesario para el loader
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
# ==========================================
# 2. CARGA DE MODELOS (Caché para mayor velocidad)
# ==========================================
@st.cache_resource
def cargar_modelos():
    import os
    
    # Obtiene la ruta de la carpeta 'src' (donde está este script lab4.py)
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Construimos las rutas hacia las dos carpetas distintas basándonos en tu foto
    ruta_notebooks = os.path.join(directorio_actual, '../notebooks')
    ruta_models = os.path.join(directorio_actual, '../models')
    
    # Apuntamos a los modelos en la carpeta 'notebooks'
    ruta_ridge = os.path.join(ruta_notebooks, 'mejor_modelo_ridge_optimizado.pkl')
    ruta_rf = os.path.join(ruta_notebooks, 'mejor_modelo_rf_optimizado.pkl')
    
    # Apuntamos a las características en la carpeta 'models'
    ruta_features = os.path.join(ruta_models, 'features_regression.joblib')
    
    # Cargamos usando las rutas exactas
    ridge = joblib.load(ruta_ridge)
    rf = joblib.load(ruta_rf)
    features = joblib.load(ruta_features)
    
    return ridge, rf, features

# Ejecutamos la función y guardamos los modelos en variables
mejor_ridge, mejor_rf, all_features = cargar_modelos()

# 1. Configuración básica de la página (opcional, pero recomendada)
st.set_page_config(page_title="App con Fondo ASCII", layout="wide")

def aplicar_fondo_webp(ruta_archivo):
    """
    Lee un archivo WebP, lo codifica en base64 y lo inyecta como 
    fondo de pantalla completa mediante CSS.
    """
    try:
        with open(ruta_archivo, "rb") as f:
            datos_imagen = f.read()
            
        imagen_base64 = base64.b64encode(datos_imagen).decode()
        
        # Inyección de CSS
        # background-size: cover -> Ajusta la imagen para cubrir toda la pantalla
        # background-attachment: fixed -> El fondo se queda quieto si haces scroll
        css_fondo = f"""
        <style>
        /* 1. El fondo animado que ya tenías */
        .stApp {{
            background-image: url("data:image/webp;base64,{imagen_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* 2. Ocultar la barra superior (Deploy, Menú, etc.) */
        [data-testid="stHeader"] {{
            visibility: hidden;
        }}
        
        /* 3. Opcional: Ocultar el footer que dice "Made with Streamlit" al final de la página */
        [data-testid="stFooter"] {{
            visibility: hidden;
        }}
        
        /* 4. Opcional: Reducir el espacio en blanco que deja la barra superior al desaparecer */
        .block-container {{
            padding-top: 2rem; 
        }}
        </style>
        """
        st.markdown(css_fondo, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error(f"No se pudo encontrar el archivo de fondo en la ruta: {ruta_archivo}")

# --- EJECUCIÓN ---
# Llamamos a la función apuntando al archivo que generaste con el script anterior
aplicar_fondo_webp("src/ascii_fondo_color_extremo.webp")

# 1. Configuración inicial
st.set_page_config(page_title="Reporte Lab 4", layout="wide", initial_sidebar_state="collapsed")

# 2. Renderizar la barra de navegación (ARREGLO DE TEXTO Y TAMAÑOS)
seccion = option_menu(
    menu_title=None,
    # Acortamos palabras muy largas para evitar que se rompa en dos líneas
    options=["Inicio", "Datos", "Modelos", "Evaluación", "Interpretabilidad", "Residuos", "Simulador"],
    icons=["house", "gear", "bar-chart", "bullseye", "brain", "graph-down", "calculator"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "transparent", "border": "none"},
        "icon": {"color": "#E2E8F0", "font-size": "16px"}, 
        "nav-link": {
            "font-size": "14px", # Letra un poco más pequeña para que encaje perfecto
            "text-align": "center", 
            "margin": "0px", 
            "color": "#E2E8F0", 
            "--hover-color": "rgba(255, 255, 255, 0.1)"
        },
        "nav-link-selected": {
            "background-color": "rgba(255, 255, 255, 0.15)", 
            "color": "#FFFFFF", 
            "border-radius": "10px" # Bordes redondeados para quitar ese corte recto raro
        },
    }
)

# ==============================================================================
# Lógica de las Secciones con la "Ruedita"
# ==============================================================================

# Creamos un contenedor vacío temporal
espacio_carga = st.empty()

# Mostramos la ruedita DENTRO del contenedor temporal
with espacio_carga.container():
    with st.spinner("Cargando módulo..."):
        time.sleep(0.6) # Medio segundo para que gire la ruedita

# Borramos la ruedita vaciando el contenedor
espacio_carga.empty()

# --- A PARTIR DE AQUÍ CARGA EL CONTENIDO REAL ---

if seccion == "Inicio":
    st.markdown("""<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px;">
<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 10px; letter-spacing: 1px; font-weight: 400;">Análisis de Valor de Mercado de Jugadores</h1>
<h3 style="color: #94A3B8; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 40px; font-weight: 300;">1. Comprensión del Problema</h3>

<div style="display: flex; gap: 20px; justify-content: center; align-items: stretch; flex-wrap: wrap;">

<!-- Tarjeta A -->
<div style="flex: 1; min-width: 250px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
<div style="width: 35px; height: 35px; border-radius: 50%; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; color: #E2E8F0; font-weight: bold; font-size: 14px;">A</div>
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px;">Variable Objetivo</h4>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; margin-bottom: 15px;">
<code style="color: #38BDF8; font-size: 15px;">valor_mercado_eur_TARGET</code>
</div>
<p style="font-size: 15px; line-height: 1.6; color: #cbd5e1; margin: 0;">Valor de mercado estimado en euros de un jugador de fútbol.</p>
</div>

<!-- Tarjeta B -->
<div style="flex: 1; min-width: 250px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
<div style="width: 35px; height: 35px; border-radius: 50%; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; color: #E2E8F0; font-weight: bold; font-size: 14px;">B</div>
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px;">Tipo de Regresión</h4>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; margin-bottom: 15px;">
<span style="color: #38BDF8; font-size: 16px; font-family: monospace;">Regresión Múltiple</span>
</div>
<p style="font-size: 15px; line-height: 1.6; color: #cbd5e1; margin: 0;">Predicción de una variable continua apoyándose en la combinación de múltiples variables predictoras.</p>
</div>

<!-- Tarjeta C -->
<div style="flex: 1; min-width: 250px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
<div style="width: 35px; height: 35px; border-radius: 50%; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; color: #E2E8F0; font-weight: bold; font-size: 14px;">C</div>
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px;">Contexto</h4>
<p style="font-size: 15px; line-height: 1.6; color: #cbd5e1; margin: 0;">El objetivo de este proyecto es predecir el precio en euros a partir de un conjunto diverso de características (numéricas, discretas y categóricas).</p>
</div>

</div>
</div>""", unsafe_allow_html=True)

elif seccion == "Datos":
    st.markdown("""<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px;">
<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 10px; letter-spacing: 1px; font-weight: 400;">Limpieza y Preparación de Datos</h1>
<h3 style="color: #94A3B8; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 40px; font-weight: 300;">2. Preprocesamiento Seguro mediante Pipelines</h3>

<div style="display: flex; gap: 20px; justify-content: center; align-items: stretch; flex-wrap: wrap; margin-bottom: 30px;">

<!-- Tarjeta 1: Partición -->
<div style="flex: 1; min-width: 250px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
<div style="width: 35px; height: 35px; border-radius: 50%; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; color: #E2E8F0; font-weight: bold; font-size: 14px;">1</div>
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px;">Partición de Datos</h4>
<p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-bottom: 15px;">Eliminamos las variables identificadoras (<code style="color:#38BDF8; background:transparent; font-size:13px;">id_observacion</code>, <code style="color:#38BDF8; background:transparent; font-size:13px;">player_id</code> y <code style="color:#38BDF8; background:transparent; font-size:13px;">fecha_valoracion</code>) porque no aportan poder predictivo. Luego, dividimos el dataset:</p>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
<span style="color: #38BDF8; font-size: 15px; font-weight: bold;">Train (70%) - Test (30%)</span>
</div>
</div>

<!-- Tarjeta 2: Numéricas -->
<div style="flex: 1; min-width: 250px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
<div style="width: 35px; height: 35px; border-radius: 50%; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; color: #E2E8F0; font-weight: bold; font-size: 14px;">2</div>
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px;">Variables Numéricas</h4>
<p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-bottom: 10px;">Para proteger la varianza original, imputamos los valores faltantes estimándolos con los vecinos más cercanos en lugar de usar la mediana global.</p>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.05);">
<code style="color: #38BDF8; font-size: 13px; font-family: monospace;">KNNImputer(n_neighbors=5)</code>
</div>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
<code style="color: #38BDF8; font-size: 13px; font-family: monospace;">StandardScaler()</code>
</div>
</div>

<!-- Tarjeta 3: Categóricas -->
<div style="flex: 1; min-width: 250px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 30px 20px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
<div style="width: 35px; height: 35px; border-radius: 50%; background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); display: inline-flex; align-items: center; justify-content: center; margin: 0 auto 20px auto; color: #E2E8F0; font-weight: bold; font-size: 14px;">3</div>
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px;">Variables Categóricas</h4>
<p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin-bottom: 10px;"> Rellenamos datos faltantes con "Sin Equipo" y usamos el Encoder para transformar los textos en columnas binarias (OneHotEncoder).</p>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.05);">
<code style="color: #38BDF8; font-size: 13px; font-family: monospace;">SimpleImputer('Sin Equipo')</code>
</div>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
<code style="color: #38BDF8; font-size: 13px; font-family: monospace;">OneHotEncoder()</code>
</div>
</div>

</div>

<!-- Banner inferior aclaratorio -->
<div style="background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-left: 4px solid #38BDF8; border-radius: 8px; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
<p style="font-size: 15px; margin: 0; color: #cbd5e1;">
<span style="font-weight: bold; color: #38BDF8;">Integración Segura:</span> Todas estas transformaciones se ensamblaron dentro de un <code style="color: #E2E8F0; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; font-size: 14px;">ColumnTransformer</code> y se ejecutaron mediante un <code style="color: #E2E8F0; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; font-size: 14px;">Pipeline</code> para garantizar que no existiera <span style="color:#FFFFFF; font-weight:600;">fuga de información (Data Leakage)</span>.
</p>
</div>

</div>""", unsafe_allow_html=True)

elif seccion == "Modelos":
    # 1. Encabezado en HTML
    st.markdown("""<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px;">
<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 10px; letter-spacing: 1px; font-weight: 400;">Validación Cruzada (K-Fold)</h1>
<h3 style="color: #94A3B8; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 30px; font-weight: 300;">3. Comparación de Múltiples Algoritmos</h3>
</div>""", unsafe_allow_html=True)

    # 2. Reconstrucción de tu tabla de resultados
    resultados_cv = [
        {'Modelo': 'XGBoost', 'MAE (CV)': 786409.18, 'MAE Std': 18109.17, 'RMSE (CV)': 2097613.50, 'RMSE Std': 69534.77, 'R^2 (CV)': 0.9378},
        {'Modelo': 'Random Forest', 'MAE (CV)': 836509.78, 'MAE Std': 18268.55, 'RMSE (CV)': 2222411.32, 'RMSE Std': 64779.74, 'R^2 (CV)': 0.9301},
        {'Modelo': 'LightGBM', 'MAE (CV)': 914647.90, 'MAE Std': 20565.22, 'RMSE (CV)': 2300125.56, 'RMSE Std': 85297.96, 'R^2 (CV)': 0.9251},
        {'Modelo': 'Árbol de Decisión', 'MAE (CV)': 977022.03, 'MAE Std': 15408.28, 'RMSE (CV)': 2893811.60, 'RMSE Std': 107961.98, 'R^2 (CV)': 0.8811},
        {'Modelo': 'Ridge', 'MAE (CV)': 2018556.80, 'MAE Std': 13907.19, 'RMSE (CV)': 4254025.04, 'RMSE Std': 118840.18, 'R^2 (CV)': 0.7440},
        {'Modelo': 'Regresión Lineal', 'MAE (CV)': 2018877.44, 'MAE Std': 13725.83, 'RMSE (CV)': 4254027.37, 'RMSE Std': 118778.87, 'R^2 (CV)': 0.7440},
        {'Modelo': 'LASSO', 'MAE (CV)': 2018880.99, 'MAE Std': 13723.17, 'RMSE (CV)': 4254028.54, 'RMSE Std': 118780.25, 'R^2 (CV)': 0.7440}
    ]
    
    import pandas as pd
    df_comparacion = pd.DataFrame(resultados_cv)
    
    st.dataframe(df_comparacion, use_container_width=True, hide_index=True)

    # 3. Explicación de Métricas de Validación Cruzada (K-Fold) y Ejemplo Práctico
    st.markdown("""<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px; margin-top: 20px;">
<div style="background-color: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 25px; margin-bottom: 30px;">
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 20px; font-weight: 500; font-size: 18px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Desglose de las Columnas (Validación Cruzada K-Fold)</h4>
<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 25px;">
<div style="flex: 1; min-width: 250px; background-color: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border-left: 3px solid #38BDF8;">
<p style="margin: 0 0 10px 0;"><span style="color: #38BDF8; font-weight: bold; font-size: 16px;">MAE (CV) y MAE Std</span></p>
<p style="font-size: 14px; color: #cbd5e1; margin: 0 0 8px 0; line-height: 1.5;"><strong style="color: #E2E8F0;">MAE (CV):</strong> El promedio del Error Absoluto tras evaluar el modelo 5 veces con datos distintos. Indica por cuántos euros se equivoca en promedio.</p>
<p style="font-size: 14px; color: #cbd5e1; margin: 0; line-height: 1.5;"><strong style="color: #E2E8F0;">MAE Std:</strong> La desviación estándar de ese error. Nos dice si el error se mantuvo estable en las 5 pruebas o si varió bruscamente.</p>
</div>
<div style="flex: 1; min-width: 250px; background-color: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border-left: 3px solid #A855F7;">
<p style="margin: 0 0 10px 0;"><span style="color: #A855F7; font-weight: bold; font-size: 16px;">RMSE (CV) y RMSE Std</span></p>
<p style="font-size: 14px; color: #cbd5e1; margin: 0 0 8px 0; line-height: 1.5;"><strong style="color: #E2E8F0;">RMSE (CV):</strong> Promedio de la Raíz del Error Cuadrático.</p>
<p style="font-size: 14px; color: #cbd5e1; margin: 0; line-height: 1.5;"><strong style="color: #E2E8F0;">RMSE Std:</strong> Mide cuánto varió el RMSE entre los 5 pliegues. Es la métrica a tener en cuenta para calificar el modelo mas estable <strong>estable</strong>.</p>
</div>
<div style="flex: 1; min-width: 200px; background-color: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border-left: 3px solid #10B981;">
<p style="margin: 0 0 10px 0;"><span style="color: #10B981; font-weight: bold; font-size: 16px;">R² (CV)</span></p>
<p style="font-size: 14px; color: #cbd5e1; margin: 0; line-height: 1.5;"><strong style="color: #E2E8F0;">Coeficiente de Determinación:</strong> El porcentaje de éxito general en los 5 pliegues. Un 0.93 significa que el modelo logra explicar el 93% de las razones por las que un jugador vale lo que vale.</p>
</div>
</div>
<div style="background-color: rgba(56, 189, 248, 0.1); border-left: 4px solid #38BDF8; padding: 15px; border-radius: 6px;">
<p style="font-size: 15px; margin: 0; color: #E2E8F0;"><strong style="color: #38BDF8;">Ejemplo Práctico en Contexto:</strong> Si miramos a XGBoost y Random Forest, ambos tienen un RMSE casi idéntico (~2 millones de euros penalizados). Sin embargo, el Random Forest tiene un <strong style="color: #FFFFFF;">RMSE Std menor (64,779 vs 69,534)</strong>. Esto significa que el modelo de Random Forest es ligeramente más confiable, por lo que es el modelo mas estable.</p>
</div>
</div>
<div style="display: flex; gap: 20px; justify-content: center; align-items: stretch; flex-wrap: wrap;">
<div style="flex: 1; min-width: 300px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 25px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px;">¿Qué modelo es más estable?</h4>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;">
<span style="color: #38BDF8; font-size: 16px; font-weight: bold;">Random Forest</span>
</div>
<p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin: 0;">Al evaluar la métrica de <code style="color: #38BDF8; background: transparent; font-size: 14px;">RMSE Std</code>, el Random Forest presentó la variación más pequeña (64,779) entre todos los modelos complejos, demostrando un rendimiento sumamente consistente a través de todos los pliegues de la validación cruzada.</p>
</div>
<div style="flex: 1; min-width: 300px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 25px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.5);">
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px;">¿Cuál presenta mayor varianza?</h4>
<div style="background-color: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;">
<span style="color: #A855F7; font-size: 16px; font-weight: bold;">Árbol de Decisión / Modelos Lineales</span>
</div>
<p style="font-size: 14px; line-height: 1.6; color: #cbd5e1; margin: 0;">El Árbol de Decisión exhibe una alta varianza (<code style="color: #A855F7; background: transparent; font-size: 14px;">RMSE Std: 107,961</code>).</p>
</div>
</div>
</div>""", unsafe_allow_html=True)

elif seccion == "Evaluación":
    st.markdown("""<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px;">
<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 10px; letter-spacing: 1px; font-weight: 400;">Resultados en Test (Hold-Out)</h1>
<h3 style="color: #94A3B8; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 30px; font-weight: 300;">4. Ajuste de Hiperparámetros y Prueba Final</h3>

<!-- Explicación de Hiperparámetros -->
<div style="background-color: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 25px; margin-bottom: 30px;">
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 15px; font-weight: 500; font-size: 18px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">¿Por qué ajustar los hiperparámetros?</h4>
<p style="font-size: 14px; color: #cbd5e1; margin-bottom: 15px; line-height: 1.6;">
Un Random Forest por defecto crece sus árboles hasta el infinito, lo que causa una memorización extrema de los datos de entrenamiento (Overfitting). Para evitar esto, utilizamos <code style="color: #38BDF8; background: transparent; font-size: 14px;">RandomizedSearchCV</code> para encontrar límites que fuercen al modelo a generalizar. La mejor configuración encontrada fue:
</p>
<div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
<span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 6px; color: #E2E8F0; font-size: 13px; font-family: monospace;">n_estimators: 200</span>
<span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 6px; color: #E2E8F0; font-size: 13px; font-family: monospace;">max_depth: 20</span>
<span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 6px; color: #E2E8F0; font-size: 13px; font-family: monospace;">max_features: 'sqrt'</span>
<span style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 6px; color: #E2E8F0; font-size: 13px; font-family: monospace;">min_samples_split: 2</span>
</div>
</div>

<!-- Tarjetas de Evaluación -->
<div style="display: flex; gap: 20px; justify-content: center; align-items: stretch; flex-wrap: wrap; margin-bottom: 30px;">

<!-- Tarjeta Ridge (Soberbia y apagada) -->
<div style="flex: 1; min-width: 300px; background-color: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
<div style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px;">
<h4 style="color: #94A3B8; margin: 0 0 5px 0; font-weight: 500; font-size: 20px;">Ridge (Optimizado)</h4>
<span style="color: #64748b; font-size: 14px;">Modelo Lineal Base</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
<span style="color: #94A3B8; font-size: 15px;">RMSE (Validación Cruzada):</span>
<span style="color: #cbd5e1; font-family: monospace; font-size: 15px;">4,255,674 €</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
<span style="color: #94A3B8; font-size: 15px;">RMSE (Hold-Out / Test):</span>
<span style="color: #cbd5e1; font-family: monospace; font-size: 15px;">4,201,788 €</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-top: 12px; border-top: 1px dashed rgba(255,255,255,0.05);">
<span style="color: #94A3B8; font-size: 15px;">Brecha de Generalización:</span>
<span style="color: #cbd5e1; font-size: 15px;">1.26 %</span>
</div>
<div style="display: flex; justify-content: space-between;">
<span style="color: #94A3B8; font-size: 15px;">R² (Test):</span>
<span style="color: #cbd5e1; font-size: 15px;">0.7484</span>
</div>
</div>

<!-- Tarjeta Random Forest (Resaltada sutilmente en cian/blanco) -->
<div style="flex: 1; min-width: 300px; background-color: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.5); border-radius: 12px; padding: 25px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); position: relative;">
<div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background-color: #38BDF8; color: #0f172a; padding: 4px 15px; border-radius: 20px; font-weight: bold; font-size: 12px; letter-spacing: 1px;">MODELO DEFINITIVO</div>
<div style="text-align: center; margin-bottom: 20px; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 15px;">
<h4 style="color: #FFFFFF; margin: 0 0 5px 0; font-weight: 500; font-size: 22px;">Random Forest</h4>
<span style="color: #38BDF8; font-size: 14px;">Ensamble de Árboles de Decisión</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
<span style="color: #cbd5e1; font-size: 15px;">RMSE (Validación Cruzada):</span>
<span style="color: #E2E8F0; font-weight: bold; font-family: monospace; font-size: 15px;">3,003,924 €</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
<span style="color: #cbd5e1; font-size: 15px;">RMSE (Hold-Out / Test):</span>
<span style="color: #E2E8F0; font-weight: bold; font-family: monospace; font-size: 16px;">2,978,307 €</span>
</div>
<div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-top: 12px; border-top: 1px dashed rgba(255,255,255,0.1);">
<span style="color: #cbd5e1; font-size: 15px;">Brecha de Generalización:</span>
<span style="color: #38BDF8; font-weight: bold; font-size: 15px;">0.85 %</span>
</div>
<div style="display: flex; justify-content: space-between;">
<span style="color: #cbd5e1; font-size: 15px;">R² (Test):</span>
<span style="color: #FFFFFF; font-weight: bold; font-size: 16px;">0.8736 (87.3%)</span>
</div>
</div>

</div>

<!-- Explicación de la Evaluación Final -->
<div style="background-color: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.1); border-left: 4px solid #E2E8F0; padding: 20px; border-radius: 8px;">
<h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 10px; font-size: 18px; font-weight: 500;">Interpretación de la Prueba de Fuego (Test Hold-Out)</h4>
<p style="font-size: 14px; margin: 0 0 10px 0; color: #cbd5e1; line-height: 1.6;">
El conjunto de <strong style="color: #FFFFFF;">Test (Hold-Out)</strong> representa el 30% de los datos originales que aislamos al principio del laboratorio. El modelo jamás vio esta información durante su entrenamiento ni durante la búsqueda de hiperparámetros. 
</p>
<p style="font-size: 14px; margin: 0; color: #cbd5e1; line-height: 1.6;">
Al comparar el error simulado en entrenamiento (<code style="color: #38BDF8; background: transparent;">3.00 M€</code>) contra el error en este examen final ciego (<code style="color: #38BDF8; background: transparent;">2.97 M€</code>), observamos una brecha de apenas <strong style="color: #FFFFFF;">0.85%</strong>. Esta similitud milimétrica muestra que la configuración de hiperparámetros fue exitosa: el Random Forest no sobreajustó (memorizó) los datos, sino que aprendió "reglas" del mercado de fichajes con una precisión del 87.3%.
</p>
</div>

</div>""", unsafe_allow_html=True)

elif seccion == "Interpretabilidad":
    st.markdown("""<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px;">
<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 10px; letter-spacing: 1px; font-weight: 400;">¿Qué variables definen el precio?</h1>
<h3 style="color: #94A3B8; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 30px; font-weight: 300;">5. Interpretabilidad</h3>
<div style="background-color: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 20px; margin-bottom: 30px; text-align: center;">
<p style="font-size: 15px; color: #cbd5e1; margin: 0; line-height: 1.6;">No basta con que un modelo tenga buenas métricas; debemos entender <strong>cómo toma sus decisiones</strong>. Aquí analizamos los factores que cada algoritmo consideró más importantes para tasar a los jugadores.</p>
</div>
</div>""", unsafe_allow_html=True)

    # Importamos las librerías de visualización
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # ¡TRUCO DE DISEÑO! Forzamos a Matplotlib a usar un tema oscuro nativo
    plt.style.use('dark_background')

    # Usamos columnas nativas de Streamlit para poner ambas explicaciones lado a lado
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""<div style="background-color: rgba(15, 23, 42, 0.85); border-top: 4px solid #A855F7; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); height: 280px;">
<h4 style="color: #A855F7; margin-top: 0; margin-bottom: 15px; font-size: 19px;">Ridge: WTF</h4>
<p style="font-size: 14px; color: #cbd5e1; margin: 0; line-height: 1.6; text-align: justify;">Los modelos lineales asignan un peso estático a cada variable. Se observa cómo el modelo le dio una importancia colosal a nacionalidades como <strong>Bahréin, Vanuatu o Qatar</strong>. Al haber poquísimos jugadores de esos países, el modelo memorizó sus precios y asumió que <em>nacer allí te hace valer cierta cantidad</em>. Esta falta de lógica evidencia por qué los modelos lineales no son tan buenos en nuestro contexto.</p>
</div>""", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # CÓDIGO PYTHON PARA EL GRÁFICO DE RIDGE (Adaptado a Dark Mode)
        # ---------------------------------------------------------
        # Asumiendo que ya tienes cargados: mejor_ridge, all_features
        coefs = mejor_ridge.named_steps['regressor'].coef_
        df_coefs = pd.DataFrame({'Variable': all_features, 'Coeficiente': coefs})
        df_coefs = df_coefs.sort_values(by='Coeficiente', ascending=False)
        
        fig1, ax1 = plt.subplots(figsize=(8, 10))
        # Hacemos el fondo de la figura transparente para que se vea el fondo de Streamlit
        fig1.patch.set_alpha(0.0) 
        ax1.set_alpha(0.0)
        
        sns.barplot(x='Coeficiente', y='Variable', data=df_coefs.head(20), ax=ax1, color="#A855F7")
        plt.title('Top 20 Coeficientes Positivos - Ridge', color='white', pad=20)
        plt.xlabel('Peso en Euros (€)', color='#94A3B8')
        plt.ylabel('')
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        
        # Mostramos el gráfico en Streamlit
        st.pyplot(fig1)


    with col2:
        st.markdown("""<div style="background-color: rgba(15, 23, 42, 0.85); border-top: 4px solid #38BDF8; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); height: 280px;">
<h4 style="color: #38BDF8; margin-top: 0; margin-bottom: 15px; font-size: 19px;">Random Forest: Lógica de Mercado Real</h4>
<p style="font-size: 14px; color: #cbd5e1; margin: 0; line-height: 1.6; text-align: justify;">Los árboles de decisión sí logran capturar mejor la naturaleza del mercado de fichajes. Podemos observar cómo el algoritmo ignoró las nacionalidades raras y le otorgó el poder predictivo a las variables que realmente dictan el mercado: <strong>el valor histórico del jugador, su presencia en la selección nacional, y sus minutos/goles jugados en los últimos 12 meses</strong>.</p>
</div>""", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # CÓDIGO PYTHON PARA EL GRÁFICO DE RANDOM FOREST (Dark Mode)
        # ---------------------------------------------------------
        # Asumiendo que ya tienes cargados: mejor_rf, all_features
        importances = mejor_rf.named_steps['regressor'].feature_importances_
        df_importances = pd.DataFrame({'Variable': all_features, 'Importancia': importances})
        df_importances = df_importances.sort_values(by='Importancia', ascending=False)
        
        fig2, ax2 = plt.subplots(figsize=(8, 10))
        fig2.patch.set_alpha(0.0)
        ax2.set_alpha(0.0)
        
        sns.barplot(x='Importancia', y='Variable', data=df_importances.head(15), ax=ax2, color="#38BDF8")
        plt.title('Top 15 Variables más Importantes - Random Forest', color='white', pad=20)
        plt.xlabel('Nivel de Importancia (0 a 1)', color='#94A3B8')
        plt.ylabel('')
        plt.grid(axis='x', linestyle='--', alpha=0.3)
        
        # Mostramos el gráfico en Streamlit
        st.pyplot(fig2)

elif seccion == "Residuos":
    st.markdown("""<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px;">
<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 10px; letter-spacing: 1px; font-weight: 400;">Análisis de Residuos (Errores del Modelo)</h1>
<h3 style="color: #94A3B8; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 30px; font-weight: 300;">6. Evaluando la Confianza de las Predicciones</h3>
</div>""", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # FUNCIÓN PARA CARGAR LOS DATOS Y CALCULAR RESIDUOS (CON CACHÉ)
    # ---------------------------------------------------------
    @st.cache_data
    def obtener_residuos_test():
        import sqlite3
        import pandas as pd
        from sklearn.model_selection import train_test_split
        import os
        
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_db = os.path.join(directorio_actual, '../database/proyecto_analitica.db')
        
        conn = sqlite3.connect(ruta_db)
        df = pd.read_sql_query("SELECT * FROM jugadores", conn)
        conn.close()
        
        columnas_a_eliminar = ['valor_mercado_eur_TARGET', 'id_observacion', 'player_id', 'fecha_valoracion']
        X = df.drop(columns=columnas_a_eliminar)
        y = df['valor_mercado_eur_TARGET']
        
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.30, random_state=42)
        
        predicciones = mejor_rf.predict(X_test)
        residuos = y_test - predicciones
        
        return predicciones, residuos

    with st.spinner('Calculando matriz de residuos sobre el conjunto de prueba...'):
        predicciones_rf, residuos_rf = obtener_residuos_test()

    # ---------------------------------------------------------
    # GRÁFICO DE DISPERSIÓN (EL EMBUDO) - 100% TRANSPARENTE
    # ---------------------------------------------------------
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.ticker import FuncFormatter

    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 1. Forzamos el fondo a ser "nada" (transparente)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')

    # 2. Pintamos los bordes (spines) de un gris muy sutil
    for spine in ax.spines.values():
        spine.set_edgecolor((1.0, 1.0, 1.0, 0.2)) # Blanco (R,G,B) con 20% de opacidad

    # 3. Gráfico de dispersión con cian brillante y opacidad para ver superposiciones
    sns.scatterplot(x=predicciones_rf, y=residuos_rf, alpha=0.5, color='#38BDF8', ax=ax, edgecolor=None)
    
    # 4. Línea ideal (Error cero) en rojo/rosado
    ax.axhline(y=0, color='#F43F5E', linestyle='--', linewidth=2)
    
    # 5. Formateo de ejes a Millones
    def millions_formatter(x, pos):
        return f'{x / 1e6:.0f}M'
    ax.xaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    # 6. Colores de textos alineados a la paleta corporativa del dashboard
    ax.set_title('Predicciones vs Residuos (Random Forest)', color='#FFFFFF', pad=15, fontsize=15)
    ax.set_xlabel('Valor Predicho de Mercado (Euros)', color='#94A3B8', fontsize=12)
    ax.set_ylabel('Residuos (Error de Predicción)', color='#94A3B8', fontsize=12)
    ax.tick_params(colors='#cbd5e1', labelsize=11)
    
    # 7. Cuadrícula blanca muy transparente
    ax.grid(True, linestyle=':', alpha=0.15, color='#FFFFFF')

    # 8. IMPORTANTE: Mandar a Streamlit con transparent=True
    st.pyplot(fig, transparent=True)

    # ---------------------------------------------------------
    # EXPLICACIÓN DEL NEGOCIO (HETEROCEDASTICIDAD)
    # ---------------------------------------------------------
    st.markdown("""<div style="display: flex; gap: 20px; justify-content: center; align-items: stretch; flex-wrap: wrap; margin-top: 30px;">

<div style="flex: 1; min-width: 300px; background-color: rgba(15, 23, 42, 0.85); border-left: 4px solid #10B981; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
<h4 style="color: #10B981; margin-top: 0; margin-bottom: 15px; font-size: 18px;">La Zona de Alta Precisión (0 a 25 Millones)</h4>
<p style="font-size: 14px; color: #cbd5e1; margin: 0; line-height: 1.6; text-align: justify;">
Si observamos el lado izquierdo del gráfico, la enorme mayoría de los puntos (jugadores regulares) están densamente agrupados alrededor de la línea roja punteada (error igual a cero). Esto indica que el modelo es preciso tasando jugadores de bajo y medio perfil, ya que sus precios obedecen estrictamente a sus estadísticas deportivas.
</p>
</div>

<div style="flex: 1; min-width: 300px; background-color: rgba(15, 23, 42, 0.85); border-left: 4px solid #F43F5E; border-radius: 8px; padding: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
<h4 style="color: #F43F5E; margin-top: 0; margin-bottom: 15px; font-size: 18px;">El Efecto "Embudo" (Heterocedasticidad)</h4>
<p style="font-size: 14px; color: #cbd5e1; margin: 0; line-height: 1.6; text-align: justify;">
A medida que avanzamos hacia la derecha (jugadores de más de 50 millones), el gráfico se abre formando un embudo. Las estrellas mundiales son casos atípicos: sus precios no solo dependen de sus goles, sino del marketing, derechos de imagen y el poder de negociación de sus agentes. Como el modelo no tiene estos datos no deportivos, su margen de error (varianza) aumenta inevitablemente.
</p>
</div>

</div>""", unsafe_allow_html=True)

elif seccion == "Simulador":
    st.markdown("""<div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px;">
<h1 style="color: #FFFFFF; text-align: center; margin-bottom: 10px; letter-spacing: 1px; font-weight: 400;">Simulador de Tasación</h1>
<h3 style="color: #94A3B8; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 30px; font-weight: 300;">Pronóstico en Tiempo Real (Random Forest)</h3>
<p style="text-align: center; color: #cbd5e1; margin-bottom: 30px;">Ingresa las métricas del jugador para estimar su valor de mercado actual en euros según los patrones detectados por el modelo ganador.</p>
</div>""", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # DICCIONARIO TRADUCTOR DE LIGAS (Para la Interfaz)
    # ---------------------------------------------------------
    diccionario_ligas = {
        "GB1": "Premier League (Inglaterra)",
        "ES1": "LaLiga (España)",
        "IT1": "Serie A (Italia)",
        "L1":  "Bundesliga (Alemania)",
        "FR1": "Ligue 1 (Francia)",
        "PO1": "Liga Portugal (Portugal)",
        "NL1": "Eredivisie (Países Bajos)",
        "BRA1": "Brasileirão (Brasil)",
        "ARG1": "Liga Profesional (Argentina)",
        "COL1": "Liga BetPlay (Colombia)",
        "MEX1": "Liga MX (México)",
        "MLS1": "MLS (Estados Unidos)",
        "SA1": "Saudi Pro League (Arabia Saudita)",
        "TR1": "Süper Lig (Turquía)",
        "BE1": "Jupiler Pro League (Bélgica)",
        "GR1": "Super League (Grecia)",
        "DK1": "Superliga (Dinamarca)",
        "SC1": "Premiership (Escocia)",
        "UKR1": "Premier League (Ucrania)",
        "RU1": "Premier Liga (Rusia)",
        "JAP1": "J1 League (Japón)",
        "KR1": "K League 1 (Corea del Sur)",
        "AUS1": "A-League (Australia)",
        "SE1": "Allsvenskan (Suecia)",
        "NO1": "Eliteserien (Noruega)",
        "PL1": "Ekstraklasa (Polonia)",
        "RO1": "SuperLiga (Rumania)",
        "A1":  "Bundesliga (Austria)",
        "C1":  "Super League (Suiza)",
        "Sin Equipo": "Sin Equipo"
    }

    # ---------------------------------------------------------
    # EXTRACCIÓN DINÁMICA DE CATEGORÍAS (CON CACHÉ)
    # ---------------------------------------------------------
    @st.cache_data
    def obtener_categorias_db():
        import sqlite3
        import pandas as pd
        import os
        
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_db = os.path.join(directorio_actual, '../database/proyecto_analitica.db')
        
        conn = sqlite3.connect(ruta_db)
        df_cat = pd.read_sql_query("SELECT pie_habil, posicion_principal, nacionalidad, liga_actual FROM jugadores", conn)
        conn.close()
        
        nacionalidades = sorted([str(n) for n in df_cat['nacionalidad'].unique() if pd.notna(n)])
        ligas = sorted([str(l) for l in df_cat['liga_actual'].unique() if pd.notna(l)])
        posiciones = sorted([str(p) for p in df_cat['posicion_principal'].unique() if pd.notna(p)])
        pies = sorted([str(p) for p in df_cat['pie_habil'].unique() if pd.notna(p)])
        
        if "Sin Equipo" not in ligas:
            ligas.insert(0, "Sin Equipo")
            
        return pies, posiciones, nacionalidades, ligas

    with st.spinner("Cargando base de datos mundial..."):
        lista_pies, lista_posiciones, lista_nacionalidades, lista_ligas = obtener_categorias_db()

    # Creamos un formulario
    with st.form("simulador_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<h4 style='color: #38BDF8; border-bottom: 1px solid rgba(56, 189, 248, 0.3); padding-bottom: 8px;'>Perfil del Jugador</h4>", unsafe_allow_html=True)
            edad = st.number_input("Edad al momento", min_value=15, max_value=45, value=25)
            mes_nacimiento = st.number_input("Mes de Nacimiento (1-12)", min_value=1, max_value=12, value=6)
            altura = st.number_input("Altura (cm)", min_value=150, max_value=210, value=180)
            
            pie = st.selectbox("Pie Hábil", lista_pies)
            posicion = st.selectbox("Posición Principal", lista_posiciones) 
            
            idx_nacion = lista_nacionalidades.index("Colombia") if "Colombia" in lista_nacionalidades else 0
            nacionalidad = st.selectbox("Nacionalidad", lista_nacionalidades, index=idx_nacion)

        with col2:
            st.markdown("<h4 style='color: #A855F7; border-bottom: 1px solid rgba(168, 85, 247, 0.3); padding-bottom: 8px;'>Rendimiento (Últimos 12m)</h4>", unsafe_allow_html=True)
            partidos = st.number_input("Partidos Jugados", min_value=0, max_value=70, value=35)
            minutos = st.number_input("Minutos Jugados", min_value=0, max_value=6000, value=2500)
            goles = st.number_input("Goles", min_value=0, max_value=60, value=8)
            asistencias = st.number_input("Asistencias", min_value=0, max_value=40, value=5)
            participacion = st.number_input("Participación Goles p/90", min_value=0.0, max_value=3.0, value=0.45, format="%.2f")
            amarillas = st.number_input("Tarjetas Amarillas", min_value=0, max_value=30, value=4)
            rojas = st.number_input("Tarjetas Rojas", min_value=0, max_value=10, value=0)

        with col3:
            st.markdown("<h4 style='color: #10B981; border-bottom: 1px solid rgba(16, 185, 129, 0.3); padding-bottom: 8px;'>Mercado y Selección</h4>", unsafe_allow_html=True)
            
            idx_liga = lista_ligas.index("GB1") if "GB1" in lista_ligas else 0
            
            # MAGIA AQUÍ: Usamos format_func para traducir los códigos visualmente
            liga = st.selectbox(
                "Liga Actual", 
                lista_ligas, 
                index=idx_liga,
                format_func=lambda x: diccionario_ligas.get(x, x) # Si no está en el dict, muestra el código normal
            )
            
            dias_contrato = st.number_input("Días para fin de contrato", min_value=0, max_value=3000, value=365)
            valor_historico = st.number_input("Valor Máx. Histórico Previo (€)", min_value=0, max_value=200000000, value=5000000, step=500000)
            partidos_sel = st.number_input("Partidos Selección (12m)", min_value=0, max_value=20, value=3)
            convocatorias_sel = st.number_input("Convocatorias Históricas Sel.", min_value=0, max_value=150, value=12)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.form_submit_button(label="🔮 Calcular Valor de Mercado", use_container_width=True)

    if submit_button:
        import pandas as pd
        input_data = pd.DataFrame({
            'edad_al_momento': [edad],
            'mes_de_nacimiento': [mes_nacimiento],
            'altura_cm': [altura],
            'minutos_jugados_12m': [minutos],
            'partidos_jugados_12m': [partidos],
            'goles_12m': [goles],
            'asistencias_12m': [asistencias],
            'tarjetas_amarillas_12m': [amarillas],
            'tarjetas_rojas_12m': [rojas],
            'participacion_goles_p90': [participacion],
            'partidos_seleccion_12m': [partidos_sel],
            'convocatorias_historicas_seleccion': [convocatorias_sel],
            'dias_para_fin_contrato': [dias_contrato],
            'valor_maximo_historico_previo': [valor_historico],
            'pie_habil': [pie],
            'posicion_principal': [posicion],
            'nacionalidad': [nacionalidad],
            'liga_actual': [liga] # ¡Se guarda 'GB1' para el modelo, no 'Premier League'!
        })

        precio_predicho = mejor_rf.predict(input_data)[0]
        precio_predicho = max(0, precio_predicho)

        st.markdown(f"""<div style="background-color: rgba(16, 185, 129, 0.1); border: 2px solid #10B981; border-radius: 12px; padding: 40px; text-align: center; margin-top: 20px; box-shadow: 0 0 30px rgba(16, 185, 129, 0.3);">
        <h3 style="color: #cbd5e1; margin-top: 0; margin-bottom: 15px; font-weight: 400; font-size: 20px;">Valor de Mercado Estimado</h3>
        <h1 style="color: #10B981; font-size: 55px; margin: 0; font-weight: bold; letter-spacing: 2px;">€ {precio_predicho:,.0f}</h1>
        <p style="color: #94A3B8; margin-top: 15px; font-size: 15px;">Basado en la evaluación de 18 variables independientes mediante Random Forest.</p>
        </div>""", unsafe_allow_html=True)