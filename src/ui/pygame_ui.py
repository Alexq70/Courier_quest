# src/ui/pygame_ui.py

import sys
from pathlib import Path

import pygame

from engine.game_engine import GameEngine

CELL_SIZE = 32
HUD_HEIGHT = 80
FPS = 60


class GameUI:
    """Interfaz gráfica con Pygame para Courier Quest."""

    def __init__(self):
        """Inicializar Pygame, motor y cargar todos los assets."""
        pygame.init()
        self.engine = GameEngine()
        self.engine.start()

        # Dimensiones de pantalla
        width = self.engine.city_map.width * CELL_SIZE
        height = self.engine.city_map.height * CELL_SIZE + HUD_HEIGHT
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Courier Quest")
        self.clock = pygame.time.Clock()

        # Assets dentro de src/assets/
        src_dir = Path(__file__).parent.parent.resolve()
        assets_dir = src_dir / "assets"
        tiles_dir = assets_dir / "tiles"

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

        # Cargar sprite del courier (opcional)
        courier_file = assets_dir / "courier.png"
        if courier_file.exists():
            img = pygame.image.load(str(courier_file)).convert_alpha()
            self.courier_img = pygame.transform.scale(
                img, (CELL_SIZE, CELL_SIZE)
            )
        else:
            self.courier_img = None

        # Estado de juego
        self.running = True
        self.elapsed_time = 0.0
        self.goal = self.engine.city_map.goal
        self.earned = 0.0

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
        """Procesar cierre de ventana y teclas de movimiento."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                dx = dy = 0
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1

                if dx or dy:
                    self._move_courier(dx, dy)

    def _move_courier(self, dx: int, dy: int):
        """Intentar mover al courier si no está bloqueado."""
        x, y = self.engine.courier.position
        nx, ny = x + dx, y + dy
        cmap = self.engine.city_map

        if (
            0 <= nx < cmap.width
            and 0 <= ny < cmap.height
            and not cmap.is_blocked(nx, ny)
        ):
            self.engine.courier.move_to((nx, ny))

    def _update(self, dt: float):
        """Actualizar lógica de juego (stamina, clima, entregas)."""
        pass

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
                    (
                        x * CELL_SIZE,
                        y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    ),
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
        """Dibujar courier como sprite o círculo rojo."""
        x, y = self.engine.courier.position
        px, py = x * CELL_SIZE, y * CELL_SIZE

        if self.courier_img:
            self.screen.blit(self.courier_img, (px, py))
        else:
            center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
            pygame.draw.circle(
                self.screen, (255, 0, 0), center, CELL_SIZE // 3
            )

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
            f"Ingresos: {int(self.earned)}/{self.goal}", True,
            (200, 200, 50)
        )
        self.screen.blit(earn_surf, (10, h - HUD_HEIGHT + 40))