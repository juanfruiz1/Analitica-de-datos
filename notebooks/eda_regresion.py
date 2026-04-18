#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from scipy import stats
warnings.filterwarnings('ignore')

# Ruta a la base de datos
ruta_db = "../database/proyecto_analitica.db"

conn = sqlite3.connect(ruta_db)

df = pd.read_sql_query("SELECT * FROM jugadores", conn)
conn.close()

print("✅ Datos cargados. Dimensiones:", df.shape)
df.head()

# In[2]:


# Identificamos numéricas y categóricas
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = df.select_dtypes(include=['object']).columns.tolist()

# Limpiar: id_observacion, player_id, fecha_valoracion no son predictoras
id_cols = ['id_observacion', 'player_id', 'fecha_valoracion']
num_cols = [c for c in num_cols if c not in id_cols]
cat_cols = [c for c in cat_cols if c not in id_cols]

print("Variables numéricas:", num_cols)
print("Variables categóricas:", cat_cols)
print("Target:", 'valor_mercado_eur_TARGET')

# In[4]:


desc_num = df[num_cols].describe().T
desc_num['mediana'] = df[num_cols].median()
desc_num = desc_num[['mean', 'mediana', 'std', 'min', 'max']]
print("Estadísticas numéricas:")
display(desc_num.round(2))

# In[5]:


import math
n_vars = len(num_cols)
n_rows = math.ceil(n_vars / 4)
fig, axes = plt.subplots(n_rows, 4, figsize=(20, n_rows*4))
axes = axes.flatten()
for i, col in enumerate(num_cols):
    sns.histplot(df[col], kde=True, ax=axes[i], bins=30, color='steelblue')
    axes[i].set_title(col)
for j in range(i+1, len(axes)):
    axes[j].set_visible(False)
plt.tight_layout()
plt.show()

# In[6]:


print("🔍 Detección de outliers (IQR):")
for col in num_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5*IQR
    upper = Q3 + 1.5*IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    print(f"{col}: {len(outliers)} outliers ({len(outliers)/len(df)*100:.2f}%)")

# Boxplots de las principales (evita saturar)
main_cols = ['valor_mercado_eur_TARGET', 'edad_al_momento', 'minutos_jugados_12m', 
             'goles_12m', 'valor_maximo_historico_previo']
fig, axes = plt.subplots(1, 5, figsize=(20, 4))
for i, col in enumerate(main_cols):
    sns.boxplot(y=df[col], ax=axes[i], color='lightcoral')
    axes[i].set_title(col)
plt.tight_layout()
plt.show()

# In[7]:


