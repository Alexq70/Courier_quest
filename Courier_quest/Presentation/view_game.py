import sys
from pathlib import Path

import pygame

from Presentation.controller_game import controller_game
CELL_SIZE = 20
HUD_HEIGHT = 80
FPS = 60

class View_game:
    """Interfaz gráfica con Pygame para Courier Quest."""

    def __init__(self):
        """Inicializar Pygame, motor y cargar todos los assets."""
        pygame.init()
        self.engine = controller_game()
        self.engine.start()

        # Dimensiones de pantalla
        width = self.engine.city_map.width * CELL_SIZE
        height = self.engine.city_map.height * CELL_SIZE + HUD_HEIGHT
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Courier Quest")
        self.clock = pygame.time.Clock()

        self.move_timer = 0.0
        self.move_delay = 0.2 
        self.current_direction = 1  # Dirección actual (0=izquierda, 1=derecha)

        # Assets dentro de src/assets/
        assets_dir = Path(r"C:\Users\jarod\Documents\Universidad\ll Semestre 2025\Estructuras\Courier_quest\src\assets")
        tiles_dir = assets_dir / "tiles"
        
        # CARGAR TODAS LAS IMÁGENES DEL COURIER AL INICIO
        self.courier_images = {}
        self._load_courier_images(tiles_dir)

        # Cargar fuente con fallback
        font_file = assets_dir / "font.ttf"
        if font_file.exists():
            self.font = pygame.font.Font(str(font_file), 18)
        else:
            print(f"WARN: no hallé {font_file}, usando SysFont")
            self.font = pygame.font.SysFont(None, 18)

        # Cargar texturas de tiles
        self.tile_images = {}
        mapping = {"C": "road.png", "B": "building.png", "P": "park.png"}
        for key, fname in mapping.items():
            img_path = tiles_dir / fname
            if img_path.exists():
                img = pygame.image.load(str(img_path)).convert()
                img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
                self.tile_images[key] = img
            else:
                print(f"WARN: falta tile '{fname}' en {tiles_dir}")

        loaded = sorted(self.tile_images.keys())
        print(f"TILE_IMAGES cargadas: {loaded}")

        # Estado de juego
        self.running = True
        self.elapsed_time = 0.0
        self.goal = self.engine.city_map.goal
        self.earned = 0.0

    def _load_courier_images(self, tiles_dir):
        """Cargar todas las imágenes del courier una sola vez."""
        try:
            # Definir las rutas de las imágenes
            image_files = {
                0: "tiggermovil_izquierda_solo.PNG",  # Izquierda
                1: "tiggermovil_derecha_solo.PNG",    # Derecha
              #  2: "tiggermovil_arriba_solo.PNG",     # Arriba (si existe)
              #  3: "tiggermovil_abajo_solo.PNG"       # Abajo (si existe)
            }
            
            for direction, filename in image_files.items():
                courier_file = tiles_dir / filename
                if courier_file.exists():
                    img = pygame.image.load(str(courier_file)).convert_alpha()
                    # Escalar a 1.5x el tamaño de la celda
                    new_size = int(CELL_SIZE * 1.5)
                    self.courier_images[direction] = pygame.transform.scale(img, (new_size, new_size))
                    print(f"✅ Cargada: {filename}")
                else:
                    print(f"⚠️  No encontrada: {filename}")
                    self.courier_images[direction] = None
            
            # Si no hay imágenes, crear un diccionario vacío
            if not self.courier_images:
                self.courier_images = {}
                
        except Exception as e:
            print(f"❌ Error cargando imágenes del courier: {e}")
            self.courier_images = {}

    def run(self):
        """Bucle principal: eventos, actualización y dibujo."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.elapsed_time += dt
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def _move_courier(self, dx: int, dy: int):
        """Intentar mover al courier si no está bloqueado."""
        x, y = self.engine.courier.position
        nx, ny = x + dx, y + dy
        cmap = self.engine.city_map

        if (0 <= nx < cmap.width and 0 <= ny < cmap.height and not cmap.is_blocked(nx, ny)):
            self.engine.courier.move_to((nx, ny))

    def _update(self, dt: float):
        self.move_timer += dt
        if self.move_timer >= self.move_delay:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            
            if keys[pygame.K_UP]:
                dy = -1
                self.current_direction = 2  # Arriba
            elif keys[pygame.K_DOWN]:
                dy = 1
                self.current_direction = 3  # Abajo
            
            if keys[pygame.K_LEFT]:
                dx = -1
                self.current_direction = 0  # Izquierda
            elif keys[pygame.K_RIGHT]:
                dx = 1
                self.current_direction = 1  # Derecha
            
            if dx or dy:
                self._move_courier(dx, dy)
            
            self.move_timer = 0.0

    def _draw(self):
        """Dibujar mapa, pedidos, courier y HUD."""
        self._draw_map()
        self._draw_jobs()
        self._draw_courier()
        self._draw_hud()

    def _draw_map(self):
        """Pintar cada celda; usar imagen o color de fallback."""
        cmap = self.engine.city_map

        for y in range(cmap.height):
            for x in range(cmap.width):
                key = cmap.tiles[y][x]
                img = self.tile_images.get(key)
                if img:
                    self.screen.blit(img, (x * CELL_SIZE, y * CELL_SIZE))
                else:
                    name = cmap.legend[key].get("name", "")
                    if name == "calle":
                        color = (190, 190, 190)
                    elif name == "edificio":
                        color = (100, 100, 100)
                    elif name == "parque":
                        color = (144, 238, 144)
                    else:
                        color = (150, 150, 150)

                    rect = pygame.Rect(
                        x * CELL_SIZE,
                        y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    pygame.draw.rect(self.screen, color, rect)

                pygame.draw.rect(
                    self.screen,
                    (50, 50, 50),
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    1
                )

    def _draw_jobs(self):
        """Dibujar puntos de recogida en azul."""
        for job in self.engine.jobs:
            x, y = job.pickup
            rect = pygame.Rect(
                x * CELL_SIZE + 8,
                y * CELL_SIZE + 8,
                CELL_SIZE - 16,
                CELL_SIZE - 16
            )
            pygame.draw.rect(self.screen, (0, 0, 255), rect)

    def _draw_courier(self):
        """Dibujar courier con la imagen correcta según dirección."""
        x, y = self.engine.courier.position
        px, py = x * CELL_SIZE, y * CELL_SIZE

        # Usar imagen pre-cargada si existe
        if self.courier_images and self.current_direction in self.courier_images:
            courier_img = self.courier_images[self.current_direction]
            if courier_img is not None:
                # Centrar la imagen más grande
                img_width, img_height = courier_img.get_size()
                draw_x = px - (img_width - CELL_SIZE) // 2
                draw_y = py - (img_height - CELL_SIZE) // 2
                self.screen.blit(courier_img, (draw_x, draw_y))
                return
        
        # Fallback: círculo rojo
        center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
        pygame.draw.circle(self.screen, (255, 0, 0), center, CELL_SIZE // 3)

    def _draw_hud(self):
        """Pintar la barra inferior con tiempo e ingresos."""
        w, h = self.screen.get_size()
        hud_rect = pygame.Rect(0, h - HUD_HEIGHT, w, HUD_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 30), hud_rect)

        time_surf = self.font.render(
            f"Tiempo: {int(self.elapsed_time)}s", True, (255, 255, 255)
        )
        self.screen.blit(time_surf, (10, h - HUD_HEIGHT + 10))

        earn_surf = self.font.render(
            f"Ingresos: {int(self.earned)}/{self.goal}", True, (200, 200, 50)
        )
        self.screen.blit(earn_surf, (10, h - HUD_HEIGHT + 40))