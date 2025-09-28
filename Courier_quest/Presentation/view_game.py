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

        #Ruta de las imagenes 

        assets_dir = Path(__file__).parent.parent.parent / "src" / "assets"
        tiles_dir = assets_dir / "tiles"
        
        self.courier_images = {}
        self._load_courier_images(tiles_dir)

        font_file = assets_dir / "font.ttf"
        if font_file.exists():
            self.font = pygame.font.Font(str(font_file), 18)
        else:
            print(f"WARN: no hallé {font_file}, usando SysFont")
            self.font = pygame.font.SysFont(None, 18)

#diccionario para cargar las imagenes
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

        self.running = True
        self.elapsed_time = 0.0
        self.goal = self.engine.city_map.goal
        self.earned = 0.0

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

#lo arregle para simular el MVC
    def _move_courier(self,dx,dy):
        self.engine.move_courier(dx,dy)

    def _update(self, dt: float):
        self.move_timer += dt
        if self.move_timer >= self.move_delay:
            keys = pygame.key.get_pressed()
            dx = dy = 0
            
            if keys[pygame.K_e]:
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
            if keys[pygame.K_LEFT ]:
                dx = -1
                self.current_direction = 0  
            elif keys[pygame.K_RIGHT ]:
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
        #dibuja la imagen del regalo sobre la ventana nada mas si se va a hacer aleatorio ,
        #hacer logica de que se vea donde se va a dibujar el regalo y use la imagen correcta
        for job in self.engine.jobs:
            x, y = job.pickup
            img = self.tile_images.get("PE")
            self.screen.blit(img, (x * CELL_SIZE, y * CELL_SIZE))

    def _update_job(self,job):
        """
        Quita el pedido del mapa y actualiza el inventario
        """
        if self.engine.courier.inventory.add_job(job):
           self.engine.set_last_picked(job)
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
        #Es la barra de abajo de la pantalla
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

    def _pickup_job(self):
        """
        verifica si el jugador esta recogiendo un pedido, y si si lo recoge y actualiza todo
        """
        self._update_job(self.engine.job_nearly())

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