corr_matrix = df[num_cols].corr()
plt.figure(figsize=(14, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap='coolwarm', 
            square=True, linewidths=0.5)
plt.title("Matriz de correlación - Variables numéricas")
plt.show()

# Correlación con el target (ordenada)
corr_target = corr_matrix['valor_mercado_eur_TARGET'].sort_values(ascending=False)
print("Correlación con el target (valor_mercado_eur_TARGET):")
print(corr_target)

# In[8]:


# ================================
# 6. RELACIONES (scatter plots vs target)
# ================================
top3 = corr_target.index[1:4]  # las 3 más correlacionadas (excluyendo el propio target)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for i, col in enumerate(top3):
    sns.regplot(data=df, x=col, y='valor_mercado_eur_TARGET', ax=axes[i],
                scatter_kws={'alpha':0.4}, line_kws={'color':'red'})
    axes[i].set_title(f"{col} vs Valor de mercado")
plt.tight_layout()
plt.show()

# In[10]:


# Importar librerías necesarias
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer # Necesario para IterativeImputer
from sklearn.impute import IterativeImputer
import matplotlib.pyplot as plt
import seaborn as sns

# In[5]:


import pandas as pd
import sqlite3
import numpy as np

ruta_db = "../database/proyecto_analitica.db"
conn = sqlite3.connect(ruta_db)
df = pd.read_sql_query("SELECT * FROM jugadores", conn)
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = df.select_dtypes(include=['object']).columns.tolist()
conn.close()


# In[6]:


# ==========================================
# 1. IDENTIFICAR VALORES FALTANTES
# ==========================================
print("--- Conteo de Valores Faltantes ---")
faltantes = df.isnull().sum()
faltantes_cols = faltantes[faltantes > 0]

if faltantes_cols.empty:
    print("¡No hay valores faltantes en el dataset!")
else:
    print(faltantes_cols)
    print(f"\nPorcentaje de datos faltantes:\n{(faltantes_cols / len(df) * 100).round(2)}%")

# Solo procedemos si hay numéricas con NAs (evitamos romper el código con categóricas)
cols_imputar = [col for col in faltantes_cols.index if col in num_cols]

if cols_imputar:
    # ==========================================
    # 2. APLICAR DOS MÉTODOS DE IMPUTACIÓN
    # ==========================================
    print("\nIniciando imputación...")
    
    # Copias para no afectar el dataset original de MOMENTO
    df_imputado_mediana = df.copy()
    df_imputado_knn = df.copy()
    
    # Método A: Tendencia Central (Mediana es más robusta a outliers que la media)
    imputer_mediana = SimpleImputer(strategy='median')
    df_imputado_mediana[cols_imputar] = imputer_mediana.fit_transform(df[cols_imputar])
    
    # Método B: KNN Imputer (Usa IterativeImputer si tu RAM colapsa en el de ajedrez)
    # imputer_avanzado = IterativeImputer(max_iter=10, random_state=42) # Alternativa rápida
    imputer_avanzado = KNNImputer(n_neighbors=5)
    df_imputado_knn[cols_imputar] = imputer_avanzado.fit_transform(df[cols_imputar])
    print("Imputación finalizada.")

    # ==========================================
    # 3. COMPARAR RESULTADOS (Antes y Después)
    # ==========================================
    print("\n--- Comparación de Estadísticas Descriptivas ---")
    for col in cols_imputar:
        print(f"\nVariable: {col}")
        comp_df = pd.DataFrame({
            'Original (con NAs)': df[col].describe(),
            'Imputado Mediana': df_imputado_mediana[col].describe(),
            'Imputado KNN': df_imputado_knn[col].describe()
        })
        display(comp_df.round(2))
        
        # Comparación visual (Distribución KDE)
        plt.figure(figsize=(10, 5))
        sns.kdeplot(data=df, x=col, label='Original', fill=True, alpha=0.3, color='blue')
        sns.kdeplot(data=df_imputado_mediana, x=col, label='Mediana', fill=False, color='red', linestyle='--')
        sns.kdeplot(data=df_imputado_knn, x=col, label='KNN', fill=False, color='green', linestyle=':')
        plt.title(f"Impacto de la imputación en la distribución de '{col}'")
        plt.legend()
        plt.show()
        


# Tras evaluar el impacto de ambos métodos en la distribución de las variables numéricas, se determina que el método de imputación multivariable (KNN Imputer) es el más adecuado por lo siguientes motivos:
# 
# Preservación de la varianza: En variables con un porcentaje significativo de datos faltantes, como dias_para_fin_contrato (11.98%) y altura_cm (2.27%), la imputación por la Mediana genera una distorsión crítica en la distribución de los datos. Como se observa en los gráficos KDE, la mediana inyecta miles de valores idénticos en la "mitad"
# 
# Reconstrucción contextual: KNN Imputer logra imputar los valores ausentes calculando distancias con los "vecinos más cercanos". Esto significa que si a un jugador le falta la estatura, el modelo buscará a otros jugadores con edad, posición o características físicas similares para estimarla.
# 
# Mantiene mejor la distribución original

# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import SimpleImputer
# Importes para habilitar el KNN Multihilo
from sklearn.experimental import enable_iterative_imputer 
from sklearn.impute import IterativeImputer
from sklearn.neighbors import KNeighborsRegressor

# ==========================================
# 0. IMPUTACIÓN DE VARIABLES CATEGÓRICAS
# ==========================================
print("--- 1. Imputando variables categóricas (Vía Moda) ---")

# 1. Guardamos copias estrictas para graficar el "Antes"
cols_cat = ['pie_habil', 'nacionalidad', 'liga_actual']
df_cat_original = df[cols_cat].copy() if set(cols_cat).issubset(df.columns) else pd.DataFrame()

# 2. Imputación por Moda para TODAS las solicitadas
for col in cols_cat:
    if col in df.columns:
        moda_val = df[col].mode()[0]
        df[col] = df[col].fillna(moda_val)

print("✅ Imputación categórica lista. Nulos restantes:")
print(df[cols_cat].isnull().sum() if not df_cat_original.empty else "Columnas no encontradas.")
print("\n")

# 3. Función de Gráficos Panorámicos Oscuros
def graficar_categorica_completa(columna):
    # Figura vertical gigante para acomodar decenas/cientos de categorías
    fig, axes = plt.subplots(2, 1, figsize=(18, 14)) 
    
    # Ordenamos por las categorías más frecuentes en el original para mantener consistencia
    orden = df_cat_original[columna].fillna('FALTANTES').value_counts().index
    
    # Gráfico 1: Antes (Azul oscuro profundo)
    sns.countplot(
        data=df_cat_original.fillna({columna: 'FALTANTES'}), 
        x=columna, 
        ax=axes[0], 
        order=orden, 
        color='#023047' 
    )
    axes[0].set_title(f'ANTES: {columna} (Con Nulos)', fontsize=16, fontweight='bold')
    axes[0].tick_params(axis='x', rotation=90, labelsize=8)
    axes[0].set_ylabel('Cantidad')
    
    # Gráfico 2: Después (Rojo oscuro profundo)
    sns.countplot(
        data=df, 
        x=columna, 
        ax=axes[1], 
        order=orden, 
        color='#780000' 
    )
    axes[1].set_title(f'DESPUÉS: {columna} (Imputado con Moda)', fontsize=16, fontweight='bold')
    axes[1].tick_params(axis='x', rotation=90, labelsize=8)
    axes[1].set_ylabel('Cantidad')
    
    plt.tight_layout()
    plt.show()

# Lanzar los gráficos si las columnas existen
if not df_cat_original.empty:
    for col in cols_cat:
        graficar_categorica_completa(col)

# ==========================================
# 1. IDENTIFICAR VALORES FALTANTES (NUMÉRICAS)
# ==========================================
print("--- 2. Conteo de Valores Faltantes (Numéricas) ---")
faltantes = df.isnull().sum()
faltantes_cols = faltantes[faltantes > 0]

if faltantes_cols.empty:
    print("¡No hay valores faltantes numéricos en el dataset!")
else:
    print(faltantes_cols)
    print(f"\nPorcentaje de datos faltantes:\n{(faltantes_cols / len(df) * 100).round(2)}%")

# Salvavidas para memoria del Notebook
if 'num_cols' not in locals():
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

cols_imputar = [col for col in faltantes_cols.index if col in num_cols]

if cols_imputar:
    # ==========================================
    # 2. APLICAR DOS MÉTODOS DE IMPUTACIÓN
    # ==========================================
    print("\n--- 3. Iniciando imputación de variables numéricas ---")
    
    df_imputado_mediana = df.copy()
    df_imputado_knn = df.copy()
    
    # Método A: Mediana
    imputer_mediana = SimpleImputer(strategy='median')
    df_imputado_mediana[cols_imputar] = imputer_mediana.fit_transform(df[cols_imputar])
    
    # Método B: KNN Multihilo (Uso de todos los núcleos del CPU)
    print("⏳ Calculando KNN usando todos los núcleos del procesador (n_jobs=-1)...")
    imputer_avanzado = IterativeImputer(
        estimator=KNeighborsRegressor(n_neighbors=5, n_jobs=-1),
        max_iter=10,
        random_state=42
    )
    df_imputado_knn[cols_imputar] = imputer_avanzado.fit_transform(df[cols_imputar])
    print("✅ Imputación numérica multihilo finalizada.")

    # ==========================================
    # 3. COMPARAR RESULTADOS (Antes y Después)
    # ==========================================
    print("\n--- 4. Comparación de Estadísticas Descriptivas ---")
    for col in cols_imputar:
        print(f"\n================ Variable: {col} ================")
        comp_df = pd.DataFrame({
            'Original (con NAs)': df[col].describe(),
            'Imputado Mediana': df_imputado_mediana[col].describe(),
            'Imputado KNN Multi': df_imputado_knn[col].describe()
        })
        display(comp_df.round(2))
        
        # Comparación visual (KDE con colores oscuros y marcados)
        plt.figure(figsize=(12, 6))
        sns.kdeplot(data=df, x=col, label='Original', fill=True, alpha=0.3, color='#1b4965')
        sns.kdeplot(data=df_imputado_mediana, x=col, label='Mediana', fill=False, color='#d62828', linewidth=2.5, linestyle='--')
        sns.kdeplot(data=df_imputado_knn, x=col, label='KNN (Multi-Core)', fill=False, color='#2a9d8f', linewidth=2.5, linestyle=':')
        
        plt.title(f"Impacto de la imputación en la distribución de '{col}'", fontsize=14, fontweight='bold')
        plt.legend(fontsize=12)
        plt.show()

# # 9. Conclusiones Finales del Análisis Exploratorio (EDA)
# 
# A partir de las pruebas de asociación y dependencia, se extraen las siguientes conclusiones determinantes para la fase de modelado predictivo:
# 
# * **La "Inercia" del Mercado:** La correlación de Spearman confirma contundentemente la Hipótesis 1. El `valor_maximo_historico_previo` es, con muchísima diferencia, el mejor predictor numérico del valor actual (0.82). Así el mercado futbolístico tiene una fuerte memoria estocástica; el estatus previo de un jugador amortigua las caídas de precio frente a un mal rendimiento reciente o posterior.
# 
# * **Regularidad vs. Explosividad:** variables de volumen de juego (`partidos_jugados_12m`, `minutos_jugados_12m` con ~0.52) tienen mayor correlación con el precio que las variables de acierto directo (`goles_12m`, `asistencias_12m` con ~0.45). El mercado valora más la consistencia y la disponibilidad física que los destellos puntuales.
# 
# * **Desmitificación de variables físicas y demográficas:** Atributos como la `altura_cm` (-0.04) o el `mes_de_nacimiento` (0.02) son irrelevantes a la hora de explicar la varianza del precio, descartando efectos como el sesgo de edad relativa en el mercado de élite.
# 
# * **El Contexto como Multiplicador del Valor:** La prueba de Kruskal-Wallis arrojó un p-valor de 0.0 para todas las variables categóricas (`liga_actual`, `nacionalidad`, `posicion_principal`). Esto valida la Hipótesis 3: el valor de un jugador no es un atributo numérico aislado de su rendimiento, sino una construcción fuertemente segmentada por la jerarquía económica de la liga en la que juega y posiblemente la escasez táctica de su rol.
# 
# * **Tratamiento de nulos en variables cualitativas:** la ausencia de información puede ser un dato en sí mismo. En el caso de liga_actual (16.25% de nulos), evitar la imputación por Moda y optar por una categoría constante (`Sin Equipo`) fue crucial para no inflar artificialmente el valor de agentes libres asignándoles ligas de élite. Por otro lado, la imputación por Moda en `pie_habil` y `nacionalidad` asumió una distribución alineada a la mayoría poblacional
# 
