import sqlite3
import pandas as pd
import os
from tqdm import tqdm
import chess
import math
import networkx as nx
import concurrent.futures
import multiprocessing

# --- 1. Clase Extractora Matemática ---
class ChessFeatureExtractor:
    def __init__(self):
        self.piece_values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
            chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
        }

    def get_all_features(self, fen: str, moves_str: str) -> dict:
        try:
            board = chess.Board(fen)
            primer_movimiento_uci = str(moves_str).split(' ')[0]
            board.push_uci(primer_movimiento_uci)

            if board.is_game_over():
                return self._empty_features()

            features = {}
            features.update(self._get_combinatorial_metrics(board))
            features.update(self._get_graph_metrics(board))
            features.update(self._get_spatial_entropy(board))
            features.update(self._get_center_of_mass_distance(board))
            return features
            
        except Exception:
            return self._empty_features()

    def _get_combinatorial_metrics(self, board):
        legal_moves = list(board.legal_moves)
        branching_factor = len(legal_moves)
        if branching_factor == 0:
            return {'branching_factor': 0, 'forcing_index': 0.0}
        forcing_moves = sum(1 for move in legal_moves if board.is_capture(move) or board.gives_check(move))
        return {'branching_factor': branching_factor, 'forcing_index': forcing_moves / branching_factor}

    def _get_graph_metrics(self, board):
        G = nx.DiGraph()
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                G.add_node(square)
                for target_square in board.attacks(square):
                    if board.piece_at(target_square):
                        G.add_edge(square, target_square)
        
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        max_edges = num_nodes * (num_nodes - 1) if num_nodes > 1 else 1
        density = num_edges / max_edges if num_nodes > 1 else 0
        components = nx.number_weakly_connected_components(G) if num_nodes > 0 else 0
        
        return {'graph_density': density, 'tension_components': components}

    def _get_spatial_entropy(self, board):
        quadrants = [0, 0, 0, 0] 
        total_mass = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                mass = self.piece_values.get(piece.piece_type, 0)
                total_mass += mass
                x, y = chess.square_file(square), chess.square_rank(square)
                if x < 4 and y < 4: quadrants[0] += mass
                elif x >= 4 and y < 4: quadrants[1] += mass
                elif x < 4 and y >= 4: quadrants[2] += mass
                else: quadrants[3] += mass
                
        if total_mass == 0: return {'spatial_entropy': 0.0}
        entropy = sum(- (m/total_mass) * math.log(m/total_mass) for m in quadrants if m > 0)
        return {'spatial_entropy': entropy}

    def _get_center_of_mass_distance(self, board):
        white_mass = black_mass = 0
        wx = wy = bx = by = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                mass = self.piece_values.get(piece.piece_type, 0)
                x, y = chess.square_file(square), chess.square_rank(square)
                if piece.color == chess.WHITE:
                    white_mass += mass; wx += x * mass; wy += y * mass
                else:
                    black_mass += mass; bx += x * mass; by += y * mass
                    
        if white_mass == 0 or black_mass == 0: return {'com_chebyshev_dist': 0.0}
        cx_w, cy_w = wx / white_mass, wy / white_mass
        cx_b, cy_b = bx / black_mass, by / black_mass
        return {'com_chebyshev_dist': max(abs(cx_w - cx_b), abs(cy_w - cy_b))}

    def _empty_features(self):
        return {'branching_factor': 0, 'forcing_index': 0.0, 'graph_density': 0.0, 
                'tension_components': 0, 'spatial_entropy': 0.0, 'com_chebyshev_dist': 0.0}


# --- 2. Funciones Envolventes para Multiprocesamiento ---
# Esto debe estar en el nivel superior (fuera de la clase) para que Windows no colapse
def procesar_fila_wrapper(tupla_datos):
    fen, moves = tupla_datos
    # Creamos una instancia independiente del extractor para cada núcleo de la CPU
    extractor = ChessFeatureExtractor()
    return extractor.get_all_features(fen, moves)


# --- 3. Pipeline de Procesamiento ---
if __name__ == "__main__":
    DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
    RUTA_DB = os.path.join(DIR_ACTUAL, "../database/proyecto_analitica.db")
    
    print("Conectando a SQLite...")
    conn = sqlite3.connect(RUTA_DB)
    
    try:
        print("Cargando la tabla original 'muestra' en memoria...")
        df_ajedrez = pd.read_sql_query("SELECT * FROM muestra", conn)
        
        # Preparamos los datos en una lista de tuplas para enviarlos a los diferentes núcleos
        datos_a_procesar = list(zip(df_ajedrez['FEN'], df_ajedrez['Moves']))
        
        # Detectamos cuántos núcleos tiene tu PC (dejamos 1 libre para que la PC no se congele)
        nucleos_disponibles = max(1, multiprocessing.cpu_count() - 1)
        print(f"Iniciando procesamiento PARALELO usando {nucleos_disponibles} núcleos...")
        
        # Aquí ocurre la magia del multiprocesamiento
        resultados = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=nucleos_disponibles) as executor:
            # Añadimos chunksize=5000 para evitar el embotellamiento de Windows
            for resultado in tqdm(executor.map(procesar_fila_wrapper, datos_a_procesar, chunksize=5000), total=len(datos_a_procesar)):
                resultados.append(resultado)
        
        # Convertimos la lista de diccionarios resultante de vuelta a DataFrame
        df_features = pd.DataFrame(resultados)
        df_procesado = pd.concat([df_ajedrez, df_features], axis=1)
        
        print("Sobrescribiendo la tabla 'muestra_procesada' en SQLite...")
        df_procesado.to_sql('muestra_procesada', conn, if_exists='replace', index=False)
        print("✅ ¡Proceso finalizado a máxima velocidad!")
        
    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
    finally:
        conn.close()