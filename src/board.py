import pygame
import os

# --- INICIALIZACIÓN ---
pygame.init()
WIDTH, HEIGHT = 1000, 800  # <--- RECORTADO A 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Chess Game - ML Project')
font = pygame.font.Font('freesansbold.ttf', 20)
medium_font = pygame.font.Font('freesansbold.ttf', 40)
big_font = pygame.font.Font('freesansbold.ttf', 50)
timer = pygame.time.Clock()
fps = 60

flip_board = False  # <--- NUEVA VARIABLE PARA GIRAR TABLERO

# --- [NUEVO] GESTIÓN DE PERSONALIZACIÓN ---

# Rutas base para los assets
ASSETS_DIR = 'assets'
BOARDS_DIR = os.path.join(ASSETS_DIR, 'boards')
PIECES_DIR = os.path.join(ASSETS_DIR, 'pieces')

# Obtener listas de opciones disponibles escaneando los directorios
# Asumimos que los tableros son archivos .png y los sets son subcarpetas
AVAILABLE_BOARDS = sorted([f for f in os.listdir(BOARDS_DIR) if f.endswith('.png')])
AVAILABLE_PIECE_SETS = sorted([f for f in os.listdir(PIECES_DIR) if os.path.isdir(os.path.join(PIECES_DIR, f))])

# Variables de configuración para la selección actual
# Puedes cambiar los índices por defecto para empezar con opciones distintas
# 0: Primera opción, 1: Segunda, etc.
CURRENT_BOARD_INDEX = AVAILABLE_BOARDS.index('green.png') if 'green.png' in AVAILABLE_BOARDS else 0
CURRENT_PIECE_SET_INDEX = AVAILABLE_PIECE_SETS.index('alpha') if 'alpha' in AVAILABLE_PIECE_SETS else 0

# Variables para almacenar las imágenes cargadas
board_img = None
white_images, small_white_images = [], []
black_images, small_black_images = [], []

def load_game_assets():
    """Carga o recarga las imágenes del tablero y las piezas según la selección actual."""
    global board_img, white_images, small_white_images, black_images, small_black_images
    
    # 1. Cargar Tablero
    board_filename = AVAILABLE_BOARDS[CURRENT_BOARD_INDEX]
    board_path = os.path.join(BOARDS_DIR, board_filename)
    try:
        loaded_board = pygame.image.load(board_path).convert_alpha()
        board_img = pygame.transform.scale(loaded_board, (800, 800))
        print(f"Tablero cargado: {board_filename}")
    except pygame.error as e:
        print(f"Error cargando tablero '{board_filename}': {e}")
        # Crear un tablero de respaldo (un cuadrado gris)
        board_img = pygame.Surface((800, 800))
        board_img.fill((200, 200, 200))

    # 2. Cargar Piezas
    piece_set_name = AVAILABLE_PIECE_SETS[CURRENT_PIECE_SET_INDEX]
    print(f"Cargando set de piezas: {piece_set_name}")
    white_images, small_white_images = [], []
    black_images, small_black_images = [], []
    
    piece_names = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
    # Mapeo: 'pawn' -> 'p', 'queen' -> 'q', etc. Para archivos como 'wp.png' o 'bb.png'
    mapping = {'pawn': 'p', 'queen': 'q', 'king': 'k', 'knight': 'n', 'rook': 'r', 'bishop': 'b'}
    
    for p in piece_names:
        char_code = mapping[p]
        
        # Rutas de archivo
        w_path = os.path.join(PIECES_DIR, piece_set_name, f'w{char_code}.png')
        b_path = os.path.join(PIECES_DIR, piece_set_name, f'b{char_code}.png')
        
        try:
            # Cargar y escalar blancas
            img = pygame.image.load(w_path).convert_alpha()
            white_images.append(pygame.transform.scale(img, (80, 80)))
            small_white_images.append(pygame.transform.scale(img, (45, 45)))
            
            # Cargar y escalar negras
            img = pygame.image.load(b_path).convert_alpha()
            black_images.append(pygame.transform.scale(img, (80, 80)))
            small_black_images.append(pygame.transform.scale(img, (45, 45)))
        except pygame.error as e:
            print(f"Error cargando pieza '{p}' para el set '{piece_set_name}': {e}")
            # En caso de error, añadir una superficie vacía para no romper el índice
            empty_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            white_images.append(empty_surface); small_white_images.append(empty_surface)
            black_images.append(empty_surface); small_black_images.append(empty_surface)

