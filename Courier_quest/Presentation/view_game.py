import sys
import math
from pathlib import Path
from Logic.entity.job import Job

import pygame
from Presentation.controller_game import controller_game
from Logic.entity.courier import Courier
from Logic.entity import courier

CELL_SIZE = 22
HUD_HEIGHT = 75
FPS = 60
prev = ''

class View_game:
    """Interfaz gráfica con Pygame para Courier Quest.""" 

    def __init__(self):
        """Inicializar Pygame, motor y cargar todos los assets."""
        pygame.init()
        pygame.mixer.init
        self.engine = controller_game()
        self.engine.start()

        # Dimensiones de pantalla
        width = self.engine.city_map.width * CELL_SIZE
        height = self.engine.city_map.height * CELL_SIZE + HUD_HEIGHT
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Courier Quest")
        self.clock = pygame.time.Clock()

        self.move_timer = 0.0
        self.move_delay = 0.15 
        self.current_direction = 1  

        # Ruta de las imágenes 
        assets_dir = Path(__file__).parent.parent.parent / "src" / "assets"
        tiles_dir = assets_dir / "tiles"
        
        self.courier_images = {}
        self._load_courier_images(tiles_dir)
        self._load_sounds(tiles_dir)

        font_file = assets_dir / "font.ttf"
        if font_file.exists():
            self.font = pygame.font.Font(str(font_file), 18)
            self.small_font = pygame.font.Font(str(font_file), 14)  # Fuente más pequeña para clima
        else:
            print(f"WARN: no hallé {font_file}, usando SysFont")
            self.font = pygame.font.SysFont(None, 18)
            self.small_font = pygame.font.SysFont(None, 14)

        # Diccionario para cargar las imágenes
        self.tile_images = {}
        mapping = {"C": "road.png", "P": "park.png", "W":"window.PNG","G":"ground.PNG","PE":"window_job.png", "D":"drop_off.png","W_NPC":"window_npc.png","G_NPC":"ground_npc.png"}
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

        # Iconos de clima (puedes agregar imágenes específicas para cada condición)
        self.weather_icons = {}
        self._load_weather_icons(tiles_dir)

        self.running = True
        self.elapsed_time = 0.0
        self.goal = self.engine.city_map.goal
        self.earned = 0.0
        self.state = "running"
        self.final_stats = None
        self.session_duration = 15 * 60
        self.remaining_time = float(self.session_duration)

        
        self.current_weather_display = ""
        self.weather_transition_progress = 0.0
        pygame.mixer.music.play(-1)
        self.roar=True
        pygame.mixer.music.set_volume(0.3)

    def _load_sounds(self, tiles_dir):  
      sounds_dict = {
        "catch": "entrega.mp3",
        "base": "base.mp3",  
        "thunder": "thunder.mp3",
        "acept":"acept.mp3",
        "error":"error.mp3",
        "remove":"remove.mp3",
        "rain":"rain.mp3",
        "roar":"roar.mp3",
        "storm":"storm",
        "remove":"remove.mp3",
        "rain":"rain.mp3",
        "roar":"roar.mp3",
        "storm":"storm"
      }
    
      self.sounds = {}
    
      for key, filename in sounds_dict.items(): 
        sound_path = tiles_dir / filename
        if sound_path.exists():
            try:
                if key == "base":
                   
                    pygame.mixer.music.load(str(sound_path))
                    print(f"Música de fondo cargada: {filename}")
                else:
                   
                    self.sounds[key] = pygame.mixer.Sound(str(sound_path))
                    print(f"Sonido cargado: {filename}")
            except Exception as e:
                print(f"Error cargando {filename}: {e}")
        else:
            print(f"Archivo no encontrado: {sound_path}")


    def _load_weather_icons(self, tiles_dir):
        """Cargar iconos para las condiciones climáticas"""
        weather_icon_mapping = {
            "clear": "clear.png",
            "clouds": "clouds.png", 
            "rain": "rain.png",
            "rain_light": "ligth_rain.png",
            "storm": "storm.png",
            "fog": "fog.png",
            "wind": "wind.png",
            "heat": "heat.png",
            "cold": "cold.png"
        }
        
        for condition, filename in weather_icon_mapping.items():
            icon_path = tiles_dir / filename
            if icon_path.exists():
                img = pygame.image.load(str(icon_path)).convert_alpha()
                img = pygame.transform.scale(img, (30, 30))  # Tamaño fijo para iconos
                self.weather_icons[condition] = img
            else:
                # Si no hay imagen, usar un placeholder con texto
                print(f"WARN: No se encontró icono de clima: {filename}")

    def _load_courier_images(self, tiles_dir):
        """Cargar todas las imágenes del courier una sola vez."""
        try:
            image_files = {
                0: "tiggermovil_izquierda_job.PNG",  
                1: "tiggermovil_derecha_job.PNG",    
                2: "tiggermovil_arriba_job.PNG",     
                3: "tiggermovil_abajo_solo.PNG" ,
                4:"tiggermovil_izquierda_job_whelee.PNG",
                5:"tiggermovil_derecha_job_whelee.PNG"    
            }
            
            for direction, filename in image_files.items():
                courier_file = tiles_dir / filename
                if courier_file.exists():
                    img = pygame.image.load(str(courier_file)).convert_alpha()
                    new_size = int(CELL_SIZE * 1.5)
                    self.courier_images[direction] = pygame.transform.scale(img, (new_size, new_size))
                    print(f" Cargada: {filename}")
                else:
                    print(f" No encontrada: {filename}")
                    self.courier_images[direction] = None
            
            if not self.courier_images:
                self.courier_images = {}
                
        except Exception as e:
            print(f"Error cargando imágenes del courier: {e}")
            self.courier_images = {}

    def play_Sound(self,sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def run(self):
        """Bucle principal: eventos, actualizacion y dibujo."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            if self.state == "running":
                self.elapsed_time += dt
                self.remaining_time = max(0.0, self.session_duration - self.elapsed_time)
                if self.remaining_time <= 0.0:
                    self._finish_game(reason="time_up")
            if self.state == "running":
                self.engine.update()
                self._update(dt)
                self._draw()
                self._draw_inventory()
            else:
                self._draw_end_screen()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "running":
                        self._finish_game(reason="manual")
                    else:
                        self.running = False
                    continue

                if self.state == "finished":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.running = False
                    continue

                if event.key == pygame.K_i:
                    self.show_inventory = not getattr(self, "show_inventory", False)

                if getattr(self, "show_inventory", False):
                    if event.key == pygame.K_1:
                        self.ordered_jobs = self.engine.courier.inventory.order_jobs("priority")
                    elif event.key == pygame.K_2:
                        self.ordered_jobs = self.engine.courier.inventory.order_jobs("deadline")

    def _finish_game(self, reason="manual"):
        if self.state != "running":
            return
        courier = self.engine.courier
        self.elapsed_time = min(self.elapsed_time, float(self.session_duration))
        self.remaining_time = max(0.0, self.session_duration - self.elapsed_time)
        earned_total = getattr(courier, "total_earned", self.earned)
        self.earned = earned_total
        self.state = "finished"
        self.final_stats = {
            "time_spent": self.elapsed_time,
            "time_left": self.remaining_time,
            "earned": earned_total,
            "goal": self.goal,
            "reputation": getattr(courier, "reputation", 0),
            "delivered": len(getattr(courier, "delivered_jobs", [])),
            "reason": reason,
        }
        if pygame.mixer.get_init():
            pygame.mixer.music.fadeout(500)
        pygame.display.set_caption("Courier Quest - Resultado")

    def _draw_end_screen(self):
        self.screen.fill((15, 15, 40))
        width, height = self.screen.get_size()
        box_width = int(width * 0.7)
        box_height = int(height * 0.5)
        panel = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 190))
        panel_rect = panel.get_rect(center=(width // 2, height // 2))
        self.screen.blit(panel, panel_rect)

        stats = self.final_stats or {}
        goal_value = stats.get("goal", 0.0) or 0.0
        earned_value = stats.get("earned", 0.0) or 0.0
        time_spent = stats.get("time_spent", stats.get("time", 0.0))
        time_left = stats.get("time_left", 0.0)
        reason_label = self._get_finish_reason_text(stats.get("reason"))

        try:
            goal_value = float(goal_value)
        except (TypeError, ValueError):
            goal_value = 0.0
        try:
            earned_value = float(earned_value)
        except (TypeError, ValueError):
            earned_value = 0.0
        try:
            time_spent = float(time_spent)
        except (TypeError, ValueError):
            time_spent = 0.0
        try:
            time_left = float(time_left)
        except (TypeError, ValueError):
            time_left = 0.0

        title = self.font.render("Partida finalizada", True, (255, 255, 255))
        self.screen.blit(title, (panel_rect.x + 30, panel_rect.y + 40))

        lines = [
            f"Tiempo usado: {self._format_time(time_spent)}",
            f"Tiempo restante: {self._format_time(time_left)}",
            f"Ingresos: {earned_value:.0f} / {goal_value:.0f}",
            f"Reputacion: {stats.get('reputation', 0)}",
            f"Entregas completadas: {stats.get('delivered', 0)}",
            f"Motivo: {reason_label}",
        ]

        for idx, message in enumerate(lines):
            line_surface = self.font.render(message, True, (220, 220, 220))
            self.screen.blit(line_surface, (panel_rect.x + 30, panel_rect.y + 110 + idx * 30))

        instruction = self.small_font.render("Presiona Enter o Esc para salir", True, (200, 200, 200))
        self.screen.blit(instruction, (panel_rect.x + 30, panel_rect.y + box_height - 50))

    def _format_time(self, seconds: float) -> str:
        try:
            value = float(seconds)
        except (TypeError, ValueError):
            value = 0.0
        value = max(0.0, value)
        minutes = int(value) // 60
        secs = int(value) % 60
        return f"{minutes:02d}:{secs:02d}"

    def _get_finish_reason_text(self, reason: str) -> str:
        if not reason:
            return "Desconocido"
        mapping = {
            "time_up": "Fin de jornada",
            "manual": "Finalizado por jugador",
        }
        return mapping.get(str(reason), str(reason))

    def _move_courier(self, dx, dy):
        self.engine.move_courier(dx, dy)

    def _update(self, dt: float):
        if(self.roar==True):
            self.roar=False
            self.play_Sound("roar")
        self.move_timer += dt
        if self.move_timer >= self.move_delay:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            
            self._pickup_job()

            if keys[pygame.K_UP]:
                dy = -1
                self.current_direction = 2  
            elif keys[pygame.K_DOWN]:
                dy = 1
                self.current_direction = 3  
            
            if keys[pygame.K_a]:
                dx = -1
                self.current_direction = 4  
            elif keys[pygame.K_d]:
                dx = 1
                self.current_direction = 5 
            if keys[pygame.K_LEFT]:
                dx = -1
                self.current_direction = 0  
            elif keys[pygame.K_RIGHT]:
                dx = 1
                self.current_direction = 1 
            
            if dx or dy:
                self._move_courier(dx, dy)
            
            self.move_timer = 0.0

            courier = self.engine.courier
            if dx == 0 and dy == 0 and courier.stamina < courier.stamina_max:
                courier.recover_stamina(1.0)  # recuperación al estar quieto

    def _draw(self):
        """Dibujar mapa, pedidos, courier y HUD."""
        self._draw_map()
        self._draw_jobs()
        self._draw_courier()
        self._draw_hud()
        self._draw_reputation()
        self._draw_weather_info()  


    def _draw_reputation(self):
        courier = self.engine.courier
        reputation = int(getattr(courier, "reputation", 0))
        max_reputation = 100
        star_count = 5
        star_size = 24
        star_spacing = 6
        padding = 8
        box_height = star_size + padding * 2
        stars_width = star_count * star_size + (star_count - 1) * star_spacing
        text_block_width = 110
        box_width = padding * 2 + stars_width + 10 + text_block_width

        overlay = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        top_left_x = 10
        top_left_y = 10
        self.screen.blit(overlay, (top_left_x, top_left_y))

        star_value = (reputation / max_reputation) * star_count if max_reputation else 0
        center_y = top_left_y + padding + star_size / 2
        star_origin_x = top_left_x + padding

        for index in range(star_count):
            center_x = star_origin_x + index * (star_size + star_spacing) + star_size / 2
            points = self._get_star_points(center_x, center_y, star_size / 2)

            pygame.draw.polygon(self.screen, (70, 70, 70), points)
            pygame.draw.polygon(self.screen, (20, 20, 20), points, width=2)

            fill_amount = max(0.0, min(1.0, star_value - index))
            if fill_amount > 0:
                clip_rect = pygame.Rect(
                    int(center_x - star_size / 2),
                    int(center_y - star_size / 2),
                    int(star_size * fill_amount),
                    int(star_size),
                )
                previous_clip = self.screen.get_clip()
                self.screen.set_clip(clip_rect)
                pygame.draw.polygon(self.screen, (255, 215, 0), points)
                self.screen.set_clip(previous_clip)

        text_x = star_origin_x + stars_width + 10
        label_surface = self.small_font.render("Reputacion", True, (200, 200, 200))
        self.screen.blit(label_surface, (text_x, top_left_y + 2))
        ratio_y = top_left_y + padding + 8
        ratio_text = self.small_font.render(f"{reputation:02d} / {max_reputation}", True, (255, 255, 255))
        self.screen.blit(ratio_text, (text_x, ratio_y))

        status_surface = None
        status_y = ratio_y + 18
        if reputation >= 90:
            status_surface = self.small_font.render("Bonus +5%", True, (255, 215, 0))
        elif reputation < 20:
            status_surface = self.small_font.render("Critico <20", True, (255, 80, 80))
        elif reputation < 40:
            status_surface = self.small_font.render("Riesgo", True, (255, 160, 60))

        if status_surface is not None:
            self.screen.blit(status_surface, (text_x, status_y))

    def _get_star_points(self, center_x, center_y, outer_radius, inner_ratio=0.5):
        points = []
        for i in range(10):
            angle = math.pi / 5 * i - math.pi / 2
            radius = outer_radius if i % 2 == 0 else outer_radius * inner_ratio
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            points.append((int(round(x)), int(round(y))))
        return points

    def _draw_weather_info(self):
      weather_info = self.engine.get_current_weather_info()
    
      if not weather_info:
        return
        
      condition = weather_info["condition"]
      intensity = weather_info["intensity"]
      multiplier = weather_info["speed_multiplier"]
      time_remaining = weather_info["time_remaining"]
      is_transitioning = weather_info["is_transitioning"]
      transition_progress = weather_info["transition_progress"]

      stamina_mult = self.engine.courier.get_speed_multiplier()
      self.move_delay = multiplier * stamina_mult * 0.1

    
      weather_x = self.screen.get_width() - 200
      weather_y = 10
    
      weather_bg = pygame.Surface((190, 60), pygame.SRCALPHA)
      weather_bg.fill((0, 0, 0, 128))
      self.screen.blit(weather_bg, (weather_x - 5, weather_y - 5))
    
      if condition in self.weather_icons:
        self.screen.blit(self.weather_icons[condition], (weather_x, weather_y))
        text_x = weather_x + 40
      else:
        text_x = weather_x
    
      condition_text = self.small_font.render(f"{condition}", True, (255, 255, 255))
      self.screen.blit(condition_text, (text_x, weather_y))
    
      multiplier_text = self.small_font.render(f"Velocidad: ×{multiplier:.2f}", True, (255, 255, 255))
      self.screen.blit(multiplier_text, (text_x, weather_y + 20))
    
      if is_transitioning:
        progress_text = self.small_font.render(f"Transición: {transition_progress*100:.0f}%", True, (255, 255, 150))
        self.screen.blit(progress_text, (text_x, weather_y + 40))
      else:
        time_text = self.small_font.render(f"Cambia en: {time_remaining:.0f}s", True, (255, 255, 255))
        self.screen.blit(time_text, (text_x, weather_y + 40))
    
      self._draw_weather_effects(condition, intensity)

    def _draw_weather_effects(self, condition, intensity):
     if condition == "clear":
        self._draw_sun_effect(intensity)
     elif condition == "clouds":
        self._draw_clouds_effect(intensity)
     elif condition == "rain_light":
        self._draw_rain_light_effect(intensity)
     elif condition == "rain":
        self._draw_rain_effect(intensity)
     elif condition == "storm":
        self._draw_storm_effect(intensity)
     elif condition == "fog":
        self._draw_fog_effect(intensity)
     elif condition == "wind":
        self._draw_wind_effect(intensity)
     elif condition == "heat":
        self._draw_heat_effect(intensity)
     elif condition == "cold":
        self._draw_cold_effect(intensity)

# MÉTODOS CON COLORES MUY CONTRASTANTES:

    def _draw_sun_effect(self, intensity):
    # Brillo constante del sol
     sun_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     sun_color = (255, 255, 0, int(40 * intensity))  # AMARILLO BRILLANTE
     sun_surface.fill(sun_color)
     self.screen.blit(sun_surface, (0, 0))
    
    # Rayos de sol ocasionales
     if pygame.time.get_ticks() % 2000 < 200:
        ray_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        ray_color = (255, 255, 100, int(80 * intensity))
        ray_surface.fill(ray_color)
        self.screen.blit(ray_surface, (0, 0))

    def _draw_clouds_effect(self, intensity):
     cloud_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     cloud_color = (50, 50, 50, int(80 * intensity))  # GRIS MUY OSCURO
     cloud_surface.fill(cloud_color)
     self.screen.blit(cloud_surface, (0, 0))

    def _draw_rain_light_effect(self, intensity):
     for i in range(int(10 * intensity)):
        x = (pygame.time.get_ticks() // 12 + i * 55) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 6 + i * 35) % self.screen.get_height()
        # AZUL ELECTRICO muy visible
        pygame.draw.line(self.screen, (0, 100, 255), (x, y), (x, y + 8), 2)

    def _draw_rain_effect(self, intensity):
     if not hasattr(self, '_rain_played'):
         self.play_Sound("rain")
         self._rain_played=True
     for i in range(int(15 * intensity)):
        x = (pygame.time.get_ticks() // 8 + i * 45) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 4 + i * 25) % self.screen.get_height()
        # AZUL MARINO muy oscuro
        pygame.draw.line(self.screen, (0, 0, 180), (x, y), (x, y + 12), 2)

    def _draw_storm_effect(self, intensity):
     if not hasattr(self, '_last_thunder_time'):
      self._last_thunder_time = 0

     current_time = pygame.time.get_ticks()

# Verificar que hayan pasado al menos 8 segundos desde el último trueno
     if current_time - self._last_thunder_time > 8000 and current_time % 8000 < 30:
      flash_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
      flash_surface.fill((255, 255, 255, int(150 * intensity)))
      self.screen.blit(flash_surface, (0, 0))
      self.play_Sound("thunder")
      self._last_thunder_time = current_time 
     if not hasattr(self, '_rain_played'):
         self.play_Sound("rain")
         self._rain_played=True
    # Lluvia muy intensa
     for i in range(int(20 * intensity)):
        x = (pygame.time.get_ticks() // 6 + i * 35) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 3 + i * 20) % self.screen.get_height()
        pygame.draw.line(self.screen, (0, 0, 120), (x, y), (x, y + 15), 3)
    
    # Fondo oscuro para tormenta
     storm_bg = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     storm_bg.fill((0, 0, 50, int(60 * intensity)))
     self.screen.blit(storm_bg, (0, 0))
    
     current_time = pygame.time.get_ticks()
     if current_time % 8000 < 30:  
        flash_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        flash_surface.fill((255, 255, 255, int(150 * intensity)))
        self.screen.blit(flash_surface, (0, 0))

    def _draw_fog_effect(self, intensity):
     fog_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     fog_color = (255, 255, 255, int(120 * intensity))  # BLANCO PURO
     fog_surface.fill(fog_color)
     self.screen.blit(fog_surface, (0, 0))

    def _draw_wind_effect(self, intensity):
     for i in range(int(12 * intensity)):
        x = (pygame.time.get_ticks() // 4 + i * 50) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 12 + i * 15) % self.screen.get_height()
        # VERDE NEÓN muy visible
        offset = int(8 * intensity)
        pygame.draw.line(self.screen, (0, 255, 0), 
                        (x, y), (x - offset, y + 3), 2)

    def _draw_heat_effect(self, intensity):
    # Brillo rojo-anaranjado constante
     heat_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     heat_color = (255, 50, 0, int(60 * intensity))  # ROJO ANARANJADO FUERTE
     heat_surface.fill(heat_color)
     self.screen.blit(heat_surface, (0, 0))
    
    # Ondas de calor (efecto de distorsión visual)
     if pygame.time.get_ticks() % 1800 < 150:
        wave_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        wave_color = (255, 100, 0, int(80 * intensity))
        wave_surface.fill(wave_color)
        self.screen.blit(wave_surface, (0, 0))

    def _draw_cold_effect(self, intensity):
    # Brillo azul constante
     cold_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     cold_color = (100, 200, 255, int(50 * intensity))  # AZUL CIELO BRILLANTE
     cold_surface.fill(cold_color)
     self.screen.blit(cold_surface, (0, 0))
    
    # Copos de nieve/hielo
     for i in range(int(10 * intensity)):
        x = (pygame.time.get_ticks() // 10 + i * 60) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 5 + i * 40) % self.screen.get_height()
        # Copos AZUL BLANQUECINO
        pygame.draw.line(self.screen, (200, 230, 255), 
                        (x, y), (x + 3, y + 6), 2)
        self._draw_inventory()

    def _draw_map(self):
        cmap = self.engine.city_map
        for y in range(cmap.height):
            for x in range(cmap.width):
                key = cmap.tiles[y][x]
                
                if key in ['C', 'P']: 
                    img = self.tile_images.get(key)
                    if img:
                        self.screen.blit(img, (x * CELL_SIZE, y * CELL_SIZE))
                    else:
                        name = cmap.legend[key].get("name", "")
                        if name == "calle":
                            color = (190, 190, 190)
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
                
        
        bloques_edificios = cmap.detectar_bloques()
        building_img = self.tile_images.get('B')
        window_img = self.tile_images.get('W') 
        ground_img = self.tile_images.get('G')  
        npc_image = self.tile_images.get('D')
        
        for bloque in bloques_edificios:
            x = bloque['x']
            y = bloque['y']
            w = bloque['width']
            h = bloque['height']
            
            building_rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                w * CELL_SIZE,
                h * CELL_SIZE
            )
            
            if building_img or window_img or ground_img or npc_image:
                edificio_completo = pygame.Surface((w * CELL_SIZE, h * CELL_SIZE), pygame.SRCALPHA)
                
                for i in range(w):  
                    for j in range(h):  
                        pos_x = i * CELL_SIZE
                        pos_y = j * CELL_SIZE                  
                        celda_x = x + i
                        celda_y = y + j
                        tipo_celda = cmap.tiles[celda_y][celda_x]
                        
                        if tipo_celda == 'D' and npc_image:
                            if h==1 and  w==1:
                                edificio_completo.blit(npc_image, (pos_x, pos_y))

                            elif j == h - 1:  
                                if self.tile_images.get('G_NPC'):  
                                    edificio_completo.blit(self.tile_images['G_NPC'], (pos_x, pos_y))
                            else:  
                                if self.tile_images.get('W_NPC'):  
                                    edificio_completo.blit(self.tile_images['W_NPC'], (pos_x, pos_y))
                        else:
                            if j == h - 1:
                                if ground_img:
                                    edificio_completo.blit(ground_img, (pos_x, pos_y))
                            else:  
                                if window_img:
                                    edificio_completo.blit(window_img, (pos_x, pos_y))
                                
                
                self.screen.blit(edificio_completo, building_rect)
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), building_rect)
            
            pygame.draw.rect(
                self.screen,
                (30, 30, 30),
                building_rect,
                1  
            )

    def _draw_jobs(self): 
        curr_job  = self.engine.get_last_job()
        if curr_job is not None:
            if curr_job.dropoff != (0,0):
               x1,y1 = curr_job.dropoff
               self.engine.city_map.tiles[y1][x1] = self.prev
       # se puede hace rque se imprima solo la promera vez
        for job in self.engine.jobs:
            x, y = job.pickup
            img = self.tile_images.get("PE")
            self.screen.blit(img, (x * CELL_SIZE, y * CELL_SIZE))
        for job in self.engine.courier.inventory.items:
              x, y = job.dropoff 
              self.engine.city_map.tiles[y][x]="D"
            


    def _update_job(self, job: Job):
        """
        Maneja interacciones con un job cercano usando teclas:
        - E: tomar el job (pickup → inventario).
        - Q: cancelar job (solo si aún no está tomado).
        - R: entregar job (solo si está en inventario y en dropoff).
        """
        keys = pygame.key.get_pressed()
        # Tomar job
        if keys[pygame.K_e] and job is not None:
            if job not in self.engine.courier.inventory.items:  # aún no tomado
                if self.engine.courier.pick_job(job):
                    x,y = job.dropoff 
                    self.prev = self.engine.city_map.tiles[y][x] # saca la posicion de donde se va anetregar a ver de que tipo es ante de actualizarlo
                    self.engine.jobs.remove(job)  # lo sacamos de la lista global
                    self.play_Sound("catch")
                else:
                   self.play_Sound("error")
                    
                   

        # Cancelar job (solo pickups)
        if keys[pygame.K_q] and job is not None:
            if job not in self.engine.courier.inventory.items:  # solo si aún no está tomado
                self.engine.jobs.remove(job)
                self.play_Sound("remove")

        if keys[pygame.K_r]:
            if self.engine.game_service.courier.inventory.peek_next() == job and job is not None:
               self.engine.set_last_job(job)
               self.earned += job.payout
               self.play_Sound("acept")
               self.engine.courier.deliver_job(job)
            else:
                if job in self.engine.game_service.courier.inventory.items and job is not None:
                   self.play_Sound("error")


    def _draw_courier(self):
        x, y = self.engine.courier.position
        px, py = x * CELL_SIZE, y * CELL_SIZE

        if self.courier_images and self.current_direction in self.courier_images:
            courier_img = self.courier_images[self.current_direction]
            if courier_img is not None:
                img_width, img_height = courier_img.get_size()
                draw_x = px - (img_width - CELL_SIZE) // 2
                draw_y = py - (img_height - CELL_SIZE) // 2
                self.screen.blit(courier_img, (draw_x, draw_y))
                return
        
        center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
        pygame.draw.circle(self.screen, (255, 0, 0), center, CELL_SIZE // 3)

    def _draw_hud(self):
        # Barra inferior
        w, h = self.screen.get_size()
        hud_rect = pygame.Rect(0, h - HUD_HEIGHT, w, HUD_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 30), hud_rect)

        # Tiempo
        remaining_text = f"Tiempo restante: {self._format_time(self.remaining_time)}"
        time_surf = self.font.render(remaining_text, True, (255, 255, 255))
        self.screen.blit(time_surf, (10, h - HUD_HEIGHT + 10))

        # Ingresos
        earn_surf = self.font.render(
            f"Ingresos: {int(self.earned)}/{self.goal}", True, (200, 200, 50)
        )
        self.screen.blit(earn_surf, (10, h - HUD_HEIGHT + 40))

        # Botón Inventario
        self.inv_button = pygame.Rect(w - 710, h - HUD_HEIGHT +80, 100, 30)
        pygame.draw.rect(self.screen, (70, 70, 200), self.inv_button, border_radius=5)

        btn_text = self.font.render("Inventario", True, (200, 200, 50))
        self.screen.blit(btn_text, (w - 710, h - HUD_HEIGHT + 80))
        
        # Descripcion controles
        btn_controls = self.font.render("Controles", True, (200, 200, 50))
        self.screen.blit(btn_controls, (w - 220, h - HUD_HEIGHT + 20))
        
        tomar = self.font.render(
            f"Tomar:   E", True, (200, 200, 50),
        )
        self.screen.blit(tomar, (w - 300, h - HUD_HEIGHT + 45))
        
        rechazar = self.font.render(
            f"Rechazar:   Q", True, (200, 200, 50),
        )
        self.screen.blit(rechazar, (w - 300, h - HUD_HEIGHT + 65))
        
        entregar = self.font.render(
            f"Entregar:   R", True, (200, 200, 50),
        )
        self.screen.blit(entregar, (w - 300, h - HUD_HEIGHT + 85))
        inventario = self.font.render(
            f"Inventario:   i    (cambiar 1 - 2)", True, (200, 200, 50),
        )
        self.screen.blit(inventario, (w - 300, h - HUD_HEIGHT + 105))
        salir = self.font.render(
            f'Finalizar:   Esc', True, (200, 200, 50)
        )
        self.screen.blit(salir, (w - 300, h - HUD_HEIGHT + 125))
        
        self.inv_button = pygame.Rect(w - 120, h - HUD_HEIGHT + 10, 100, 30)
        pygame.draw.rect(self.screen, (70, 70, 200), self.inv_button, border_radius=5)

        btn_text = self.font.render("Inventario", True, (255, 255, 255))
        self.screen.blit(btn_text, (w - 110, h - HUD_HEIGHT + 15))

        # Barra de stamina (energía)
        courier = self.engine.courier
        stamina_pct = courier.get_stamina_percentage()
        stamina_actual = int(courier.stamina)
        stamina_max = int(courier.stamina_max)
        stamina_state = courier.get_stamina_state()

        bar_height = HUD_HEIGHT - 20
        bar_width = 20
        bar_x = 10
        bar_y = h - HUD_HEIGHT - bar_height - 10  #  está justo encima del HUD

        # Fondo de la barra
        pygame.draw.rect(self.screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height), border_radius=4)

        # Color según estado
        if stamina_state == "Normal":
            color = (0, 200, 0)
        elif stamina_state == "Cansado":
            color = (255, 200, 0)
        else:
            color = (200, 0, 0)

        # Relleno proporcional
        fill_height = int(bar_height * stamina_pct)
        fill_y = bar_y + (bar_height - fill_height)
        pygame.draw.rect(self.screen, color, (bar_x, fill_y, bar_width, fill_height), border_radius=4)

        # Texto: número y estado
        text_x = bar_x + 30
        text_y = bar_y + bar_height // 2 - 10
        stamina_text = self.small_font.render(f"Energía: {stamina_actual}/{stamina_max}", True, (255, 255, 255))
        state_text = self.small_font.render(f"Estado: {stamina_state}", True, (255, 255, 255))
        self.screen.blit(stamina_text, (text_x, text_y))
        self.screen.blit(state_text, (text_x, text_y + 20))


    def _pickup_job(self):
        self._update_job(self.engine.job_nearly())

    
    def _draw_inventory(self):
       if not getattr(self, "show_inventory", False):
           return

       # rectángulo principal del popup
       w, h = self.screen.get_size()
       inv_rect = pygame.Rect(w//2 - 175, h//2 - 130, 400, 300)
       pygame.draw.rect(self.screen, (50, 50, 50), inv_rect, border_radius=10)
       pygame.draw.rect(self.screen, (200, 200, 200), inv_rect, 2, border_radius=10)

       # título
       title = self.font.render("Inventario", True, (255, 255, 255))
       self.screen.blit(title, (inv_rect.x + 10, inv_rect.y + 10))
       capacity = self.font.render( f"Capacidad: {self.engine.courier.inventory.max_weight} kg." , True, (255, 255, 255))
       self.screen.blit(capacity, (inv_rect.x + 210, inv_rect.y + 10))

       # botones para elegir orden
       self.priority_button = pygame.Rect(inv_rect.x + 10, inv_rect.y + 40, 120, 30)
       self.deadline_button = pygame.Rect(inv_rect.x + 220, inv_rect.y + 40, 120, 30)

       pygame.draw.rect(self.screen, (25, 25, 25), self.priority_button, border_radius=5)
       pygame.draw.rect(self.screen, (25, 25, 25), self.deadline_button, border_radius=5)

       txt_p = self.font.render("Prioridad", True, (255, 255, 255))
       txt_d = self.font.render("Entrega", True, (255, 255, 255))
       self.screen.blit(txt_p, (self.priority_button.x + 10, self.priority_button.y + 5))
       self.screen.blit(txt_d, (self.deadline_button.x + 10, self.deadline_button.y + 5))

       # mostrar items ya ordenados por el engine
       items = getattr(self, "ordered_jobs", self.engine.courier.inventory.items)
       if items:
           for i, item in enumerate(items[:5]):  # muestra hasta 5
               txt = self.small_font.render(
                   f"{item.id}:  "
                   f"Prioridad: {item.priority}  "
                  # f" Entrega:{item.deadline}"
                   f"Peso: {item.weight} kg.  "
                   f"${item.payout}", True, (200, 200, 200)
               )
               self.screen.blit(txt, (inv_rect.x + 10, inv_rect.y + 80 + i*30))
       else:
           empty = self.font.render("Vacío", True, (200, 200, 200))
           self.screen.blit(empty, (inv_rect.x + 10, inv_rect.y + 80))
