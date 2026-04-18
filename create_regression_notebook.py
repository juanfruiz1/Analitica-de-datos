import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

nb = new_notebook()

# Celda 1: Título y descripción
nb.cells.append(new_markdown_cell("""# EDA Regresión - Datos Promediados de Jugadores

Este notebook utiliza la tabla `jugadores_promediados` (jugadores únicos con estadísticas promediadas a lo largo de su carrera) para predecir el valor de mercado (`valor_mercado_eur_TARGET`).

**Objetivos:**
1. Cargar la base de datos promediada.
2. Explorar distribuciones y correlaciones.
3. Aplicar transformación logarítmica al target (debido a la alta asimetría).
4. Preparar datos para modelado (train/test split).
"""))

# Celda 2: Importaciones
nb.cells.append(new_code_cell("""import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
warnings.filterwarnings('ignore')"""))

# Celda 3: Cargar datos
nb.cells.append(new_code_cell("""# Ruta a la base de datos
ruta_db = "../database/proyecto_analitica.db"
conn = sqlite3.connect(ruta_db)
df = pd.read_sql_query("SELECT * FROM jugadores_promediados", conn)
conn.close()
print("✅ Datos cargados. Dimensiones:", df.shape)
df.head()"""))

# Celda 4: Identificar variables
nb.cells.append(new_code_cell("""# Identificamos numéricas y categóricas
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = df.select_dtypes(include=['object']).columns.tolist()

# player_id es identificador, no predictora
if 'player_id' in num_cols:
    num_cols.remove('player_id')

print("Variables numéricas:", num_cols)
print("Variables categóricas:", cat_cols)
print("Target:", 'valor_mercado_eur_TARGET')"""))

# Celda 5: Estadísticas descriptivas
nb.cells.append(new_code_cell("""desc_num = df[num_cols].describe().T
desc_num['mediana'] = df[num_cols].median()
desc_num = desc_num[['mean', 'mediana', 'std', 'min', 'max']]
print("Estadísticas numéricas:")
display(desc_num.round(2))"""))

# Celda 6: Distribución del target (original y log-transformado)
nb.cells.append(new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Target original
axes[0].hist(df['valor_mercado_eur_TARGET'], bins=50, edgecolor='black', alpha=0.7)
axes[0].set_title('Distribución original del valor de mercado')
axes[0].set_xlabel('Valor (€)')
axes[0].set_ylabel('Frecuencia')

# Target log-transformado (para reducir asimetría)
df['log_valor_mercado'] = np.log1p(df['valor_mercado_eur_TARGET'])
axes[1].hist(df['log_valor_mercado'], bins=50, edgecolor='black', alpha=0.7, color='orange')
axes[1].set_title('Distribución log-transformada (log1p)')
axes[1].set_xlabel('log(1 + Valor)')
axes[1].set_ylabel('Frecuencia')

plt.tight_layout()
plt.show()

print("Asimetría (skewness) original:", df['valor_mercado_eur_TARGET'].skew())
print("Asimetría después de log1p:", df['log_valor_mercado'].skew())"""))

# Celda 7: Valores faltantes
nb.cells.append(new_code_cell("""faltantes = df.isnull().sum()
faltantes_cols = faltantes[faltantes > 0]

if faltantes_cols.empty:
    print("¡No hay valores faltantes en el dataset promediado!")
else:
    print(faltantes_cols)
    print(f"\\nPorcentaje de datos faltantes:\\n{(faltantes_cols / len(df) * 100).round(2)}%")"""))

# Celda 8: Correlaciones numéricas (con target log-transformado)
nb.cells.append(new_code_cell("""# Matriz de correlación (solo numéricas)
corr_matrix = df[num_cols + ['log_valor_mercado']].corr()
target_corr = corr_matrix['log_valor_mercado'].drop('log_valor_mercado').sort_values(ascending=False)

print("Correlación con target log-transformado:")
print(target_corr.round(3))

plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', center=0)
plt.title('Matriz de correlación (variables numéricas)')
plt.show()"""))

# Celda 9: Preparación para modelado (train/test split)
nb.cells.append(new_code_cell("""# Definir features y target (usaremos el log-transformado como target para el modelo)
X = df.drop(columns=['valor_mercado_eur_TARGET', 'log_valor_mercado', 'player_id'])
y = df['log_valor_mercado']

# Separar en train y test (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Train: {X_train.shape}, Test: {X_test.shape}")"""))

# Celda 10: Pipeline de preprocesamiento
nb.cells.append(new_code_cell("""# Identificar columnas numéricas y categóricas después de quitar columnas eliminadas
num_features = X_train.select_dtypes(include=[np.number]).columns.tolist()
cat_features = X_train.select_dtypes(include=['object']).columns.tolist()

print("Numeric features:", num_features)
print("Categorical features:", cat_features)

# Preprocesador
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, num_features),
        ('cat', categorical_transformer, cat_features)
    ])

print("Preprocesador creado exitosamente.")"""))

# Celda 11: Guardar el notebook
nb.cells.append(new_markdown_cell("""## Próximos pasos

Este notebook ha preparado los datos para modelado. En un siguiente notebook (`02_modeling.ipynb`) se pueden entrenar modelos de regresión (Linear Regression, Random Forest, XGBoost) usando el preprocesador definido.

**Nota importante:** Recordar que las predicciones del modelo estarán en escala logarítmica. Para obtener el valor en euros, hay que aplicar la transformación inversa: `np.expm1(prediccion_log)`.
"""))

# Escribir notebook
with open('/root/.openclaw/workspace/Analitica-de-datos/notebooks/eda_regresion_promediados.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook creado en 'notebooks/eda_regresion_promediados.ipynb'")