# Cargar assets iniciales
load_game_assets()

# --- VARIABLES DE ESTADO DEL JUEGO ---
white_piece_list = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]

# CORRECCIÓN AQUÍ: Asegúrate de que los últimos elementos sean 'pawn' y no coordenadas
black_piece_list = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn'] 

black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]

# Listas principales de juego (para pop/append)
white_pieces = white_piece_list.copy()
black_pieces = black_piece_list.copy()
# Rastrear si el rey o torres se movieron para el Enroque
white_king_moved = False
black_king_moved = False
white_rooks_moved = [False, False] 
black_rooks_moved = [False, False]

# Estado de Coronación
promotion_active = False
promotion_coords = None
promotion_color = ''
promotion_idex=100

captured_pieces_white = []
captured_pieces_black = []
turn_step = 0 # 0-1: Blancas, 2-3: Negras
selection = 100
valid_moves = []
dragging = False
drag_pos = (0, 0)
game_over = False
winner = ''
counter = 0

# --- [NUEVO] VARIABLES DE ESTADO PARA REGLAS ADICIONALES ---

# Rastrear si la captura al paso está disponible. Almacena las coordenadas de destino.
# Por ejemplo, si el peón blanco mueve de (4, 1) a (4, 3), el objetivo en passant será (4, 2).
# Se restablece a None al comienzo del turno de cada jugador.
en_passant_target_coords = None

# Variable auxiliar para la función check_pawn
original_piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']

# --- SISTEMA DE HISTORIAL ---
game_history = []
history_index = -1

def save_state():
    global game_history, history_index
    # Si viajamos al pasado y hacemos una jugada nueva, borramos el futuro alternativo
    game_history = game_history[:history_index + 1]
    
    state = {
        'wp': white_pieces.copy(), 'wl': white_locations.copy(),
        'bp': black_pieces.copy(), 'bl': black_locations.copy(),
        'cw': captured_pieces_white.copy(), 'cb': captured_pieces_black.copy(),
        'turn': turn_step, 'ep': en_passant_target_coords
    }
    game_history.append(state)
    history_index += 1

def load_state(index):
    global white_pieces, white_locations, black_pieces, black_locations
    global captured_pieces_white, captured_pieces_black, turn_step, en_passant_target_coords
    global selection, valid_moves, dragging
    
    state = game_history[index]
    white_pieces, white_locations = state['wp'].copy(), state['wl'].copy()
    black_pieces, black_locations = state['bp'].copy(), state['bl'].copy()
    captured_pieces_white, captured_pieces_black = state['cw'].copy(), state['cb'].copy()
    turn_step, en_passant_target_coords = state['turn'], state['ep']
    
    # Limpiar selecciones a medias
    selection = 100
    valid_moves = []
    dragging = False


# --- FUNCIONES DE LÓGICA DE MOVIMIENTO ---

