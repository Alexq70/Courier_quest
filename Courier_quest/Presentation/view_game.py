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
        self.move_delay = 0.15 
        self.current_direction = 1  

        # Ruta de las imágenes 
        assets_dir = Path(__file__).parent.parent.parent / "src" / "assets"
        tiles_dir = assets_dir / "tiles"
        
        self.courier_images = {}
        self._load_courier_images(tiles_dir)

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

        # Estado del clima para la vista
        self.current_weather_display = ""
        self.weather_transition_progress = 0.0

    def _load_weather_icons(self, tiles_dir):
        """Cargar iconos para las condiciones climáticas"""
        weather_icon_mapping = {
            "clear": "weather_clear.png",
            "clouds": "weather_clouds.png", 
            "rain": "weather_rain.png",
            "rain_light": "weather_rain_light.png",
            "storm": "weather_storm.png",
            "fog": "weather_fog.png",
            "wind": "weather_wind.png",
            "heat": "weather_heat.png",
            "cold": "weather_cold.png"
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

    def run(self):
        """Bucle principal: eventos, actualización y dibujo."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.elapsed_time += dt
            
            # Actualizar el motor del juego (incluye clima)
            self.engine.update()
            
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
       for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.running = False   # 🔴 aquí va con self.
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
           if event.button == 1:  # clic izquierdo
              if hasattr(self, "inv_button") and self.inv_button.collidepoint(event.pos):
               self.show_inventory = not getattr(self, "show_inventory", False)

           if getattr(self, "show_inventory", False):
               if hasattr(self, "priority_button") and self.priority_button.collidepoint(event.pos):
                   self.engine.sort_by_priority()
               elif hasattr(self, "deadline_button") and self.deadline_button.collidepoint(event.pos):
                   self.engine.sort_by_deadline()


 

    def _move_courier(self, dx, dy):
        self.engine.move_courier(dx, dy)

    def _update(self, dt: float):
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

    def _draw(self):
        """Dibujar mapa, pedidos, courier y HUD."""
        self._draw_map()
        self._draw_jobs()
        self._draw_courier()
        self._draw_hud()
        self._draw_weather_info()  # Nueva función para mostrar clima

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

      self.move_delay=multiplier*0.1
    
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
     for i in range(int(15 * intensity)):
        x = (pygame.time.get_ticks() // 8 + i * 45) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 4 + i * 25) % self.screen.get_height()
        # AZUL MARINO muy oscuro
        pygame.draw.line(self.screen, (0, 0, 180), (x, y), (x, y + 12), 2)

    def _draw_storm_effect(self, intensity):
    # Lluvia muy intensa
     for i in range(int(20 * intensity)):
        x = (pygame.time.get_ticks() // 6 + i * 35) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 3 + i * 20) % self.screen.get_height()
        pygame.draw.line(self.screen, (0, 0, 120), (x, y), (x, y + 15), 3)
    
    # Fondo oscuro para tormenta
     storm_bg = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     storm_bg.fill((0, 0, 50, int(60 * intensity)))  # AZUL MUY OSCURO
     self.screen.blit(storm_bg, (0, 0))
    
    # Relámpagos BLANCOS MUY BRILLANTES
     if pygame.time.get_ticks() % 1500 < 100:
        flash_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        flash_surface.fill((255, 255, 255, int(150 * intensity)))  # BLANCO PURO
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
        job = self.reprint_job(cmap)

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
                
                pygame.draw.rect(
                    self.screen,
                    (50, 50, 50),
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                    1
                )
        
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
        for job in self.engine.jobs:
            x, y = job.pickup
            img = self.tile_images.get("PE")
            self.screen.blit(img, (x * CELL_SIZE, y * CELL_SIZE))

    def _update_job(self, job):
        if self.engine.courier.inventory.add_job(job):
            self.engine.set_last_picked(job)
            self.engine.jobs.remove(job)
    def _update_job(self,job):
        keys = pygame.key.get_pressed()
        """
        Quita el pedido del mapa y actualiza el inventario
        """
        if keys[pygame.K_e] and job is not None:
          if self.engine.courier.inventory.add_job(job):
             self.engine.set_last_picked(job)
             self.engine.jobs.remove(job)
        if keys[pygame.K_q]:
             self.engine.jobs.remove(job)
    

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
        w, h = self.screen.get_size()
        hud_rect = pygame.Rect(0, h - HUD_HEIGHT, w, HUD_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 30), hud_rect)
=======
      # Barra inferior
      w, h = self.screen.get_size()
      hud_rect = pygame.Rect(0, h - HUD_HEIGHT, w, HUD_HEIGHT)
      pygame.draw.rect(self.screen, (30, 30, 30), hud_rect)

      # Tiempo
      time_surf = self.font.render(
          f"Tiempo: {int(self.elapsed_time)}s", True, (255, 255, 255)
      )
      self.screen.blit(time_surf, (10, h - HUD_HEIGHT + 10))

      # Ingresos
      earn_surf = self.font.render(
          f"Ingresos: {int(self.earned)}/{self.goal}", True, (200, 200, 50)
      )
      self.screen.blit(earn_surf, (10, h - HUD_HEIGHT + 40))

      # Botón Inventario
      self.inv_button = pygame.Rect(w - 120, h - HUD_HEIGHT + 10, 100, 30)
      pygame.draw.rect(self.screen, (70, 70, 200), self.inv_button, border_radius=5)

      btn_text = self.font.render("Inventario", True, (255, 255, 255))
      self.screen.blit(btn_text, (w - 110, h - HUD_HEIGHT + 15))
  

    def _pickup_job(self):
        self._update_job(self.engine.job_nearly())

    def reprint_job(self, map):
        job = self.engine.last_job_picked()
        dropoff = job.dropoff

        if dropoff != (0,0):
            c1, c2 = dropoff
            map.tiles[c1][c2] = 'D'
            return dropoff
    def reprint_job(self,map):
      """
      Actualiza la vista del ultimo recogido pedido en el mapa
      """
      job = self.engine.last_job_picked()
      dropoff = job.dropoff
      
      if dropoff != (0,0):
          c1,c2 = dropoff
          map.tiles[c1][c2] = 'D'

          return dropoff

    
    def _draw_inventory(self):
       if not getattr(self, "show_inventory", False):
           return

       # rectángulo principal del popup
       w, h = self.screen.get_size()
       inv_rect = pygame.Rect(w//2 - 150, h//2 - 130, 300, 260)
       pygame.draw.rect(self.screen, (50, 50, 50), inv_rect, border_radius=10)
       pygame.draw.rect(self.screen, (200, 200, 200), inv_rect, 2, border_radius=10)

       # título
       title = self.font.render("Inventario", True, (255, 255, 255))
       self.screen.blit(title, (inv_rect.x + 10, inv_rect.y + 10))

       # botones para elegir orden
       self.priority_button = pygame.Rect(inv_rect.x + 10, inv_rect.y + 40, 120, 30)
       self.deadline_button = pygame.Rect(inv_rect.x + 150, inv_rect.y + 40, 120, 30)

       pygame.draw.rect(self.screen, (100, 100, 200), self.priority_button, border_radius=5)
       pygame.draw.rect(self.screen, (200, 100, 100), self.deadline_button, border_radius=5)

       txt_p = self.font.render("Prioridad", True, (255, 255, 255))
       txt_d = self.font.render("Entrega", True, (255, 255, 255))
       self.screen.blit(txt_p, (self.priority_button.x + 10, self.priority_button.y + 5))
       self.screen.blit(txt_d, (self.deadline_button.x + 10, self.deadline_button.y + 5))

       # mostrar items ya ordenados por el engine
       items = self.engine.courier.inventory.items
       if items:
           for i, item in enumerate(items[:5]):  # muestra hasta 5
               txt = self.font.render(
                   f"{i+1}. {item.pickup}->{item.dropoff} "
                   f"${item.payout}", True, (200, 200, 50)
               )
               self.screen.blit(txt, (inv_rect.x + 10, inv_rect.y + 80 + i*30))
       else:
           empty = self.font.render("Vacío", True, (200, 200, 200))
           self.screen.blit(empty, (inv_rect.x + 10, inv_rect.y + 80))
>>>>>>> ALEXX
