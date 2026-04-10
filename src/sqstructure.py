import sqlite3
import pandas as pd
import os

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(DIR_ACTUAL, "../database/proyecto_analitica.db")

conn = sqlite3.connect(db_path)

# 1. Le decimos que mire la NUEVA tabla
nombre_tabla = 'muestra_procesada'

print(f"\n=== ESTRUCTURA DE LA TABLA: {nombre_tabla} ===")
info_columnas = pd.read_sql_query(f"PRAGMA table_info({nombre_tabla});", conn)

# 2. Mostramos TODAS las columnas para que veas que pasaste de 10 a 16
print(info_columnas[['name', 'type']])

print("\n=== MUESTRA DE DATOS (3 filas) ===")
pd.set_option('display.max_columns', None) 
pd.set_option('display.width', 1000)
datos = pd.read_sql_query(f"SELECT * FROM {nombre_tabla} LIMIT 3;", conn)

# 3. Imprimimos los datos
print(datos)

conn.close()