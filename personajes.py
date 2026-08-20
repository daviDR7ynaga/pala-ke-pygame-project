# --- MÓDULO DE ENTIDADES: personajes.py ---

import pygame
import os

# --- CLASE JUGADOR (HERENCIA DE SPRITE) ---
class Protagonista(pygame.sprite.Sprite):
    def __init__(self, ANCHO, ALTO, ruta_img, ruta_proyectil, tamanio=(150, 150), tamanio_proyectil=(130, 130), offset_y=45):
        super().__init__()
        
        # --- CARGA Y ESCALADO DE IMAGEN ---
        ruta = os.path.join("imagenes", "personajes", ruta_img)
        if os.path.exists(ruta):
            img = pygame.image.load(ruta).convert_alpha() 
            self.image = pygame.transform.scale(img, tamanio)
        else:
            self.image = pygame.Surface(tamanio) 
            self.image.fill((0, 255, 0)) 

        # --- FÍSICAS Y COLISIONES EXACTAS (PIXEL-PERFECT) ---
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        # --- POSICIONAMIENTO INICIAL ---
        self.rect.centerx = ANCHO // 2
        self.rect.bottom = ALTO - 50
        
        # --- ATRIBUTOS DE JUGABILIDAD ---
        self.velocidad = 8
        self.limite_ancho = ANCHO
        self.ALTO = ALTO
        
        # --- CONFIGURACIÓN DE ARMAMENTO ---
        self.ruta_proyectil = ruta_proyectil
        self.tamanio_proyectil = tamanio_proyectil
        self.offset_y = offset_y
        self.proyectiles_group = None 
        
        # --- SISTEMA DE VIDAS E I-FRAMES ---
        self.vidas = 3
        self.invencible = False
        self.tiempo_invencible = 0
        self.duracion_invencibilidad = 1500 

    def set_proyectiles_group(self, grupo):
        self.proyectiles_group = grupo

    def recibir_danio(self):
        # Resta vida y activa la invulnerabilidad temporal
        if not self.invencible:
            self.vidas -= 1
            self.invencible = True
            self.tiempo_invencible = pygame.time.get_ticks()

    def update(self):
        # --- LÓGICA DE MOVIMIENTO ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.velocidad
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.velocidad

        # --- ENCAPSULAMIENTO DE BORDES ---
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.limite_ancho:
            self.rect.right = self.limite_ancho

        # --- LÓGICA DE PARPADEO POR DAÑO ---
        if self.invencible:
            ahora = pygame.time.get_ticks()
            if ahora - self.tiempo_invencible > self.duracion_invencibilidad:
                self.invencible = False
                self.image.set_alpha(255) 
            else:
                if (ahora // 100) % 2 == 0:
                    self.image.set_alpha(0) 
                else:
                    self.image.set_alpha(255) 

    def disparar(self):
        # Instanciación de un nuevo objeto Proyectil
        if self.proyectiles_group is not None:
            token = Proyectil(self.rect.centerx, self.rect.top + self.offset_y, -12, self.ALTO, "elementos", self.ruta_proyectil, self.tamanio_proyectil)
            self.proyectiles_group.add(token)


# --- CLASE ENEMIGO (HERENCIA DE SPRITE) ---
class Villano(pygame.sprite.Sprite):
    def __init__(self, ANCHO, ALTO, ruta_img, ruta_proyectil, velocidad, tamanio=(135, 135), tamanio_proyectil=(100, 100), offset_y=-20):
        super().__init__()
        
        # --- CARGA DINÁMICA DE ASSETS ---
        ruta = os.path.join("imagenes", "personajes", ruta_img)
        if os.path.exists(ruta):
            img = pygame.image.load(ruta).convert_alpha() 
            self.image = pygame.transform.scale(img, tamanio)
        else:
            self.image = pygame.Surface(tamanio)
            self.image.fill((255, 0, 0)) 

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        # --- ATRIBUTOS DEL ENEMIGO ---
        self.velocidad = velocidad 
        self.limite_ancho = ANCHO
        self.ALTO = ALTO
        self.ruta_proyectil = ruta_proyectil
        self.tamanio_proyectil = tamanio_proyectil
        self.offset_y = offset_y
        self.proyectiles_group = None
        self.direccion = 1 

    def set_proyectiles_group(self, grupo):
        self.proyectiles_group = grupo

    def update(self):
        # --- PATRÓN DE PATRULLAJE HORIZONTAL ---
        self.rect.x += self.velocidad * self.direccion
        if self.rect.right > self.limite_ancho or self.rect.left < 0:
            self.direccion *= -1

    def disparar(self):
        if self.proyectiles_group is not None:
            lol = Proyectil(self.rect.centerx, self.rect.bottom + self.offset_y, 7, self.ALTO, "elementos", self.ruta_proyectil, self.tamanio_proyectil)
            self.proyectiles_group.add(lol)


# --- CLASE MUNICIÓN (HERENCIA DE SPRITE REUTILIZABLE) ---
class Proyectil(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidad_y, limite_alto, subcarpeta, nombre_archivo, tamanio):
        super().__init__()
        
        ruta = os.path.join("imagenes", subcarpeta, nombre_archivo)
        if os.path.exists(ruta):
            img = pygame.image.load(ruta).convert_alpha()
            self.image = pygame.transform.scale(img, tamanio)
        else:
            self.image = pygame.Surface(tamanio)
            self.image.fill((255, 255, 0)) 

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect.centerx = x
        self.rect.centery = y
        self.velocidad_y = velocidad_y
        self.limite_alto = limite_alto

    def update(self):
        # --- MOVIMIENTO VERTICAL ---
        self.rect.y += self.velocidad_y
        
        # --- OPTIMIZACIÓN DE MEMORIA ---
        # Destruye el objeto si sale de los límites de la pantalla
        if self.rect.bottom < 0 or self.rect.top > self.limite_alto:
            self.kill()