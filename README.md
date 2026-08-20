# 🕹️ Pala... ¿Pala ke? - Proyecto 3 (UTN)

Un videojuego arcade 2D desarrollado en **Python** utilizando la librería **Pygame**. El juego destaca por su arquitectura modular, aplicación de Programación Orientada a Objetos (POO) y manejo asincrónico del tiempo.

## 🚀 Características Técnicas Destacadas

*   **Máquina de Estados Finita (FSM):** Arquitectura de control de flujo para transiciones limpias entre menús, opciones, gameplay y pantallas de victoria/derrota.
*   **Colisiones "Pixel-Perfect":** Implementación de `pygame.mask` para detectar impactos exactos basados en los píxeles reales de los sprites y no en cajas delimitadoras (hitboxes).
*   **Gestión de Memoria y Rendimiento:** Uso de `pygame.sprite.Group` para el renderizado en lote y eliminación activa de entidades con el método `.kill()` para prevenir fugas de memoria (Memory Leaks).
*   **Temporizadores No Bloqueantes:** Lógica de deltas de tiempo (`pygame.time.get_ticks()`) para manejar la recarga de disparos, "I-Frames" de invulnerabilidad y pausas entre oleadas sin congelar el Game Loop.
*   **HUD Dinámico:** Renderizado algorítmico de barras de vida complejas (ej. La secuencia de Pi del jefe final) y elementos de interfaz adaptativos.

## 📂 Arquitectura del Código

El proyecto está dividido en cuatro módulos principales para garantizar la escalabilidad y aplicar el principio de responsabilidad única:

1.  `main.py`: Director de orquesta. Contiene el bucle principal (Game Loop), la gestión de eventos, el manejo de estados y el renderizado visual de capas.
2.  `personajes.py`: Encapsula el comportamiento físico y lógico (IA básica) del Protagonista, los Villanos y los Proyectiles mediante herencia de `pygame.sprite.Sprite`.
3.  `utilidades.py`: Módulo auxiliar para la carga de recursos multiplataforma (rutas absolutas) y el dibujo de interfaz procedimental.
4.  `config.py`: Diccionario centralizado de constantes, textos y paletas de colores RGB (Single Source of Truth).

## 🛠️ Requisitos e Instalación

Para ejecutar este juego en tu computadora, necesitás tener Python y Pygame instalados.

1. Clonar el repositorio:
   git clone https://github.com/daviDR7ynaga/pala-ke-pygame-project.git
2. Instalar dependencias:
   pip install pygame
3. Ejecutar el juego:
   python main.py

## 🎮 Controles

*   **A / D o Flechas:** Mover al protagonista de izquierda a derecha.
*   **Espacio:** Disparar (requiere tokens de munición).
*   **Clic Izquierdo:** Interactuar con los menús.
