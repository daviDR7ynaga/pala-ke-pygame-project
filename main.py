# --- MÓDULO PRINCIPAL: main.py ---

import pygame
import sys
import os
import random 

from config import *
from utilidades import *
from personajes import Protagonista, Villano

# --- INICIALIZACIÓN DE PYGAME Y VENTANA ---
pygame.init()
pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Pala... ¿Pala ke?")

ANCHO = pantalla.get_width()
ALTO = pantalla.get_height()

# --- CARGA DE RECURSOS ---
fuente_titulo = cargar_fuente("fuentes/PixeloidSans-Bold.ttf", 96) 
fuente_subtitulo = cargar_fuente("fuentes/PixeloidSans-Bold.ttf", 50) 
fuente_botones = cargar_fuente("fuentes/VCR_OSD_MONO_1.001.ttf", 36)
fuente_version = cargar_fuente("fuentes/Silkscreen-Regular.ttf", 18)
fuente_espacio = cargar_fuente("fuentes/PixeloidSans.ttf", 28) 

ruta_fondo_menu = os.path.join("imagenes", "fondos", "Fondo.jpg")
if os.path.exists(ruta_fondo_menu):
    fondo_menu_img = pygame.image.load(ruta_fondo_menu).convert()
    fondo_menu_img = pygame.transform.scale(fondo_menu_img, (ANCHO, ALTO))
else:
    fondo_menu_img = None

icono_cv = cargar_icono("interfaz", "CV_icono.png")
icono_opc = cargar_icono("interfaz", "Tuerca_icono.png")
icono_salir = cargar_icono("interfaz", "Pulgar_icono.png")

carta_facil = cargar_carta("interfaz", "ModoFacil.jpg")
carta_normal = cargar_carta("interfaz", "ModoNormal.jpg")
carta_dificil = cargar_carta("interfaz", "ModoDificil.jpg")

def cargar_img_hud(ruta, tamaño, color_fallback):
    if os.path.exists(ruta):
        img = pygame.image.load(ruta).convert_alpha()
        return pygame.transform.scale(img, tamaño)
    else:
        superficie = pygame.Surface(tamaño)
        superficie.fill(color_fallback)
        return superficie

img_vida_llena = cargar_img_hud(os.path.join("imagenes", "interfaz", "Vida1.png"), (50, 50), (255, 0, 0))
img_vida_vacia = cargar_img_hud(os.path.join("imagenes", "interfaz", "Vida2.png"), (50, 50), (100, 100, 100))
img_icono_token = cargar_img_hud(os.path.join("imagenes", "interfaz", "Tokens.png"), (40, 40), (0, 255, 255))
img_icono_pi = cargar_img_hud(os.path.join("imagenes", "interfaz", "Pi.png"), (50, 50), (255, 0, 255))

# --- ZONAS DE CLIC (RECTS) ---
rect_cv = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 - 40, 300, 65)
rect_opc = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 + 45, 300, 65)
rect_salir = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 + 130, 300, 65)

