import pandas as pd
import numpy as np
import sqlite3
from sklearn.impute import KNNImputer

def procesar_jugadores():
    print("Conectando a la base de datos...")
    conn = sqlite3.connect('/root/.openclaw/workspace/proyecto_analitica.db')
    df = pd.read_sql_query('SELECT * FROM jugadores', conn)
    
    print(f"Datos originales: {df.shape[0]} filas.")
    
    # 1. Ordenar cronológicamente para que "last" (último valor) tenga sentido
    df = df.sort_values(by=['player_id', 'fecha_valoracion'])
    
    # 2. Separar numéricas y categóricas
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    num_cols.remove('player_id')
    cat_cols.remove('id_observacion') # El ID original ya no tiene sentido (era Nombre_Año)
    
    # 3. Diccionario de reglas de agregación
    agg_funcs = {}
    
    # Para las numéricas (stats, valor de mercado, edad): sacamos el promedio
    for col in num_cols:
        agg_funcs[col] = 'mean'
        
    # Para las categóricas (nacionalidad, posición, pie hábil): nos quedamos con la más reciente
    for col in cat_cols:
        agg_funcs[col] = 'last'
        
    print("Agrupando y promediando por jugador...")
    df_grouped = df.groupby('player_id').agg(agg_funcs).reset_index()
    print(f"Datos agrupados: {df_grouped.shape[0]} jugadores únicos.")
    
    # 4. Manejo de valores faltantes (NaN)
    # Nota: El promedio (mean) de Pandas ya ignora los NaN automáticamente. 
    # Si un jugador tiene 2 años de datos y 1 año vacío, el promedio se hace sobre los 2 años.
    # El problema ocurre si TODA la historia del jugador es NaN. Para eso usamos KNNImputer.
    faltantes_antes = df_grouped[num_cols].isnull().sum().sum()
    if faltantes_antes > 0:
        print(f"Imputando {faltantes_antes} valores nulos restantes con KNNImputer (vecinos cercanos)...")
        imputer = KNNImputer(n_neighbors=5)
        df_grouped[num_cols] = imputer.fit_transform(df_grouped[num_cols])
    else:
        print("No quedaron valores nulos después del promedio.")
        
    # 5. Guardar el resultado SIN tocar la tabla original
    print("Guardando en la nueva tabla 'jugadores_promediados'...")
    df_grouped.to_sql('jugadores_promediados', conn, if_exists='replace', index=False)
    
    conn.close()
    print("¡Proceso completado exitosamente!")

if __name__ == "__main__":
    procesar_jugadores()
