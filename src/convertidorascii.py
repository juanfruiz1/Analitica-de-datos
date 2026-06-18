import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time

# --- CONFIGURACIÓN ---
VIDEO_ENTRADA = "src/tu_video.mp4"
WEBP_SALIDA = "src/ascii_fondo_color_extremo.webp"

ASCII_CHARS = list(" `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@")
NUEVO_ANCHO = 500  
SALTO_FRAMES = 6   

RUTA_FUENTE = None 
TAMANO_FUENTE = 12

if RUTA_FUENTE:
    fuente_ascii = ImageFont.truetype(RUTA_FUENTE, TAMANO_FUENTE)
    bbox = fuente_ascii.getbbox("A")
    CHAR_W = bbox[2] - bbox[0]
    CHAR_H = bbox[3] - bbox[1]
else:
    fuente_ascii = ImageFont.load_default()
    CHAR_W = 6
    CHAR_H = 15

def ajustar_gamma(imagen, gamma=0.4):
    """
    La corrección Gamma < 1 hace que los colores oscuros se vuelvan 
    brillantes sin quemar los colores que ya son blancos.
    """
    invGamma = 1.0 / gamma
    tabla = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(imagen, tabla)

def potenciar_colores_nuclear(frame_bgr):
    """
    Lleva la saturación y el brillo al límite absoluto antes de que 
    el fondo negro se los trague.
    """
    # 1. Aplicar Gamma para rescatar colores de las sombras absolutas
    frame_gamma = ajustar_gamma(frame_bgr, gamma=0.5)
    
    # 2. Pasar a HSV para manipular color puro
    hsv = cv2.cvtColor(frame_gamma, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # 3. Saturación al 250% (Multiplicador 2.5)
    s = cv2.multiply(s, 2.5)
    
    # 4. Brillo (Value) al 150% (Multiplicador 1.5)
    v = cv2.multiply(v, 1.5)
    
    # Recortar para no exceder el límite de 255
    s = np.clip(s, 0, 255).astype(np.uint8)
    v = np.clip(v, 0, 255).astype(np.uint8)
    
    hsv_nuclear = cv2.merge([h, s, v])
    return cv2.cvtColor(hsv_nuclear, cv2.COLOR_HSV2RGB)

def procesar_frame_color_maximo(frame):
    # Usamos la nueva función nuclear para extraer los colores RGB
    frame_rgb = potenciar_colores_nuclear(frame)
    
    # Para el mapa de grises (que decide qué letra usar), seguimos usando la versión normal
    # para no deformar las siluetas.
    frame_gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    gris_revelado = clahe.apply(frame_gris)
    
    alto_orig, ancho_orig = frame_gris.shape
    ratio_imagen = alto_orig / ancho_orig
    nuevo_alto = int((NUEVO_ANCHO * ratio_imagen) * (CHAR_W / CHAR_H))
    
    gris_mini = cv2.resize(gris_revelado, (NUEVO_ANCHO, nuevo_alto))
    rgb_mini = cv2.resize(frame_rgb, (NUEVO_ANCHO, nuevo_alto))
    
    ancho_img = NUEVO_ANCHO * CHAR_W
    alto_img = nuevo_alto * CHAR_H
    
    img_resultado = Image.new('RGB', (ancho_img, alto_img), color='black')
    dibujo = ImageDraw.Draw(img_resultado)
    
    len_chars = len(ASCII_CHARS) - 1
    
    for y in range(nuevo_alto):
        for x in range(NUEVO_ANCHO):
            luma = gris_mini[y, x]
            indice_char = int((luma / 255) * len_chars)
            caracter = ASCII_CHARS[indice_char]
            
            if caracter != " ":
                r, g, b = rgb_mini[y, x]
                # Un último empujón manual de brillo justo al pintar
                r = min(255, int(r * 1.2))
                g = min(255, int(g * 1.2))
                b = min(255, int(b * 1.2))
                
                dibujo.text((x * CHAR_W, y * CHAR_H), caracter, font=fuente_ascii, fill=(r, g, b))
                
    return img_resultado

def ejecutar_conversion():
    print(f"Iniciando Renderizado con COLOR NUCLEAR...")
    cap = cv2.VideoCapture(VIDEO_ENTRADA)
    frames_webp = []
    contador = 0
    
    tiempo_inicio = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
            
        if contador % SALTO_FRAMES == 0:
            img = procesar_frame_color_maximo(frame)
            frames_webp.append(img)
            print(f"Frame {contador} procesado con color al máximo...")
            
        contador += 1

    cap.release()
    
    if frames_webp:
        print(f"Comprimiendo WebP...")
        frames_webp[0].save(
            WEBP_SALIDA, format='WebP', save_all=True,
            append_images=frames_webp[1:], duration=150, loop=0, quality=70 
        )
        print(f"¡Terminado! {WEBP_SALIDA} generado con éxito.")

if __name__ == "__main__":
    ejecutar_conversion()