import pandas as pd
import os

# Configuramos la ruta dinámica
DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATOS = os.path.join(DIR_ACTUAL, "../datax")

print("🔍 ESCANEANDO ABSOLUTAMENTE TODAS LAS BASES DE DATOS...\n")

# Python lee la carpeta y saca una lista automática de todos los .csv.gz
archivos_a_escanear = [f for f in os.listdir(CARPETA_DATOS) if f.endswith('.csv.gz')]

# Ordenamos la lista alfabéticamente para que sea más fácil de leer
archivos_a_escanear.sort()

#ME QUIERO MORIR

for archivo in archivos_a_escanear:
    ruta_completa = os.path.join(CARPETA_DATOS, archivo)
    
    try:
        # Leemos solo la fila de títulos
        df_scan = pd.read_csv(ruta_completa, compression='gzip', nrows=0)
        
        print(f"📄 Archivo: {archivo}")
        print(f"📊 Total de columnas: {len(df_scan.columns)}")
        
        # Imprimimos la lista de columnas
        for col in df_scan.columns:
            print(f"   - {col}")
        print("-" * 40 + "\n")
        
    except Exception as e:
        print(f"❌ No se pudo leer {archivo}: {e}\n")