def load_fen(fen):
    """Convierte un string FEN a la lógica del tablero actual."""
    global white_pieces, white_locations, black_pieces, black_locations, turn_step
    global game_history, history_index, captured_pieces_white, captured_pieces_black
    
    white_pieces.clear(); white_locations.clear()
    black_pieces.clear(); black_locations.clear()
    
    piece_map = {'p': 'pawn', 'r': 'rook', 'n': 'knight', 'b': 'bishop', 'q': 'queen', 'k': 'king'}
    parts = fen.strip().split(' ')
    rows = parts[0].split('/')
    
    for y_fen, row in enumerate(rows):
        y = 7 - y_fen # Invertimos Y porque en tu lógica el blanco empieza en y=0
        x = 0
        for char in row:
            if char.isdigit():
                x += int(char)
            else:
                color = 'white' if char.isupper() else 'black'
                piece = piece_map[char.lower()]
                if color == 'white':
                    white_pieces.append(piece)
                    white_locations.append((x, y))
                else:
                    black_pieces.append(piece)
                    black_locations.append((x, y))
                x += 1
                
    turn_step = 0 if len(parts) == 1 or parts[1] == 'w' else 2
    captured_pieces_white, captured_pieces_black = [], []
    game_history, history_index = [], -1
    save_state()



def check_options(pieces, locations, turn):
    moves_list = []
    all_moves_list = []
    for i in range((len(pieces))):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn': moves_list = check_pawn(location, turn)
        elif piece == 'rook': moves_list = check_rook(location, turn)
        elif piece == 'knight': moves_list = check_knight(location, turn)
        elif piece == 'bishop': moves_list = check_bishop(location, turn)
        elif piece == 'queen': moves_list = check_queen(location, turn)
        elif piece == 'king': moves_list = check_king(location, turn)
        all_moves_list.append(moves_list)
    return all_moves_list