rect_quedar = pygame.Rect(ANCHO // 2 - 320, ALTO // 2 + 80, 300, 65)
rect_confirmar_salir = pygame.Rect(ANCHO // 2 + 20, ALTO // 2 + 80, 300, 65)
rect_volver = pygame.Rect(ANCHO // 2 - 150, ALTO - 120, 300, 65)

rect_facil = pygame.Rect(ANCHO // 2 - 520, ALTO // 2 - 150, 320, 380)
rect_normal = pygame.Rect(ANCHO // 2 - 160, ALTO // 2 - 150, 320, 380)
rect_dificil = pygame.Rect(ANCHO // 2 + 200, ALTO // 2 - 150, 320, 380)

datos_botones = [
    ("TIRAR CV", rect_cv, icono_cv),
    ("OPCIONES", rect_opc, icono_opc),
    ("RENUNCIAR", rect_salir, icono_salir)
]

# --- VARIABLES GLOBALES Y ESTADOS ---
estado = "MENU" 
dificultad_seleccionada = ""
frase_actual = ""
oleada_actual = 1 

en_transicion = False
tiempo_transicion = 0
duracion_espera = 0 

score = 0
tokens_maximos = 0
tokens_actuales = 0
boss_hp = 15 

todos_los_sprites = pygame.sprite.Group()
proyectiles_prota = pygame.sprite.Group()
proyectiles_villano = pygame.sprite.Group()
enemigos = pygame.sprite.Group()

fondo_gameplay = None
FRECUENCIA_DISPARO_VILLANO = 1000 
ultimo_disparo_villano = 0
prota = None
reloj = pygame.time.Clock()

# --- FUNCIONES DE LÓGICA DE JUEGO ---
def resetear_gameplay():
    global fondo_gameplay, prota, oleada_actual, ultimo_disparo_villano
    global en_transicion, tiempo_transicion, duracion_espera, score, boss_hp
    todos_los_sprites.empty()
    proyectiles_prota.empty()
    proyectiles_villano.empty()
    enemigos.empty()
    fondo_gameplay = None
    prota = None
    oleada_actual = 1
    ultimo_disparo_villano = pygame.time.get_ticks()
    en_transicion = False
    tiempo_transicion = 0
    duracion_espera = 0
    score = 0
    boss_hp = 15 

def crear_oleada(nombre_img, nombre_proyectil, velocidad_villano, tamanio_villano=(135, 135), offset_disparo=-20):
    espacio_x = 130 
    espacio_y = 100  
    ancho_grilla = (7 * espacio_x) + 110 
    margen_x = (ANCHO - ancho_grilla) // 2 
    margen_y = 80
    
    for fila in range(3):
        for col in range(8):
            villano = Villano(ANCHO, ALTO, nombre_img, nombre_proyectil, velocidad_villano, tamanio=tamanio_villano, offset_y=offset_disparo)
            villano.rect.x = margen_x + (col * espacio_x)
            villano.rect.y = margen_y + (fila * espacio_y)
            villano.set_proyectiles_group(proyectiles_villano)
            todos_los_sprites.add(villano)
            enemigos.add(villano)

def crear_boss(nombre_img, nombre_proyectil, velocidad_boss, tamanio_boss=(250, 250), offset_disparo=20):
    boss = Villano(ANCHO, ALTO, nombre_img, nombre_proyectil, velocidad_boss, tamanio=tamanio_boss, offset_y=offset_disparo)
    boss.rect.centerx = ANCHO // 2
    boss.rect.y = 80
    boss.set_proyectiles_group(proyectiles_villano)
    todos_los_sprites.add(boss)
    enemigos.add(boss)

# --- CONFIGURACIONES POR DIFICULTAD ---
def setup_nivel_facil():
    global fondo_gameplay, prota, frase_actual, FRECUENCIA_DISPARO_VILLANO, tokens_maximos, tokens_actuales
    resetear_gameplay()
    ruta = os.path.join("imagenes", "fondos", "FondoGM1.jpg")
    if os.path.exists(ruta):
        fondo_gameplay = pygame.transform.scale(pygame.image.load(ruta).convert(), (ANCHO, ALTO))
    
    prota = Protagonista(ANCHO, ALTO, "Estudiante.png", "Token.png")
    prota.set_proyectiles_group(proyectiles_prota)
    todos_los_sprites.add(prota)
    
    FRECUENCIA_DISPARO_VILLANO = 1000
    tokens_maximos = 40
    tokens_actuales = 40
    crear_oleada("Laptop.png", "Lol.png", 3, tamanio_villano=(135, 135), offset_disparo=-20) 
    frase_actual = random.choice(FRASES_CARGA)

def setup_nivel_normal():
    global fondo_gameplay, prota, frase_actual, FRECUENCIA_DISPARO_VILLANO, tokens_maximos, tokens_actuales
    resetear_gameplay()
    ruta = os.path.join("imagenes", "fondos", "FondoGM2.jpg")
    if os.path.exists(ruta):
        fondo_gameplay = pygame.transform.scale(pygame.image.load(ruta).convert(), (ANCHO, ALTO))
    
    prota = Protagonista(ANCHO, ALTO, "Graduado.png", "Token.png")
    prota.set_proyectiles_group(proyectiles_prota)
    todos_los_sprites.add(prota)
    
    FRECUENCIA_DISPARO_VILLANO = 750
    tokens_maximos = 35
    tokens_actuales = 35
    crear_oleada("Obrero.png", "Pala.png", 5, tamanio_villano=(120, 110), offset_disparo=5) 
    frase_actual = random.choice(FRASES_CARGA)

def setup_nivel_dificil():
    global fondo_gameplay, prota, frase_actual, FRECUENCIA_DISPARO_VILLANO, tokens_maximos, tokens_actuales
    resetear_gameplay()
    ruta = os.path.join("imagenes", "fondos", "FondoGM2.jpg")
    if os.path.exists(ruta):
        fondo_gameplay = pygame.transform.scale(pygame.image.load(ruta).convert(), (ANCHO, ALTO))
    
    prota = Protagonista(ANCHO, ALTO, "Recursante.png", "Token.png")
    prota.set_proyectiles_group(proyectiles_prota)
    todos_los_sprites.add(prota)
    
    FRECUENCIA_DISPARO_VILLANO = 500
    tokens_maximos = 30
    tokens_actuales = 30
    crear_oleada("Despertador.png", "Zzz.png", 6, tamanio_villano=(100, 100), offset_disparo=10) 
    frase_actual = random.choice(FRASES_CARGA)


# --- BUCLE PRINCIPAL DEL JUEGO ---
ejecutando = True
while ejecutando:
    mouse_pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()

    # --- GESTIÓN DE EVENTOS ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if estado == "MENU":
                    estado = "CONFIRMAR_SALIDA"
                elif estado in ["SELECCION_DIFICULTAD", "PANTALLA_CARGA", "JUGANDO", "VICTORIA", "GAME_OVER", "CONFIRMAR_SALIDA", "OPCIONES"]:
                    estado = "MENU"
                    resetear_gameplay()
            
            if evento.key == pygame.K_RETURN and estado in ["VICTORIA", "GAME_OVER"]:
                if dificultad_seleccionada == "FÁCIL": setup_nivel_facil()
                elif dificultad_seleccionada == "NORMAL": setup_nivel_normal()
                elif dificultad_seleccionada == "DIFÍCIL": setup_nivel_dificil()
                estado = "PANTALLA_CARGA"

            if evento.key == pygame.K_SPACE and estado == "JUGANDO":
                if prota and not en_transicion and tokens_actuales > 0: 
                    prota.disparar()
                    tokens_actuales -= 1 
                    
            if evento.key == pygame.K_SPACE and estado == "PANTALLA_CARGA":
                estado = "JUGANDO"
                en_transicion = True
                tiempo_transicion = pygame.time.get_ticks()
                duracion_espera = 2000 

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:
                if estado == "MENU":
                    if rect_cv.collidepoint(mouse_pos): estado = "SELECCION_DIFICULTAD" 
                    elif rect_opc.collidepoint(mouse_pos): estado = "OPCIONES"
                    elif rect_salir.collidepoint(mouse_pos): estado = "CONFIRMAR_SALIDA"
                
                elif estado == "OPCIONES":
                    if rect_volver.collidepoint(mouse_pos): estado = "MENU"
                
                elif estado == "CONFIRMAR_SALIDA":
                    if rect_quedar.collidepoint(mouse_pos): estado = "MENU" 
                    elif rect_confirmar_salir.collidepoint(mouse_pos): ejecutando = False 
                
                elif estado == "SELECCION_DIFICULTAD":
                    if rect_facil.collidepoint(mouse_pos):
                        dificultad_seleccionada = "FÁCIL"
                        setup_nivel_facil()
                        estado = "PANTALLA_CARGA"
                    elif rect_normal.collidepoint(mouse_pos):
                        dificultad_seleccionada = "NORMAL"
                        setup_nivel_normal()
                        estado = "PANTALLA_CARGA"
                    elif rect_dificil.collidepoint(mouse_pos):
                        dificultad_seleccionada = "DIFÍCIL"
                        setup_nivel_dificil()
                        estado = "PANTALLA_CARGA"

    # --- LÓGICA DEL JUEGO Y COLISIONES ---
    if estado == "JUGANDO":
        if not en_transicion:
            todos_los_sprites.update()
            proyectiles_prota.update()
            proyectiles_villano.update()
            
            if current_time - ultimo_disparo_villano > FRECUENCIA_DISPARO_VILLANO:
                if enemigos: 
                    tirador = random.choice(enemigos.sprites()) 
                    tirador.disparar()
                ultimo_disparo_villano = current_time

            choques = pygame.sprite.groupcollide(enemigos, proyectiles_prota, False, True, pygame.sprite.collide_mask)
            for enemigo_golpeado, lista_proyectiles in choques.items():
                if oleada_actual == 3: 
                    boss_hp -= len(lista_proyectiles)
                    if boss_hp <= 0:
                        enemigo_golpeado.kill()
                else:
                    enemigo_golpeado.kill()
                    score += 10

            golpes = pygame.sprite.spritecollide(prota, proyectiles_villano, False, pygame.sprite.collide_mask)
            if golpes:
                if not prota.invencible:
                    prota.recibir_danio()
                    for proyectil in golpes:
                        proyectil.kill()
                    if prota.vidas <= 0:
                        estado = "GAME_OVER"

            # --- TRANSICIÓN DE OLEADAS ---
            if len(enemigos) == 0:
                if oleada_actual == 1:
                    en_transicion = True
                    tiempo_transicion = current_time
                    duracion_espera = 3500 
                    
                    proyectiles_villano.empty()
                    proyectiles_prota.empty()
                    prota.rect.centerx = ANCHO // 2
                    
                    if dificultad_seleccionada == "FÁCIL":
                        tokens_maximos = 40
                        crear_oleada("Laptop.png", "Lol.png", 5, tamanio_villano=(135, 135), offset_disparo=-20)
                    elif dificultad_seleccionada == "NORMAL":
                        tokens_maximos = 35
                        crear_oleada("Obrero.png", "Pala.png", 7, tamanio_villano=(120, 110), offset_disparo=5)
                    elif dificultad_seleccionada == "DIFÍCIL":
                        tokens_maximos = 30
                        crear_oleada("Despertador.png", "Zzz.png", 8, tamanio_villano=(100, 100), offset_disparo=10)
                    tokens_actuales = tokens_maximos 
                
                elif oleada_actual == 2 and dificultad_seleccionada == "DIFÍCIL":
                    en_transicion = True
                    tiempo_transicion = current_time
                    duracion_espera = 3500 
                    
                    proyectiles_villano.empty()
                    proyectiles_prota.empty()
                    prota.rect.centerx = ANCHO // 2
                    
                    tokens_maximos = 20
                    tokens_actuales = 20
                    boss_hp = 15 
                    
                    ruta_fondo_boss = os.path.join("imagenes", "fondos", "FondoGM3.jpg")
                    if os.path.exists(ruta_fondo_boss):
                        fondo_gameplay = pygame.transform.scale(pygame.image.load(ruta_fondo_boss).convert(), (ANCHO, ALTO))
                    
                    crear_boss("Maestra.png", "Math.png", 12, tamanio_boss=(250, 250), offset_disparo=30)
                    FRECUENCIA_DISPARO_VILLANO = 300 
                else:
                    estado = "VICTORIA"
        else:
            if current_time - tiempo_transicion >= duracion_espera:
                if duracion_espera == 3500:
                    if oleada_actual == 1: oleada_actual = 2
                    elif oleada_actual == 2: oleada_actual = 3
                en_transicion = False
                ultimo_disparo_villano = current_time 

    # --- RENDERIZADO VISUAL ---
    if estado == "MENU":
        if fondo_menu_img: pantalla.blit(fondo_menu_img, (0, 0))
        else: pantalla.fill(NEGRO)
        
        txt_titulo = fuente_titulo.render("Pala... ¿Pala ke?", True, BLANCO_TEXTO)
        pantalla.blit(txt_titulo, txt_titulo.get_rect(center=(ANCHO // 2, ALTO // 3)))
        
        for texto, rect_btn, icono in datos_botones:
            color_borde = CELESTE_MONITOR if rect_btn.collidepoint(mouse_pos) else BORDE_NORMAL
            dibujar_boton_pixelado(pantalla, rect_btn, GRIS_OSCURO_BTN, color_borde, 2)
            txt_btn = fuente_botones.render(texto, True, BLANCO_TEXTO)
            if icono:
                pantalla.blit(icono, (rect_btn.x + 25, rect_btn.centery - icono.get_height() // 2))
                pantalla.blit(txt_btn, txt_btn.get_rect(midleft=(rect_btn.x + 95, rect_btn.centery)))
            else:
                pantalla.blit(txt_btn, txt_btn.get_rect(center=rect_btn.center))
        
        txt_v = fuente_version.render("v 1.0 - UTN FRSR", True, BLANCO_TEXTO)
        pantalla.blit(txt_v, txt_v.get_rect(bottomright=(ANCHO - 20, ALTO - 20)))

    elif estado == "OPCIONES":
        if fondo_menu_img: pantalla.blit(fondo_menu_img, (0, 0))
        capa_oscura = pygame.Surface((ANCHO, ALTO)); capa_oscura.fill(NEGRO); capa_oscura.set_alpha(200); pantalla.blit(capa_oscura, (0, 0))

        txt_opt = fuente_subtitulo.render("CONTROLES", True, CELESTE_MONITOR)
        pantalla.blit(txt_opt, txt_opt.get_rect(center=(ANCHO // 2, 180)))

        txt_mov = fuente_espacio.render("[<-] [->]  o  [ A ] [ D ] :  Moverse", True, BLANCO_TEXTO)
        pantalla.blit(txt_mov, txt_mov.get_rect(center=(ANCHO // 2, 280)))

        txt_disp = fuente_espacio.render("[ ESPACIO ] :  Tirar Tokens", True, BLANCO_TEXTO)
        pantalla.blit(txt_disp, txt_disp.get_rect(center=(ANCHO // 2, 350)))

        txt_reglas = fuente_subtitulo.render("MUNICIÓN", True, CELESTE_MONITOR)
        pantalla.blit(txt_reglas, txt_reglas.get_rect(center=(ANCHO // 2, 480)))

        txt_alerta = fuente_espacio.render("¡CUIDADO! Los Tokens son limitados.", True, (255, 50, 50))
        pantalla.blit(txt_alerta, txt_alerta.get_rect(center=(ANCHO // 2, 560)))

        txt_alerta2 = fuente_espacio.render("Recargas al pasar de oleada. ¡No espamees!", True, BLANCO_TEXTO)
        pantalla.blit(txt_alerta2, txt_alerta2.get_rect(center=(ANCHO // 2, 610)))

        color_borde_volver = CELESTE_MONITOR if rect_volver.collidepoint(mouse_pos) else BORDE_NORMAL
        dibujar_boton_pixelado(pantalla, rect_volver, GRIS_OSCURO_BTN, color_borde_volver, 2)
        txt_volver = fuente_botones.render("VOLVER", True, BLANCO_TEXTO)
        pantalla.blit(txt_volver, txt_volver.get_rect(center=rect_volver.center))

    elif estado == "CONFIRMAR_SALIDA":
        if fondo_menu_img: pantalla.blit(fondo_menu_img, (0, 0))
        capa_oscura = pygame.Surface((ANCHO, ALTO)); capa_oscura.fill(NEGRO); capa_oscura.set_alpha(200); pantalla.blit(capa_oscura, (0, 0))
        
        txt_seguro = fuente_titulo.render("¿Seguro?", True, (255, 50, 50))
        pantalla.blit(txt_seguro, txt_seguro.get_rect(center=(ANCHO // 2, ALTO // 2 - 100)))
        
        txt_broma = fuente_espacio.render("Afuera tampoco están contratando mucho...", True, BLANCO_TEXTO)
        pantalla.blit(txt_broma, txt_broma.get_rect(center=(ANCHO // 2, ALTO // 2 - 10)))
        
        color_borde_quedar = CELESTE_MONITOR if rect_quedar.collidepoint(mouse_pos) else BORDE_NORMAL
        dibujar_boton_pixelado(pantalla, rect_quedar, GRIS_OSCURO_BTN, color_borde_quedar, 2)
        txt_quedar = fuente_espacio.render("Mejor me quedo", True, BLANCO_TEXTO)
        pantalla.blit(txt_quedar, txt_quedar.get_rect(center=rect_quedar.center))
        
        color_borde_salir = (255, 50, 50) if rect_confirmar_salir.collidepoint(mouse_pos) else BORDE_NORMAL
        dibujar_boton_pixelado(pantalla, rect_confirmar_salir, GRIS_OSCURO_BTN, color_borde_salir, 2)
        txt_salir = fuente_espacio.render("Salir igual", True, BLANCO_TEXTO)
        pantalla.blit(txt_salir, txt_salir.get_rect(center=rect_confirmar_salir.center))

    elif estado == "SELECCION_DIFICULTAD":
        if fondo_menu_img: pantalla.blit(fondo_menu_img, (0, 0))
        capa_oscura = pygame.Surface((ANCHO, ALTO)); capa_oscura.fill(NEGRO); capa_oscura.set_alpha(150); pantalla.blit(capa_oscura, (0, 0))
        
        txt_sel = fuente_subtitulo.render("Selección de Perfil / Dificultad", True, BLANCO_TEXTO)
        pantalla.blit(txt_sel, txt_sel.get_rect(center=(ANCHO // 2, 180)))
        
        for rect_carta, img_carta in [(rect_facil, carta_facil), (rect_normal, carta_normal), (rect_dificil, carta_dificil)]:
            if img_carta: pantalla.blit(img_carta, rect_carta.topleft)
            if rect_carta.collidepoint(mouse_pos): pygame.draw.rect(pantalla, CELESTE_MONITOR, rect_carta, 4, border_radius=5)

    elif estado == "PANTALLA_CARGA":
        pantalla.fill(NEGRO)
        txt_frase = fuente_subtitulo.render(frase_actual, True, CELESTE_MONITOR)
        pantalla.blit(txt_frase, txt_frase.get_rect(center=(ANCHO // 2, ALTO // 2 - 30)))
        txt_espacio = fuente_espacio.render("Presione la tecla Espacio para empezar", True, BLANCO_TEXTO)
        pantalla.blit(txt_espacio, txt_espacio.get_rect(center=(ANCHO // 2, ALTO // 2 + 50)))

    elif estado == "JUGANDO":
        if fondo_gameplay: pantalla.blit(fondo_gameplay, (0, 0))
        else: pantalla.fill(NEGRO)
        todos_los_sprites.draw(pantalla)
        proyectiles_prota.draw(pantalla)
        proyectiles_villano.draw(pantalla)
        
        if prota is not None:
            for i in range(3):
                x_pos = 30 + (i * 60)
                if i < prota.vidas: pantalla.blit(img_vida_llena, (x_pos, 30))
                else: pantalla.blit(img_vida_vacia, (x_pos, 30))

            txt_score = fuente_espacio.render(f"SCORE: {score:05d}", True, BLANCO_TEXTO)
            pantalla.blit(txt_score, (ANCHO - txt_score.get_width() - 30, 40))

            x_ammo, y_ammo = 30, ALTO - 60
            txt_limite = fuente_espacio.render("Límite de Tokens ", True, BLANCO_TEXTO)
            pantalla.blit(txt_limite, (x_ammo, y_ammo))
            x_ammo += txt_limite.get_width()
            pantalla.blit(img_icono_token, (x_ammo, y_ammo - 5))
            x_ammo += img_icono_token.get_width() + 10
            color_tokens = (255, 50, 50) if tokens_actuales == 0 else BLANCO_TEXTO 
            pantalla.blit(fuente_espacio.render(f"{tokens_actuales}/{tokens_maximos}", True, color_tokens), (x_ammo, y_ammo))

        if oleada_actual == 3 and dificultad_seleccionada == "DIFÍCIL" and len(enemigos) > 0:
            secuencia_pi = "314159265358979"
            superficies_letras = []
            ancho_letras = 0
            
            for i, digito in enumerate(secuencia_pi):
                color = (255, 50, 50) if i < boss_hp else (80, 80, 80)  
                surf_letra = fuente_espacio.render(digito, True, color)
                superficies_letras.append(surf_letra)
                ancho_letras += surf_letra.get_width() + 2
                
            inicio_x = (ANCHO - (img_icono_pi.get_width() + 15 + ancho_letras)) // 2
            pantalla.blit(img_icono_pi, (inicio_x, 20))
            
            actual_x = inicio_x + img_icono_pi.get_width() + 15
            for surf_letra in superficies_letras:
                pantalla.blit(surf_letra, (actual_x, 28)) 
                actual_x += surf_letra.get_width() + 2

    elif estado == "GAME_OVER":
        pantalla.fill(NEGRO)
        txt_lose = fuente_subtitulo.render("Te fuiste a recursar...", True, (255, 50, 50))
        pantalla.blit(txt_lose, txt_lose.get_rect(center=(ANCHO // 2, ALTO // 2 - 50)))
        
        txt_esc = fuente_espacio.render("Escape para salir al menú", True, BLANCO_TEXTO)
        pantalla.blit(txt_esc, txt_esc.get_rect(center=(ANCHO // 2, ALTO // 2 + 40)))
        
        txt_retry = fuente_espacio.render("Enter para reintentar", True, BLANCO_TEXTO)
        pantalla.blit(txt_retry, txt_retry.get_rect(center=(ANCHO // 2, ALTO // 2 + 80)))
        
        txt_final_score = fuente_espacio.render(f"Puntaje Final: {score}", True, CELESTE_MONITOR)
        pantalla.blit(txt_final_score, txt_final_score.get_rect(center=(ANCHO // 2, ALTO // 2 + 150)))

    elif estado == "VICTORIA":
        pantalla.fill(NEGRO)
        txt_win = fuente_subtitulo.render("Bien... ¿Y el laburo para cuando?", True, CELESTE_MONITOR)
        pantalla.blit(txt_win, txt_win.get_rect(center=(ANCHO // 2, ALTO // 2 - 50)))
        
        txt_esc = fuente_espacio.render("Escape para salir", True, BLANCO_TEXTO)
        pantalla.blit(txt_esc, txt_esc.get_rect(center=(ANCHO // 2, ALTO // 2 + 40)))
        
        txt_retry = fuente_espacio.render("Enter para reiniciar el juego", True, BLANCO_TEXTO)
        pantalla.blit(txt_retry, txt_retry.get_rect(center=(ANCHO // 2, ALTO // 2 + 80)))
        
        txt_final_score = fuente_espacio.render(f"Puntaje Final: {score}", True, CELESTE_MONITOR)
        pantalla.blit(txt_final_score, txt_final_score.get_rect(center=(ANCHO // 2, ALTO // 2 + 150)))

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
sys.exit()