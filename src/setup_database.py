import pandas as pd
import sqlite3
import os

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# 1. Definimos las rutas (crearemos la carpeta database si no existe)
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(DIR_ACTUAL, "../database/proyecto_analitica.db")

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# Rutas de los archivos CSV originales (Actualizado: Jugadores y Ajedrez):
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

RUTA_JUGADORES = os.path.join(DIR_ACTUAL, "../data/raw/JUGADORES.csv")
RUTA_AJEDREZ = os.path.join(DIR_ACTUAL, "../data/raw/lichess_db_puzzle.csv")

#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#
# Función para la creación de la base de datos
#⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘#

def crear_base_datos():
    
    # 2. Conectamos a SQLite
    conexion = sqlite3.connect(RUTA_DB)
    
    try:
        # 3. Cargar los CSV en Pandas
        print("Cargando JUGADORES.csv...")
        df_jugadores = pd.read_csv(RUTA_JUGADORES, sep=',') 
        
        print("Cargando muestra.csv (Ajedrez)...")
        df_ajedrez = pd.read_csv(RUTA_AJEDREZ, sep=',')
        
        # 4. Enviamos los datos a SQLite creando las tablas con los nombres exactos
        print("Creando tablas en la base de datos...")
        # Guardamos como 'jugadores' y 'muestra' para que coincida con appvis.py
        df_jugadores.to_sql('jugadores', conexion, if_exists='replace', index=False)
        df_ajedrez.to_sql('muestra', conexion, if_exists='replace', index=False)
        
        print("✅ ¡Éxito! Base de datos actualizada con las tablas 'jugadores' y 'muestra' en database/proyecto_analitica.db")
        
    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
        
    finally:
        # Siempre cerramos la conexión
        conexion.close()

if __name__ == "__main__":
    
    # Crear la carpeta database si no existe
    os.makedirs(os.path.join(DIR_ACTUAL, "../database"), exist_ok=True)
    crear_base_datos()