def check_king(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
            
    # [NUEVO] Lógica base de Enroque (Asume Rey en índice 3, columna 3)
    all_occupied = white_locations + black_locations
    if color == 'white' and not white_king_moved:
        # Enroque derecho (columna 4, 5, 6 vacías)
        if not white_rooks_moved[1] and all(x not in all_occupied for x in [(4,0), (5,0), (6,0)]):
            moves_list.append((position[0] + 2, position[1]))
        # Enroque izquierdo (columna 1, 2 vacías)
        if not white_rooks_moved[0] and all(x not in all_occupied for x in [(1,0), (2,0)]):
            moves_list.append((position[0] - 2, position[1]))
            
    elif color == 'black' and not black_king_moved:
        if not black_rooks_moved[1] and all(x not in all_occupied for x in [(4,7), (5,7), (6,7)]):
            moves_list.append((position[0] + 2, position[1]))
        if not black_rooks_moved[0] and all(x not in all_occupied for x in [(1,7), (2,7)]):
            moves_list.append((position[0] - 2, position[1]))
            
    return moves_list

def check_queen(position, color):
    return check_bishop(position, color) + check_rook(position, color)

def check_bishop(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations
    enemies_list = black_locations if color == 'white' else white_locations
    directions = [(1, -1), (-1, -1), (1, 1), (-1, 1)]
    for d in directions:
        path, chain = True, 1
        x, y = d
        while path:
            target = (position[0] + (chain * x), position[1] + (chain * y))
            if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
                moves_list.append(target)
                if target in enemies_list: path = False
                chain += 1
            else: path = False
    return moves_list

def check_rook(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations
    enemies_list = black_locations if color == 'white' else white_locations
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for d in directions:
        path, chain = True, 1
        x, y = d
        while path:
            target = (position[0] + (chain * x), position[1] + (chain * y))
            if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
                moves_list.append(target)
                if target in enemies_list: path = False
                chain += 1
            else: path = False
    return moves_list

def check_pawn(position, color):
    """
    Comprueba movimientos válidos para peones, incluyendo movimientos de una y dos casillas,
    capturas diagonales y [NUEVO] la regla de captura al paso.
    """
    moves_list = []
    all_occupied = white_locations + black_locations
    
    if color == 'white':
        # Movimiento de 1 casilla hacia adelante
        forward_1 = (position[0], position[1] + 1)
        if forward_1 not in all_occupied and position[1] < 7:
            moves_list.append(forward_1)
            # Movimiento inicial de 2 casillas
            forward_2 = (position[0], position[1] + 2)
            if forward_2 not in all_occupied and position[1] == 1:
                moves_list.append(forward_2)
        
        # Capturas diagonales estándar
        # Derecha-arriba
        cap_r = (forward_1[0] + 1, forward_1[1])
        if cap_r in black_locations: moves_list.append(cap_r)
        # Izquierda-arriba
        cap_l = (forward_1[0] - 1, forward_1[1])
        if cap_l in black_locations: moves_list.append(cap_l)
        
        # [NUEVO] Lógica de captura al paso (En Passant) para blancas
        if en_passant_target_coords is not None:
            # Verificar si las coordenadas objetivo están dentro de una captura diagonal válida para este peón
            # El peón enemigo que avanzó dos casillas estará en x=en_passant_target_coords[0], y=en_passant_target_coords[1]-1
            if en_passant_target_coords == (position[0] + 1, position[1] + 1) or \
               en_passant_target_coords == (position[0] - 1, position[1] + 1):
                # Verificar si en la casilla adyacente correcta hay un peón negro que avanzó dos casillas
                # (coordenadas objetivo para la captura)
                # La regla dice que debe ser el turno inmediatamente siguiente, lo cual se maneja en el loop de eventos
                moves_list.append(en_passant_target_coords)

    else: # Negro
        # Movimiento de 1 casilla hacia adelante
        forward_1 = (position[0], position[1] - 1)
        if forward_1 not in all_occupied and position[1] > 0:
            moves_list.append(forward_1)
            # Movimiento inicial de 2 casillas
            forward_2 = (position[0], position[1] - 2)
            if forward_2 not in all_occupied and position[1] == 6:
                moves_list.append(forward_2)
        
        # Capturas diagonales estándar
        # Derecha-abajo
        cap_r = (forward_1[0] + 1, forward_1[1])
        if cap_r in white_locations: moves_list.append(cap_r)
        # Izquierda-abajo
        cap_l = (forward_1[0] - 1, forward_1[1])
        if cap_l in white_locations: moves_list.append(cap_l)
        
        # [NUEVO] Lógica de captura al paso (En Passant) para negras
        if en_passant_target_coords is not None:
            if en_passant_target_coords == (position[0] + 1, position[1] - 1) or \
               en_passant_target_coords == (position[0] - 1, position[1] - 1):
                moves_list.append(en_passant_target_coords)
                
    return moves_list

def check_knight(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations
    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list

# --- FUNCIÓN CRÍTICA: ¿ESTÁ EL REY EN JAQUE? ---
def is_in_check(color):
    # Ahora lee directamente las variables globales (que modificaremos temporalmente)
    if color == 'white':
        king_idx = white_pieces.index('king')
        king_loc = white_locations[king_idx]
        options = check_options(black_pieces, black_locations, 'black')
    else:
        king_idx = black_pieces.index('king')
        king_loc = black_locations[king_idx]
        options = check_options(white_pieces, white_locations, 'white')
    
    for opt_list in options:
        if king_loc in opt_list:
            return True
    return False

def get_legal_moves(color, pieces, locations, all_options):
    global white_pieces, white_locations, black_pieces, black_locations
    legal_options = []
    for i in range(len(pieces)):
        piece_legal_moves = []
        for move in all_options[i]:
            # 1. Copia de seguridad del universo actual
            w_p_back, w_l_back = white_pieces.copy(), white_locations.copy()
            b_p_back, b_l_back = black_pieces.copy(), black_locations.copy()
            
            # 2. Simular el movimiento alterando la realidad global
            if color == 'white':
                white_locations[i] = move
                if move in black_locations:
                    idx = black_locations.index(move)
                    black_pieces.pop(idx); black_locations.pop(idx)
            else:
                black_locations[i] = move
                if move in white_locations:
                    idx = white_locations.index(move)
                    white_pieces.pop(idx); white_locations.pop(idx)
                    
            # 3. Verificar la condición de verdad (si el rey sobrevive)
            if not is_in_check(color):
                piece_legal_moves.append(move)
                
            # 4. Restaurar el universo a su estado original
            white_pieces, white_locations = w_p_back, w_l_back
            black_pieces, black_locations = b_p_back, b_l_back
            
        legal_options.append(piece_legal_moves)
    return legal_options

# --- FUNCIONES DE DIBUJO ---

def draw_board():
    """Dibuja el tablero de ajedrez y el panel lateral limpio."""
    screen.blit(board_img, (0, 0))
    # Panel gris derecho (ya sin márgenes dorados ni texto abajo)
    pygame.draw.rect(screen, (180, 180, 180), [800, 0, 200, 800])

def draw_sidebar_ui():
    """Dibuja los botones interactivos en el panel lateral derecho."""
    btn_color = (200, 200, 200) 
    
    # Botón Tablero (Solo texto fijo y flechas)
    screen.blit(font.render('Tablero', True, 'black'), (855, 170))
    pygame.draw.rect(screen, btn_color, [820, 200, 160, 40], border_radius=5)
    screen.blit(font.render('<', True, 'black'), (830, 210))
    screen.blit(font.render('>', True, 'black'), (950, 210))

    # Botón Piezas (Solo texto fijo y flechas)
    screen.blit(font.render('Piezas', True, 'black'), (860, 270))
    pygame.draw.rect(screen, btn_color, [820, 300, 160, 40], border_radius=5)
    screen.blit(font.render('<', True, 'black'), (830, 310))
    screen.blit(font.render('>', True, 'black'), (950, 310))

    # Botón Girar
    pygame.draw.rect(screen, (150, 150, 200), [820, 400, 160, 40], border_radius=5)
    screen.blit(font.render('GIRAR 180', True, 'black'), (840, 410))

    # Botón FEN
    pygame.draw.rect(screen, (150, 200, 150), [820, 500, 160, 40], border_radius=5)
    screen.blit(font.render('LEER FEN', True, 'black'), (845, 510))

    # Botón Reiniciar
    pygame.draw.rect(screen, (220, 100, 100), [820, 700, 160, 50], border_radius=10)
    screen.blit(font.render('REINICIAR', True, 'white'), (840, 715))

def draw_pieces():
    """Dibuja todas las piezas en el tablero y maneja la pieza que se está arrastrando."""
    original_piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
    
    for i in range(len(white_pieces)):
        img_index = original_piece_list.index(white_pieces[i])
        x, y = white_locations[i]
        if flip_board: x, y = 7 - x, 7 - y  # Transforma la posición si está girado
        
        if turn_step < 2 and selection == i and dragging:
            screen.blit(white_images[img_index], (drag_pos[0] - 40, drag_pos[1] - 40))
        else:
            screen.blit(white_images[img_index], (x * 100 + 10, y * 100 + 10))

    for i in range(len(black_pieces)):
        img_index = original_piece_list.index(black_pieces[i])
        x, y = black_locations[i]
        if flip_board: x, y = 7 - x, 7 - y  # Transforma la posición si está girado
        
        if turn_step >= 2 and selection == i and dragging:
            screen.blit(black_images[img_index], (drag_pos[0] - 40, drag_pos[1] - 40))
        else:
            screen.blit(black_images[img_index], (x * 100 + 10, y * 100 + 10))

def draw_valid(moves):
    """Dibuja círculos indicadores para movimientos válidos."""
    # [SOLICITUD: ELIMINAR PUNTOS ROJOS] - Comentar o eliminar el cuerpo de esta función.
    # color = 'red' if turn_step < 2 else 'blue'
    # for move in moves:
    #     pygame.draw.circle(screen, color, (move[0] * 100 + 50, move[1] * 100 + 50), 10, 2)
    pass

def draw_captured():
    """Dibuja las piezas capturadas en el panel lateral."""
    original_piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
    # Negras capturadas por blancas
    for i in range(len(captured_pieces_white)):
        captured_piece = captured_pieces_white[i]
        index = original_piece_list.index(captured_piece)
        screen.blit(small_black_images[index], (825, 10 + 50 * i))
    # Blancas capturadas por negras
    for i in range(len(captured_pieces_black)):
        captured_piece = captured_pieces_black[i]
        index = original_piece_list.index(captured_piece)
        screen.blit(small_white_images[index], (925, 10 + 50 * i))

def draw_game_over():
    """Dibuja la pantalla de fin de juego."""
    pygame.draw.rect(screen, 'black', [200, 200, 400, 70])
    screen.blit(font.render(f'{winner.capitalize()} won the game!', True, 'white'), (210, 210))
    screen.blit(font.render(f'Press ENTER to Restart!', True, 'white'), (210, 240))
    
def load_fen(fen):
    """Convierte un string FEN a la lógica del tablero actual."""
    global white_pieces, white_locations, black_pieces, black_locations, turn_step
    global game_history, history_index, captured_pieces_white, captured_pieces_black
    
    white_pieces.clear(); white_locations.clear()
    black_pieces.clear(); black_locations.clear()
    
    piece_map = {'p': 'pawn', 'r': 'rook', 'n': 'knight', 'b': 'bishop', 'q': 'queen', 'k': 'king'}
    parts = fen.strip().split(' ')
    rows = parts[0].split('/')
    
    for y_fen, row in enumerate(rows):
        y = 7 - y_fen 
        x = 0
        for char in row:
            if char.isdigit():
                x += int(char)
            else:
                color = 'white' if char.isupper() else 'black'
                piece = piece_map[char.lower()]
                if color == 'white':
                    white_pieces.append(piece)
                    white_locations.append((x, y))
                else:
                    black_pieces.append(piece)
                    black_locations.append((x, y))
                x += 1
                
    turn_step = 0 if len(parts) == 1 or parts[1] == 'w' else 2
    captured_pieces_white, captured_pieces_black = [], []
    game_history, history_index = [], -1
    save_state()

def reset_game():
    """Reinicia todas las variables del juego a su estado inicial."""
    global white_pieces, white_locations, black_pieces, black_locations
    global captured_pieces_white, captured_pieces_black, turn_step, selection
    global valid_moves, dragging, game_over, winner, counter
    global en_passant_target_coords
    global white_piece_list, black_piece_list
    
    # Reiniciar listas de piezas
    white_pieces = white_piece_list.copy()
    black_pieces = black_piece_list.copy()
    
    # Reiniciar ubicaciones estándar
    white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                       (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
    black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                       (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                       
    # Reiniciar otras variables
    captured_pieces_white = []
    captured_pieces_black = []
    turn_step = 0
    selection = 100
    valid_moves = []
    dragging = False
    game_over = False
    winner = ''
    counter = 0
    en_passant_target_coords = None
    
# ... (aquí termina draw_pieces)

def draw_promotion_menu():
    pygame.draw.rect(screen, 'white', [200, 400, 400, 100])
    pygame.draw.rect(screen, 'black', [200, 400, 400, 100], 5)
    promo_pieces = ['queen', 'rook', 'bishop', 'knight']
    for i in range(4):
        # original_piece_list debe estar definido arriba
        img_idx = original_piece_list.index(promo_pieces[i])
        if promotion_color == 'white':
            screen.blit(white_images[img_idx], (210 + i * 100, 410))
        else:
            screen.blit(black_images[img_idx], (210 + i * 100, 410))
    screen.blit(font.render("Elije pieza para coronar:", True, 'black'), (210, 370))

# --- AQUÍ EMPIEZA EL LOOP PRINCIPAL ---
# while run:
#    ...

# --- LOOP PRINCIPAL ---
black_options = check_options(black_pieces, black_locations, 'black')
white_options = check_options(white_pieces, white_locations, 'white')
run = True

# Guardar estado de En Passant del turno anterior para limpieza
prev_en_passant_target = None

while run:
    timer.tick(fps)
    screen.fill('dark gray')
    draw_board()
    draw_sidebar_ui()
    draw_captured()
    draw_pieces()
    
    if winner != '':
        game_over = True
        draw_game_over()
        
    if promotion_active:
        draw_promotion_menu()
    
    # Cálculo de Legales (Filtra los movimientos que te dejan en jaque)
    if selection != 100 and dragging:
        if turn_step < 2:
            pseudo = check_options(white_pieces, white_locations, 'white')
            legal_list = get_legal_moves('white', white_pieces, white_locations, pseudo)
        else:
            pseudo = check_options(black_pieces, black_locations, 'black')
            legal_list = get_legal_moves('black', black_pieces, black_locations, pseudo)
            
        valid_moves = legal_list[selection]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # --- EVENTOS DE TECLADO (Deshacer / Rehacer) ---
        if event.type == pygame.KEYDOWN:
            # Flecha Izquierda: Deshacer
            if event.key == pygame.K_LEFT and history_index > 0:
                history_index -= 1
                load_state(history_index)
            # Flecha Derecha: Rehacer
            elif event.key == pygame.K_RIGHT and history_index < len(game_history) - 1:
                history_index += 1
                load_state(history_index)

        # --- EVENTOS DEL MOUSE ---
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            
            # 0. Clics en la Barra Lateral (X > 800)
            if event.pos[0] > 800:
                if 200 <= event.pos[1] <= 240: # Botones Tablero
                    if 820 <= event.pos[0] <= 850: CURRENT_BOARD_INDEX = (CURRENT_BOARD_INDEX - 1) % len(AVAILABLE_BOARDS)
                    elif 940 <= event.pos[0] <= 980: CURRENT_BOARD_INDEX = (CURRENT_BOARD_INDEX + 1) % len(AVAILABLE_BOARDS)
                    load_game_assets()
                elif 300 <= event.pos[1] <= 340: # Botones Piezas
                    if 820 <= event.pos[0] <= 850: CURRENT_PIECE_SET_INDEX = (CURRENT_PIECE_SET_INDEX - 1) % len(AVAILABLE_PIECE_SETS)
                    elif 940 <= event.pos[0] <= 980: CURRENT_PIECE_SET_INDEX = (CURRENT_PIECE_SET_INDEX + 1) % len(AVAILABLE_PIECE_SETS)
                    load_game_assets()
                elif 400 <= event.pos[1] <= 440: # Botón Girar
                    flip_board = not flip_board
                elif 500 <= event.pos[1] <= 540: # Botón FEN
                    fen_input = input("\n=== INGRESE EL CÓDIGO FEN AQUÍ Y PRESIONE ENTER ===\n> ")
                    try: load_fen(fen_input)
                    except: print("Código FEN inválido.")
                elif 700 <= event.pos[1] <= 750 and 820 <= event.pos[0] <= 980: # Botón Reiniciar
                    reset_game()
                    game_history = []
                    history_index = -1
                    save_state()

            # 1. Resolver el Menú de Coronación
            elif promotion_active:
                if 400 <= event.pos[1] <= 500 and 200 <= event.pos[0] <= 600:
                    idx = (event.pos[0] - 200) // 100
                    choice = ['queen', 'rook', 'bishop', 'knight'][idx]
                    
                    if promotion_color == 'white':
                        white_pieces[promotion_index] = choice
                        turn_step = 2
                    else:
                        black_pieces[promotion_index] = choice
                        turn_step = 0
                        
                    promotion_active = False
                    selection = 100
                    dragging = False
                    save_state() # Guardar jugada al coronar
            
            # 2. Selección normal de piezas
            else:
                x_raw, y_raw = event.pos[0] // 100, event.pos[1] // 100
                # Si el tablero está girado, calculamos a la inversa
                x_coord = 7 - x_raw if flip_board else x_raw
                y_coord = 7 - y_raw if flip_board else y_raw
                
                if turn_step < 2 and (x_coord, y_coord) in white_locations:
                    selection = white_locations.index((x_coord, y_coord))
                    dragging = True
                elif turn_step >= 2 and (x_coord, y_coord) in black_locations:
                    selection = black_locations.index((x_coord, y_coord))
                    dragging = True

        if event.type == pygame.MOUSEMOTION:
            drag_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP and dragging and not promotion_active:
            x_raw, y_raw = event.pos[0] // 100, event.pos[1] // 100
            x_coord = 7 - x_raw if flip_board else x_raw
            y_coord = 7 - y_raw if flip_board else y_raw
            end_coords = (x_coord, y_coord)
            
            if end_coords in valid_moves:
                if turn_step < 2: # --- BLANCAS ---
                    start_coords = white_locations[selection]
                    piece_type = white_pieces[selection]
                    white_locations[selection] = end_coords 
                    
                    # EJECUCIÓN ENROQUE (Mover la torre)
                    if piece_type == 'king':
                        white_king_moved = True
                        if end_coords[0] - start_coords[0] == 2: # Derecho
                            r_idx = white_locations.index((7,0)); white_locations[r_idx] = (5,0)
                        elif start_coords[0] - end_coords[0] == 2: # Izquierdo
                            r_idx = white_locations.index((0,0)); white_locations[r_idx] = (2,0)
                    elif piece_type == 'rook':
                        if start_coords == (0,0): white_rooks_moved[0] = True
                        if start_coords == (7,0): white_rooks_moved[1] = True
                    
                    # Capturas
                    if end_coords in black_locations:
                        idx = black_locations.index(end_coords)
                        captured_pieces_white.append(black_pieces[idx])
                        black_pieces.pop(idx); black_locations.pop(idx)
                    
                    # Coronación (Guardar índice)
                    if piece_type == 'pawn' and end_coords[1] == 7:
                        promotion_active, promotion_color = True, 'white'
                        promotion_index = selection
                    else: 
                        turn_step = 2
                        save_state() # <--- GUARDAR JUGADA NORMAL

                else: # --- NEGRAS ---
                    start_coords = black_locations[selection]
                    piece_type = black_pieces[selection]
                    black_locations[selection] = end_coords
                    
                    # EJECUCIÓN ENROQUE
                    if piece_type == 'king':
                        black_king_moved = True
                        if end_coords[0] - start_coords[0] == 2:
                            r_idx = black_locations.index((7,7)); black_locations[r_idx] = (5,7)
                        elif start_coords[0] - end_coords[0] == 2:
                            r_idx = black_locations.index((0,7)); black_locations[r_idx] = (2,7)
                    elif piece_type == 'rook':
                        if start_coords == (0,7): black_rooks_moved[0] = True
                        if start_coords == (7,7): black_rooks_moved[1] = True
                    
                    # Capturas
                    if end_coords in white_locations:
                        idx = white_locations.index(end_coords)
                        captured_pieces_black.append(white_pieces[idx])
                        white_pieces.pop(idx); white_locations.pop(idx)
                            
                    # Coronación (Guardar índice)
                    if piece_type == 'pawn' and end_coords[1] == 0:
                        promotion_active, promotion_color = True, 'black'
                        promotion_index = selection
                    else: 
                        turn_step = 0
                        save_state() # <--- GUARDAR JUGADA NORMAL
            
            # Limpiar estado si NO estamos pausados coronando
            if not promotion_active:
                dragging, selection, valid_moves = False, 100, []

    pygame.display.flip()

pygame.quit()