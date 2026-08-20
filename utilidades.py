# --- MÓDULO DE UTILIDADES: utilidades.py ---

import pygame
import os

# --- MANEJO DE FUENTES ---
def cargar_fuente(ruta, tamanio):
    if os.path.exists(ruta):
        return pygame.font.Font(ruta, tamanio)
    else:
        return pygame.font.SysFont("arial", tamanio, True)

# --- RENDERIZADO DE INTERFAZ (UI) ---
def dibujar_boton_pixelado(superficie, rect, color_fondo, color_borde, grosor):
    pygame.draw.rect(superficie, color_fondo, (rect.x, rect.y + 4, rect.width, rect.height - 8))
    pygame.draw.rect(superficie, color_fondo, (rect.x + 4, rect.y, rect.width - 8, rect.height))
    
    pygame.draw.line(superficie, color_borde, (rect.x + 4, rect.y), (rect.right - 5, rect.y), grosor)
    pygame.draw.line(superficie, color_borde, (rect.x + 4, rect.bottom - 1), (rect.right - 5, rect.bottom - 1), grosor)
    pygame.draw.line(superficie, color_borde, (rect.x, rect.y + 4), (rect.x, rect.bottom - 5), grosor)
    pygame.draw.line(superficie, color_borde, (rect.right - 1, rect.y + 4), (rect.right - 1, rect.bottom - 5), grosor)
    
    pygame.draw.rect(superficie, color_borde, (rect.x + 1, rect.y + 1, 3, 3)) 
    pygame.draw.rect(superficie, color_borde, (rect.right - 4, rect.y + 1, 3, 3)) 
    pygame.draw.rect(superficie, color_borde, (rect.x + 1, rect.bottom - 4, 3, 3)) 
    pygame.draw.rect(superficie, color_borde, (rect.right - 4, rect.bottom - 4, 3, 3)) 

# --- CARGA DE ASSETS GRÁFICOS ---
def cargar_icono(subcarpeta, nombre_archivo):
    ruta = os.path.join("imagenes", subcarpeta, nombre_archivo)
    if os.path.exists(ruta):
        img = pygame.image.load(ruta).convert_alpha()
        return pygame.transform.scale(img, (60, 60))
    else:
        print(f"Error: No se encontró la imagen en {ruta}")
        return None

def cargar_carta(subcarpeta, nombre_archivo):
    ruta = os.path.join("imagenes", subcarpeta, nombre_archivo)
    if os.path.exists(ruta):
        img = pygame.image.load(ruta).convert()
        return pygame.transform.scale(img, (320, 380)) 
    else:
        print(f"Error: No se encontró la imagen en {ruta}")
        return None