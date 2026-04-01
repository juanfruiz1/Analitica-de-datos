import pandas as pd
import numpy as np # Importamos numpy para usar np.nan
import os

# ⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘ #
# ⚙️ CONFIGURACIÓN DE RUTAS QUE NO JODE LA VIDA
# ⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘ #
DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
CARPETA_ENTRADA = os.path.join(DIR_ACTUAL, "../datax") 
ARCHIVO_SALIDA = os.path.join(DIR_ACTUAL, "../data/raw/FTP.csv")

def construir_dataset():
    print("🚀 Iniciando Integración Avanzada (Con Filtro de Ceros Falsos)...")
    
    try:
        print("⏳ Leyendo tablas comprimidas...")
        df_clubs = pd.read_csv(os.path.join(CARPETA_ENTRADA, 'clubs.csv.gz'), compression='gzip')
        df_comps = pd.read_csv(os.path.join(CARPETA_ENTRADA, 'competitions.csv.gz'), compression='gzip')
        df_players = pd.read_csv(os.path.join(CARPETA_ENTRADA, 'players.csv.gz'), compression='gzip')
        df_club_games = pd.read_csv(os.path.join(CARPETA_ENTRADA, 'club_games.csv.gz'), compression='gzip')
        df_appearances = pd.read_csv(os.path.join(CARPETA_ENTRADA, 'appearances.csv.gz'), compression='gzip')

        print("⏳ Calculando Edades y VALOR TOTAL DEL CLUB...")
        df_players['date_of_birth'] = pd.to_datetime(df_players['date_of_birth'], errors='coerce')
        df_players['age'] = pd.Timestamp.today().year - df_players['date_of_birth'].dt.year

        stats_plantilla = df_players.groupby('current_club_id').agg(
            AveragePlayerAge=('age', 'mean'),
            AveragePlayerHeight=('height_in_cm', 'mean'),
            TotalPlayers=('player_id', 'count'),
            SquadMarketValue=('market_value_in_eur', 'sum') 
        ).reset_index()

        stats_plantilla = stats_plantilla[stats_plantilla['SquadMarketValue'] > 0]

        print("⏳ Calculando rendimiento deportivo (Victorias, EMPATES y DERROTAS)...")
        df_club_games['is_draw'] = (df_club_games['own_goals'] == df_club_games['opponent_goals']).astype(int)
        df_club_games['is_loss'] = (df_club_games['own_goals'] < df_club_games['opponent_goals']).astype(int)

        stats_juegos = df_club_games.groupby('club_id').agg(
            TotalGoals=('own_goals', 'sum'),
            TotalWins=('is_win', 'sum'),
            TotalDraws=('is_draw', 'sum'), 
            TotalLosses=('is_loss', 'sum'), 
            MatchesPlayed=('game_id', 'count')
        ).reset_index()

        print("⏳ Calculando asistencias y tarjetas (Respetando nulos)...")
        stats_apariciones = df_appearances.groupby('player_club_id').agg(
            TotalYellowCards=('yellow_cards', 'sum'),
            TotalRedCards=('red_cards', 'sum'),
            TotalAssists=('assists', 'sum'),
            TotalMinutesPlayed=('minutes_played', 'sum')
        ).reset_index()

        print("⏳ Uniendo todas las bases de datos...")
        df_master = pd.merge(
            df_clubs, 
            df_comps[['competition_id', 'name', 'country_name']], 
            left_on='domestic_competition_id', 
            right_on='competition_id', 
            how='inner' 
        )

        df_master = pd.merge(df_master, stats_plantilla, left_on='club_id', right_on='current_club_id', how='inner')
        df_master = pd.merge(df_master, stats_juegos, on='club_id', how='left')
        df_master = pd.merge(df_master, stats_apariciones, left_on='club_id', right_on='player_club_id', how='left')

        print("⏳ Puliendo detalles finales...")
        df_master = df_master.rename(columns={
            'name_x': 'ClubName',
            'name_y': 'LeagueName',
            'country_name': 'Country',
            'stadium_seats': 'StadiumCapacity',
            'foreigners_percentage': 'ForeignersPercentage',
            'national_team_players': 'NationalTeamPlayers'
        })

        columnas_finales = [
            'ClubName', 'LeagueName', 'Country', 'SquadMarketValue', 
            'StadiumCapacity', 'ForeignersPercentage', 'NationalTeamPlayers', 
            'AveragePlayerAge', 'AveragePlayerHeight', 'TotalPlayers',
            'TotalGoals', 'TotalWins', 'TotalDraws', 'TotalLosses', 'MatchesPlayed',
            'TotalYellowCards', 'TotalRedCards', 'TotalAssists', 'TotalMinutesPlayed'
        ]
        
        df_final = df_master[columnas_finales].copy()

        df_final['SquadMarketValue'] = df_final['SquadMarketValue'] / 1_000_000

        # 🌟 EL FILTRO DE INTUICIÓN MATEMÁTICA 🌟
        # Si un equipo tiene 0 minutos jugados, los datos de tarjetas y asistencias son FALSOS.
        # Los convertimos en auténticos nulos (NaN) para poder imputarlos después.
        mascara_ceros_falsos = df_final['TotalMinutesPlayed'] == 0
        columnas_corruptas = ['TotalYellowCards', 'TotalRedCards', 'TotalAssists', 'TotalMinutesPlayed']
        
        df_final.loc[mascara_ceros_falsos, columnas_corruptas] = np.nan

        os.makedirs(os.path.dirname(ARCHIVO_SALIDA), exist_ok=True)
        df_final.to_csv(ARCHIVO_SALIDA, index=False)
        
        print("\n" + "🌟" * 25)
        print(f"✅ ¡DATASET CREADO Y DEPURADO CON ÉXITO!")
        print(f"📊 Dimensiones: {df_final.shape[0]} Clubes y {df_final.shape[1]} Variables.")
        print(f"📍 Ruta: {ARCHIVO_SALIDA}")
        print("🌟" * 25 + "\n")

    except Exception as e:
        print(f"\n❌ Falla en la Matrix: {e}")

if __name__ == "__main__":
    construir_dataset()