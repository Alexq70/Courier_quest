import sys
import math
import time
import json
from pathlib import Path
from typing import Optional
from Logic.entity.job import Job

import pygame
from Presentation.controller_game import controller_game
from Logic.entity.courier import Courier
from Logic.entity import courier
from Logic.entity.ia import Ia
from Logic.entity.inventory import Inventory


from Data.score_repository import ScoreRepository
from Logic.score_manager import ScoreBreakdown

CELL_SIZE = 20
HUD_HEIGHT = 180  # ajustado para asegurar espacio suficiente
FPS = 60
prev = ''
prev_ia = ''

class View_game:
    """Interfaz gráfica con Pygame para Courier Quest.""" 

    def __init__(self, player_name: Optional[str] = None, resume: bool = False, difficulty: str = "Medium"):
        """Inicializar Pygame, motor y cargar todos los assets."""
        pygame.init()
        pygame.mixer.init
        self.engine = controller_game()
        self.engine.start()

        #Mapear dificultad del menú hacia el modo de IA
        difficulty_map = {
            "Easy": 1,
            "Medium": 2,
            "Hard": 3
        }

        mode_number = difficulty_map.get(difficulty, 1)  
        self.engine.ia.set_mode(mode_number)  # ← ahora sí depende del menú

        self.player_name = (player_name or "Player").strip() or "Player"
        self.resume_requested = resume
        self.return_to_menu = False
        self.score_repository = ScoreRepository()


        # Dimensiones de pantalla
        width = self.engine.city_map.width * CELL_SIZE
        height = self.engine.city_map.height * CELL_SIZE + HUD_HEIGHT
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Courier Quest")
        self.clock = pygame.time.Clock()

        self.move_timer = 0.0
        self.move_delay = 0.15
        self.current_direction = 1  
        
        self.ia_move_timer=0.0
        self.ia_move_delay=0.15
        self.current_direction_ia = 1 
        
        

        # Ruta de las imÃ¡genes 
        assets_dir = Path(__file__).parent.parent.parent / "src" / "assets"
        tiles_dir = assets_dir / "tiles"
        
        self.courier_images = {}
        self.alonso_images = {}
        self._load_courier_images(tiles_dir)
        self._load_sounds(tiles_dir)

        font_file = assets_dir / "font.ttf"
        if font_file.exists():
            self.font = pygame.font.Font(str(font_file), 18)
            self.small_font = pygame.font.Font(str(font_file), 14)  # Fuente mÃ¡s pequeÃ±a para clima
        else:
            print(f"WARN: no hallÃ© {font_file}, usando SysFont")
            self.font = pygame.font.SysFont(None, 18)
            self.small_font = pygame.font.SysFont(None, 14)

        # Diccionario para cargar las imÃ¡genes
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

        # Iconos de clima (puedes agregar imÃ¡genes especÃ­ficas para cada condiciÃ³n)
        self.weather_icons = {}
        self._load_weather_icons(tiles_dir)

        self.running = True
        self.elapsed_time = 0.0
        self.player_interacting = False
        self.goal = self.engine.city_map.goal
        self.earned = 0.0
        self.state = "running"
        self.final_stats = None
        self.session_duration = 15 * 60
        self.remaining_time = float(self.session_duration)

        self.paused = False
        self.pause_options = ["Resume", "Save", "Main Menu", "Quit Game"]
        self.pause_index = 0
        self.pause_feedback = ""
        self.prev = None
        self.prev_ia = None
        self.pause_feedback_time = 0.0
        self.return_to_menu = False
        self.exit_game = False
        if resume:
            self._load_game_snapshot_if_available()
        else:
            self._delete_snapshot()

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
        "storm":"storm.mp3",
        "remove":"remove_item.mp3",
        "rain":"rain.mp3",
        "roar":"roar.mp3",
        "wind":"wind.mp3",
        "heat":"heat.mp3",
        "fog":"fog.mp3",
        "cold":"cold.mp3",
        "fall": "fall.mp3"
      }
    
      self.sounds = {}
    
      for key, filename in sounds_dict.items(): 
        sound_path = tiles_dir / filename
        if sound_path.exists():
            try:
                if key == "base":
                   
                    pygame.mixer.music.load(str(sound_path))
                    print(f"Musica de fondo cargada: {filename}")
                else:
                   
                    self.sounds[key] = pygame.mixer.Sound(str(sound_path))
                    print(f"Sonido cargado: {filename}")
            except Exception as e:
                print(f"Error cargando {filename}: {e}")
        else:
            print(f"Archivo no encontrado: {sound_path}")


    def _load_weather_icons(self, tiles_dir):
        """Cargar iconos para las condiciones climÃ¡ticas"""
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
                img = pygame.transform.scale(img, (30, 30))  # TamaÃ±o fijo para iconos
                self.weather_icons[condition] = img
            else:
                # Si no hay imagen, usar un placeholder con texto
                print(f"WARN: No se encontrÃ³ icono de clima: {filename}")

    def _load_courier_images(self, tiles_dir):
        """Cargar todas las imágenes del courier una sola vez."""
        try:
            image_files = {
                0: "tiggermovil_izquierda_job.PNG",
                1: "tiggermovil_derecha_job.PNG",
                2: "tiggermovil_arriba_job.PNG",
                3: "tiggermovil_abajo_solo.PNG",
                4: "tiggermovil_izquierda_job_whelee.PNG",
                5: "tiggermovil_derecha_job_whelee.PNG",
            }

            # Determinar conjunto de imágenes para la IA según mode_deliver (fallback safe)
            mode_val = 1
            try:
                mode_val = int(getattr(self.engine, "ia", None) and getattr(self.engine.ia, "mode_deliver", 1) or 1)
            except Exception:
                mode_val = 1

            if mode_val == 1:
                image_alonso = {
                    0: "fernando-izquierda.png",
                    1: "fernando-derecha.png",
                    2: "fernando-atras.png",
                    3: "fernando-frente.png",
                }
            elif mode_val == 2:
                image_alonso = {
                    0: "alonso-izquierda.png",
                    1: "alonso-derecha.png",
                    2: "alonso-atras.png",
                    3: "alonso-frente.png",
                }
            elif mode_val == 3:
                image_alonso = {
                    0: "hard-izquierda.png",
                    1: "hard-derecha.png",
                    2: "hard-atras.png",
                    3: "hard-frente.png",
                }
            else:
                image_alonso = {
                    0: "fernando-izquierda.png",
                    1: "fernando-derecha.png",
                    2: "fernando-atras.png",
                    3: "fernando-frente.png",
                }

            # Cargar imágenes del courier principal
            for direction, filename in image_files.items():
                courier_file = tiles_dir / filename
                if courier_file.exists():
                    img = pygame.image.load(str(courier_file)).convert_alpha()
                    new_size = int(CELL_SIZE * 1.5)
                    self.courier_images[direction] = pygame.transform.scale(img, (new_size, new_size))
                    print(f"Cargada: {filename}")
                else:
                    print(f"No encontrada: {filename}")
                    self.courier_images[direction] = None

            if not self.courier_images:
                self.courier_images = {}

            # Cargar imágenes específicas para la IA (alonso/hard/fernando)
            for direction, filename in image_alonso.items():
                courier_file = tiles_dir / filename
                if courier_file.exists():
                    img = pygame.image.load(str(courier_file)).convert_alpha()
                    new_size = int(CELL_SIZE * 1.5)
                    self.alonso_images[direction] = pygame.transform.scale(img, (new_size, new_size))
                    print(f"Cargada: {filename}")
                else:
                    print(f"No encontrada: {filename}")
                    self.alonso_images[direction] = None

            if not self.alonso_images:
                self.alonso_images = {}

        except Exception as e:
            print(f"Error cargando imágenes del courier: {e}")
            self.courier_images = {}
            self.alonso_images = {}
                    

    def play_Sound(self,sound_name,loop):
        if sound_name in self.sounds:
            self.sounds[sound_name].play(loop)
            self.sounds[sound_name].set_volume(0.5)
    
    def stop_Sound(self, sound_name):
        if hasattr(self, 'sounds') and sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.stop()

    def run(self):
            """Bucle principal: eventos, actualizacion y dibujo."""
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0
                self._handle_events()
                if self.state == "running" and not self.paused:
                    self.elapsed_time += dt
                    self.remaining_time = max(0.0, self.session_duration - self.elapsed_time)
                    if self.remaining_time <= 0.0:
                        self._finish_game(reason="time_up")

                # --- FIN POR ALCANZAR META: jugador O IA ---
                if self.state == "running" and not self.paused:
                    # jugador
                    if getattr(self, "earned", 0.0) >= float(getattr(self, "goal", 0.0) or 0.0):
                        self._finish_game(reason="total_earned")
                    # IA
                    ia = getattr(self.engine, "ia", None)
                    if ia is not None:
                        ia_earned = float(getattr(ia, "earned", 0.0) or 0.0)
                        goal_value = float(getattr(self, "goal", 0.0) or 0.0)
                        if goal_value > 0 and ia_earned >= goal_value:
                            self._finish_game(reason="ia_reached_goal")

                if self.state == "running":
                    if not self.paused:
                        self.engine.update()
                        self._update(dt)
                        #Se hace separado para no intervernir con el jugador
                        self._update_ia(dt)

                    courier = self.engine.courier
                    ia=self.engine.ia
                    defeat_reason = getattr(courier, "defeat_reason", None)
                    if defeat_reason and self.state == "running":
                        self._finish_game(reason=defeat_reason)

                if self.state == "running":
                    self._draw()
                    if self.paused:
                        self._draw_pause_menu()
                    else:
                        self._draw_inventory()
                else:
                    self._draw_end_screen()
                pygame.display.flip()

            pygame.quit()
            return {"return_to_menu": self.return_to_menu, "exit_game": self.exit_game}

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_game = True
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "running":
                        self._finish_game(reason="Ended by player")
                    else:
                        self.return_to_menu = True
                        self.running = False
                    continue

                if self.state == "finished":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.return_to_menu = True
                        self.running = False
                    continue

                if self.state != "running":
                    continue

                if event.key == pygame.K_p and not self.paused:
                    self.paused = True
                    self.pause_index = 0
                    self.pause_feedback = ""
                    self.show_inventory = False
                    continue

                if self.paused:
                    if event.key == pygame.K_UP:
                        self.pause_index = (self.pause_index - 1) % len(self.pause_options)
                    elif event.key == pygame.K_DOWN:
                        self.pause_index = (self.pause_index + 1) % len(self.pause_options)
                    elif event.key == pygame.K_RETURN:
                        self._execute_pause_option()
                    continue

                if event.key == pygame.K_i:
                    self.show_inventory = not getattr(self, "show_inventory", False)
                    
                if event.key == pygame.K_c:
                     self.show_controls = not getattr(self, "show_controls", False)
                     self.show_inventory = False

                if getattr(self, "show_inventory", False):
                    if event.key == pygame.K_1:
                        self.ordered_jobs = self.engine.courier.inventory.ordered_jobs("priority")
                    elif event.key == pygame.K_2:
                        self.ordered_jobs = self.engine.courier.inventory.ordered_jobs("deadline")

    def _finish_game(self, reason: str = "unknown"):
        """Finaliza la partida y prepara las estadísticas para la pantalla final."""
        courier = self.engine.courier

        # Asegurar tiempos consistentes
        self.elapsed_time = min(self.elapsed_time, float(self.session_duration))
        self.remaining_time = max(0.0, self.session_duration - self.elapsed_time)

        # Mantener compatibilidad con total_earned histórico
        earned_total = float(getattr(courier, "total_earned", self.earned) or self.earned)
        self.earned = earned_total

        # tiempos
        total_duration = int(getattr(self, "session_duration", 15 * 60))
        remaining = int(getattr(self, "remaining_time", 0))
        time_spent = max(0, total_duration - remaining)
        time_left = max(0, remaining)

        # valores generales
        goal_value = float(getattr(self, "goal", 0.0) or 0.0)

        # Player (courier) stats
        player_earned = float(getattr(self, "earned", 0.0) or 0.0)
        player_deliveries = int(len(getattr(courier, "delivered_jobs", []) or []))
        player_reputation = float(getattr(courier, "reputation", 0.0) or 0.0)
        player_points = int(getattr(self, "points", int(player_earned)))  # fallback
        player_time_bonus = int(getattr(self, "time_bonus", 0))
        player_penalties = int(getattr(self, "penalties", 0))

        # IA stats
        ia = getattr(self.engine, "ia", None)
        ia_earned = float(getattr(ia, "earned", 0.0) or 0.0)
        ia_deliveries = int(len(getattr(ia, "delivered_jobs", []) or []))
        ia_reputation = float(getattr(ia, "reputation", 0.0) or 0.0)
        # Si el ScoreManager mantiene breakdown por actor, se podría extraer aquí.
        ia_points = int(getattr(ia, "points", int(ia_earned)))  # fallback
        ia_time_bonus = int(getattr(ia, "time_bonus", 0))
        ia_penalties = int(getattr(ia, "penalties", 0))

        # Determinar ganador (priorizar alcanzar la meta)
        if goal_value > 0:
            if ia_earned >= goal_value and player_earned >= goal_value:
                winner = "Tie"
            elif ia_earned >= goal_value:
                winner = "IA"
            elif player_earned >= goal_value:
                winner = "Player"
            else:
                # ninguno alcanzó meta: quien tenga más earned
                if ia_earned > player_earned:
                    winner = "IA"
                elif player_earned > ia_earned:
                    winner = "Player"
                else:
                    winner = "Tie"
        else:
            # sin goal definido, comparar earned
            if ia_earned > player_earned:
                winner = "IA"
            elif player_earned > ia_earned:
                winner = "Player"
            else:
                winner = "Tie"

        # motivo final
        final_reason = reason or getattr(self, "final_reason", "unknown")

        # Guardar estadísticas planas (compatibilidad con el resto del código)
        self.final_stats = {
            "player_name": getattr(self, "player_name", "Player"),
            "time_spent": int(time_spent),
            "time_left": int(time_left),
            "points": player_points,
            "time_bonus": player_time_bonus,
            "penalties": player_penalties,
            "earned": float(player_earned),
            "goal": float(goal_value),
            "reputation": player_reputation,
            "deliveries": player_deliveries,
            "reason": final_reason,
            # IA résumé (para compatibilidad con pantallas que esperan claves ia_*)
            "ia_earned": ia_earned,
            "ia_delivered": ia_deliveries,
            "ia_reputation": ia_reputation,
            # Resultado
            "winner": winner,
            # Además, datos estructurados por entidad
            "player_stats": {
                "earned": player_earned,
                "delivered": player_deliveries,
                "reputation": player_reputation,
                "points": player_points,
                "time_bonus": player_time_bonus,
                "penalties": player_penalties,
            },
            "ia_stats": {
                "earned": ia_earned,
                "delivered": ia_deliveries,
                "reputation": ia_reputation,
                "points": ia_points,
                "time_bonus": ia_time_bonus,
                "penalties": ia_penalties,
            },
        }

        # cambiar estado para que dibuje la pantalla final
        self.state = "finished"

    def _store_score_record(self, score_data: dict, reputation_value: float, delivered_count: int, reason: str) -> None:
        repository = getattr(self, "score_repository", None)
        if repository is None:
            return
        try:
            record = {
                "player_name": self.player_name,
                "total_points": float(score_data.get("total_points", 0.0)),
                "base_income": float(score_data.get("base_income", 0.0)),
                "penalties": float(score_data.get("penalty_total", 0.0)),
                "time_bonus": float(score_data.get("time_bonus", 0.0)),
                "earned": float(self.earned),
                "goal": float(self.goal),
                "reputation": float(reputation_value),
                "delivered": int(delivered_count),
                "time_spent": float(self.elapsed_time),
                "time_left": float(self.remaining_time),
                "finished_at": float(time.time()),
                "reason": reason,
            }
            repository.append(record)
        except Exception as exc:
            print(f"[Score] Unable to store score: {exc}")

    def _draw_end_screen(self):
        """Dibuja la pantalla de fin de sesión con las mismas stats del ejemplo."""
        if not getattr(self, "final_stats", None):
            return

        stats = self.final_stats
        w, h = self.screen.get_size()

        # Fondo semi-transparente y panel central
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        panel_w, panel_h = min(600, w - 80), min(420, h - 120)
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.screen, (18, 20, 30), panel)
        pygame.draw.rect(self.screen, (30, 30, 40), panel, 8)

        # Título
        title = self.font.render("Session complete", True, (255, 255, 255))
        self.screen.blit(title, (panel_x + 20, panel_y + 20))

        # Formatear tiempos mm:ss
        def fmt(t):
            m = int(t) // 60
            s = int(t) % 60
            return f"{m:02d}:{s:02d}"

        lines = [
            f"Player: {stats.get('player_name','Player')}",
            f"Time spent: {fmt(stats.get('time_spent', 0))}",
            f"Time left: {fmt(stats.get('time_left', 0))}",
            f"Points: {stats.get('points', 0)}",
            f"Time bonus: {stats.get('time_bonus', 0):+d}",
            f"Penalties: {stats.get('penalties', 0):+d}",
            f"Earnings: {int(stats.get('earned',0))} / {int(stats.get('goal',0))}",
            f"Reputation: {int(stats.get('reputation',0))}",
            f"Deliveries: {int(stats.get('deliveries',0))}",
            f"Reason: {stats.get('reason','')}",
        ]

        # Texto en panel
        start_y = panel_y + 80
        for i, text in enumerate(lines):
            surf = self.small_font.render(text, True, (200, 200, 200))
            self.screen.blit(surf, (panel_x + 28, start_y + i * 30))

        # Instrucciones para salir
        instr = self.small_font.render("Press Enter or Esc to exit", True, (150, 150, 150))
        self.screen.blit(instr, (panel_x + 28, panel_y + panel_h - 40))

        # (Opcional) mostrar IA stats en columna a la derecha si hay espacio
        if panel_w > 420:
            ia_x = panel_x + panel_w - 200
            ia_y = panel_y + 80
            ia_lines = [
                "IA stats:",
                f"Earned: {int(stats.get('ia_earned',0))}",
                f"Delivered: {int(stats.get('ia_delivered',0))}",
                f"Reputation: {int(stats.get('ia_reputation',0))}",
            ]
            for j, t in enumerate(ia_lines):
                surf = self.small_font.render(t, True, (200, 200, 200))
                self.screen.blit(surf, (ia_x, ia_y + j * 26))

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
            return "Unknown"
        mapping = {
            "time_up": "Shift complete",
            "manual": "Ended by player",
            "reputation": "Critical reputation",
        }
        return mapping.get(str(reason), str(reason))

    def _execute_pause_option(self) -> None:
        option = self.pause_options[self.pause_index]
        if option == "Resume":
            self.paused = False
        elif option == "Save":
            self._save_game_snapshot()
        elif option == "Main Menu":
            self.paused = False
            self.return_to_menu = True
            self.exit_game = False
            self.running = False
        elif option == "Quit Game":
            self.exit_game = True
            self.return_to_menu = False
            self.running = False

    def _get_save_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "saves" / "pause_save.json"

    def _serialize_job(self, job: Job) -> dict:
        return {
            "id": getattr(job, "id", None),
            "pickup": list(getattr(job, "pickup", (0, 0))),
            "dropoff": list(getattr(job, "dropoff", (0, 0))),
            "payout": float(getattr(job, "payout", 0.0)),
            "deadline": getattr(job, "deadline_raw", getattr(job, "deadline", None)),
            "weight": float(getattr(job, "weight", 0.0)),
            "priority": int(getattr(job, "priority", 0)),
            "release_time": getattr(job, "release_time", None),
        }

    def _deserialize_job(self, data: dict) -> Job:
        return Job(
            id=data.get("id"),
            pickup=tuple(data.get("pickup", (0, 0))),
            dropoff=tuple(data.get("dropoff", (0, 0))),
            payout=float(data.get("payout", 0.0)),
            deadline=data.get("deadline"),
            weight=float(data.get("weight", 0.0)),
            priority=int(data.get("priority", 0)),
            release_time=data.get("release_time"),
        )

    def _serialize_weather_state(self) -> dict:
        simulator = getattr(self.engine, "weather_simulator", None)
        if not simulator:
            return {}
        return {
            "current_condition": simulator.current_condition,
            "current_intensity": simulator.current_intensity,
            "current_speed_multiplier": simulator.current_speed_multiplier,
            "is_transitioning": simulator.is_transitioning,
            "burst_start_time": simulator.burst_start_time,
            "burst_duration": simulator.burst_duration,
            "transition_duration": simulator.transition_duration,
            "transition_start_time": simulator.transition_start_time,
            "target_condition": getattr(simulator, "target_condition", None),
            "target_intensity": getattr(simulator, "target_intensity", None),
            "target_multiplier": getattr(simulator, "target_multiplier", None),
        }

    def _apply_weather_snapshot(self, data: dict) -> None:
        simulator = getattr(self.engine, "weather_simulator", None)
        
        if not simulator:
            return
        simulator.current_condition = data.get("current_condition", simulator.current_condition)
        simulator.current_intensity = data.get("current_intensity", simulator.current_intensity)
        simulator.current_speed_multiplier = data.get("current_speed_multiplier", simulator.current_speed_multiplier)
        simulator.is_transitioning = data.get("is_transitioning", simulator.is_transitioning)
        simulator.burst_start_time = data.get("burst_start_time", simulator.burst_start_time)
        simulator.burst_duration = data.get("burst_duration", simulator.burst_duration)
        simulator.transition_duration = data.get("transition_duration", simulator.transition_duration)
        simulator.transition_start_time = data.get("transition_start_time", simulator.transition_start_time)
        target_condition = data.get("target_condition")
        if target_condition:
            simulator.target_condition = target_condition
            simulator.target_intensity = data.get("target_intensity", simulator.current_intensity)
            simulator.target_multiplier = data.get("target_multiplier", simulator.current_speed_multiplier)
        courier = getattr(self.engine, "courier", None)
        if courier:
            courier.weather = simulator.current_condition

    def _save_game_snapshot(self):
        """Guarda snapshot mínimo incluyendo estado de la IA y del mapa."""
        save_path = self._get_save_path()
        save_path.parent.mkdir(parents=True, exist_ok=True)

        def _job_to_dict(job):
            if job is None:
                return None
            return {
                "id": getattr(job, "id", None),
                "pickup": list(getattr(job, "pickup", (0, 0))),
                "dropoff": list(getattr(job, "dropoff", (0, 0))),
                "payout": float(getattr(job, "payout", 0.0) or 0.0),
                "weight": float(getattr(job, "weight", 0.0) or 0.0),
                "priority": int(getattr(job, "priority", 0) or 0),
                "deadline": getattr(job, "deadline", None),
                "release_time": getattr(job, "release_time", None),
            }

        courier = getattr(self.engine, "courier", None)
        ia = getattr(self.engine, "ia", None)

        snapshot = {
            "saved_at": time.time(),
            "player_name": getattr(self, "player_name", None),
            "state": getattr(self, "state", "running"),
            "elapsed_time": float(getattr(self, "elapsed_time", 0.0) or 0.0),
            "remaining_time": float(getattr(self, "remaining_time", 0.0) or 0.0),
            "earned": float(getattr(self, "earned", 0.0) or 0.0),
            "goal": float(getattr(self, "goal", 0.0) or 0.0),
            "jobs": [],
            "courier": None,
            "ia": None,
            "map": None,
        }

        # engine.jobs
        try:
            for j in getattr(self.engine, "jobs", []) or []:
                jd = _job_to_dict(j)
                if jd:
                    snapshot["jobs"].append(jd)
        except Exception:
            snapshot["jobs"] = []

        # courier
        if courier is not None:
            try:
                snapshot["courier"] = {
                    "position": list(getattr(courier, "position", (0, 0))),
                    "stamina": float(getattr(courier, "stamina", 0.0) or 0.0),
                    "stamina_max": float(getattr(courier, "stamina_max", 100.0) or 100.0),
                    "reputation": float(getattr(courier, "reputation", 0.0) or 0.0),
                    "delivered_jobs": [getattr(j, "id", None) for j in getattr(courier, "delivered_jobs", []) or []],
                    "inventory": [],
                    "earned": float(getattr(courier, "earned", getattr(courier, "total_earned", 0.0) or 0.0)),
                }
                if getattr(courier, "inventory", None):
                    try:
                        for j in courier.inventory.get_all() or []:
                            jd = _job_to_dict(j)
                            if jd:
                                snapshot["courier"]["inventory"].append(jd)
                    except Exception:
                        snapshot["courier"]["inventory"] = []
            except Exception:
                snapshot["courier"] = None

        # IA
        if ia is not None:
            try:
                ia_inv = []
                if getattr(ia, "inventory", None):
                    try:
                        for j in ia.inventory.get_all() or []:
                            jd = _job_to_dict(j)
                            if jd:
                                ia_inv.append(jd)
                    except Exception:
                        ia_inv = []
                snapshot["ia"] = {
                    "position": list(getattr(ia, "position", (0, 0))),
                    "stamina": float(getattr(ia, "stamina", 0.0) or 0.0),
                    "stamina_max": float(getattr(ia, "stamina_max", 100.0) or 100.0),
                    "reputation": float(getattr(ia, "reputation", 0.0) or 0.0),
                    "delivered_jobs": [getattr(j, "id", None) for j in getattr(ia, "delivered_jobs", []) or []],
                    "inventory": ia_inv,
                    "earned": float(getattr(ia, "earned", 0.0) or 0.0),
                }
            except Exception:
                snapshot["ia"] = None

        # Map (guardar lo mínimo necesario para reanudar mismo mapa)
        try:
            cmap = getattr(self.engine, "city_map", None)
            if cmap is not None:
                # tiles may be nested lists; JSON supports lists
                tiles = getattr(cmap, "tiles", None)
                snapshot["map"] = {
                    "width": int(getattr(cmap, "width", 0)),
                    "height": int(getattr(cmap, "height", 0)),
                    "tiles": tiles,
                    "goal": getattr(cmap, "goal", getattr(self, "goal", 0)),
                }
        except Exception:
            snapshot["map"] = None

        try:
            save_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
            self.pause_feedback = "Game saved"
            self.pause_feedback_time = time.time()
        except Exception as exc:
            self.pause_feedback = f"Save error"
            print(f"[ERROR] saving snapshot: {exc}")

    def _load_game_snapshot_if_available(self) -> None:
        save_path = self._get_save_path()
        if not save_path.exists():
            return
        try:
            snapshot = json.loads(save_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[Save] Could not read snapshot: {exc}")
            return
        try:
            self._apply_snapshot(snapshot)
            print("[Save] Snapshot loaded successfully.")
        except Exception as exc:
            print(f"[Save] Could not apply snapshot: {exc}")

    def _apply_snapshot(self, snapshot: dict) -> None:
        """Aplica snapshot: restaura mapa, jobs, courier e IA (minimamente)."""
        if not isinstance(snapshot, dict):
            return

        # restore simple scalars
        self.player_name = snapshot.get("player_name", self.player_name)
        self.state = "running"
        self.elapsed_time = max(0.0, float(snapshot.get("elapsed_time", self.elapsed_time)))
        self.remaining_time = max(0.0, float(snapshot.get("remaining_time", self.remaining_time)))
        self.earned = float(snapshot.get("earned", self.earned))
        self.goal = float(snapshot.get("goal", self.goal))

        # Restore map if provided
        map_snap = snapshot.get("map")
        if map_snap:
            try:
                cmap = getattr(self.engine, "city_map", None)
                if cmap:
                    if "tiles" in map_snap and map_snap.get("tiles") is not None:
                        cmap.tiles = map_snap.get("tiles")
                    if "width" in map_snap and map_snap.get("width") is not None:
                        cmap.width = int(map_snap.get("width"))
                    if "height" in map_snap and map_snap.get("height") is not None:
                        cmap.height = int(map_snap.get("height"))
                    cmap.goal = map_snap.get("goal", getattr(cmap, "goal", self.goal))
                else:
                    # si engine no tiene city_map, intentar crear uno mínimo (depende de la implementación)
                    try:
                        from Logic.city_map import CityMap
                        new_map = CityMap(width=int(map_snap.get("width", 0)), height=int(map_snap.get("height", 0)))
                        new_map.tiles = map_snap.get("tiles", new_map.tiles)
                        new_map.goal = map_snap.get("goal", self.goal)
                        self.engine.city_map = new_map
                    except Exception:
                        pass
            except Exception as e:
                print(f"[WARN] restoring map failed: {e}")

        # Restore jobs
        try:
            jobs = [self._deserialize_job(jd) for jd in snapshot.get("jobs", []) or []]
            self.engine.jobs = jobs
            if getattr(self.engine, "game_service", None):
                try:
                    self.engine.game_service.set_jobs(jobs)
                except Exception:
                    pass
        except Exception:
            pass

        # Restore courier
        courier = getattr(self.engine, "courier", None)
        cdata = snapshot.get("courier", {}) or {}
        if courier and cdata:
            try:
                if cdata.get("position") is not None:
                    courier.position = tuple(cdata.get("position"))
                courier.stamina = float(cdata.get("stamina", getattr(courier, "stamina", 0.0)))
                courier.stamina_max = float(cdata.get("stamina_max", getattr(courier, "stamina_max", 100.0)))
                courier.reputation = float(cdata.get("reputation", getattr(courier, "reputation", 0.0)))
                courier.total_earned = float(cdata.get("earned", getattr(courier, "total_earned", getattr(courier, "earned", 0.0))))
                # restore inventory
                try:
                    if getattr(courier, "inventory", None):
                        courier.inventory.items.clear()
                except Exception:
                    courier.inventory = Inventory(getattr(courier, "max_weight", 100.0))
                for jd in cdata.get("inventory", []) or []:
                    job_obj = self._deserialize_job(jd)
                    if job_obj:
                        courier.inventory.add_job(job_obj)
                courier.delivered_jobs = [self._deserialize_job(jd) for jd in cdata.get("delivered_jobs", []) or []]
            except Exception as e:
                print(f"[WARN] restoring courier: {e}")

        # Restore IA
        ia = getattr(self.engine, "ia", None)
        ia_data = snapshot.get("ia", {}) or {}
        if ia and ia_data:
            try:
                if ia_data.get("position") is not None:
                    ia.position = tuple(ia_data.get("position"))
                ia.stamina = float(ia_data.get("stamina", getattr(ia, "stamina", 0.0)))
                ia.stamina_max = float(ia_data.get("stamina_max", getattr(ia, "stamina_max", 100.0)))
                ia.reputation = float(ia_data.get("reputation", getattr(ia, "reputation", 0.0)))
                ia.earned = float(ia_data.get("earned", getattr(ia, "earned", 0.0)))
                # restore IA inventory
                try:
                    if getattr(ia, "inventory", None):
                        ia.inventory.items.clear()
                except Exception:
                    ia.inventory = Inventory(getattr(ia, "max_weight", 100.0))
                for jd in ia_data.get("inventory", []) or []:
                    job_obj = self._deserialize_job(jd)
                    if job_obj:
                        ia.inventory.add_job(job_obj)
                ia.delivered_jobs = [self._deserialize_job(jd) for jd in ia_data.get("delivered_jobs", []) or []]
            except Exception as e:
                print(f"[WARN] restoring ia: {e}")

        # restore weather/score etc if present (existing code handles it)
        try:
            if "score_breakdown" in snapshot and getattr(self.engine, "score_manager", None):
                sdata = snapshot.get("score_breakdown")
                if sdata:
                    breakdown = ScoreBreakdown(
                        base_income=float(sdata.get("base_income", 0.0)),
                        penalty_total=float(sdata.get("penalty_total", 0.0)),
                        time_bonus=float(sdata.get("time_bonus", 0.0)),
                    )
                    self.engine.score_manager._breakdown = breakdown
        except Exception:
            pass

        self._apply_weather_snapshot(snapshot.get("weather", {}) or {})
        self.paused = False
        self.pause_feedback = ""
        self.pause_feedback_time = 0.0

    def _delete_snapshot(self) -> None:
        save_path = self._get_save_path()
        try:
            if save_path.exists():
                save_path.unlink()
        except OSError as exc:
            print(f"[Save] Could not remove snapshot: {exc}")

    def _draw_pause_menu(self) -> None:
        width, height = self.screen.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        panel_width = 320
        panel_height = 260
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((20, 20, 35, 240))
        panel_rect = panel.get_rect(center=(width // 2, height // 2))
        self.screen.blit(panel, panel_rect)

        title = self.font.render("Pause", True, (255, 255, 255))
        title_x = panel_rect.x + (panel_width - title.get_width()) // 2
        self.screen.blit(title, (title_x, panel_rect.y + 30))

        option_y = panel_rect.y + 90
        spacing = 40
        for idx, option in enumerate(self.pause_options):
            selected = idx == self.pause_index
            color = (255, 255, 255) if selected else (180, 180, 180)
            label = self.font.render(option, True, color)
            self.screen.blit(label, (panel_rect.x + 80, option_y + idx * spacing))
            if selected:
                pointer = self.font.render(">", True, color)
                self.screen.blit(pointer, (panel_rect.x + 50, option_y + idx * spacing))

        if self.pause_feedback and time.time() - self.pause_feedback_time <= 3.0:
            feedback = self.small_font.render(self.pause_feedback, True, (200, 200, 100))
            feedback_x = panel_rect.x + (panel_width - feedback.get_width()) // 2
            self.screen.blit(feedback, (feedback_x, panel_rect.bottom - 70))

        instruction = self.small_font.render("Press Enter to select", True, (180, 180, 180))
        instr_x = panel_rect.x + (panel_width - instruction.get_width()) // 2
        self.screen.blit(instruction, (instr_x, panel_rect.bottom - 25))

    def _move_courier(self, dx, dy, record_step=True):
        self.engine.move_courier(dx, dy, record_step)
        
    def _move_ia(self, dx, dy, record_step=True):
        self.engine.move_ia(dx, dy, record_step)
        
             
    def _update(self, dt: float):
     if self.roar == True:
        self.roar = False
        self.play_Sound("roar", 0)
        
     self.move_timer += dt
     if self.move_timer >= self.move_delay:
        keys = pygame.key.get_pressed()
        dx = dy = 0
        self._pickup_job()
        if keys[pygame.K_BACKSPACE]:
            dx
            self._move_courier(dx, dy,False)
            self.move_timer = 0
        else:
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
              self.engine.include_step(self.engine.courier.position)
              self._move_courier(dx, dy,True)
              self.move_timer = 0  

            courier = self.engine.courier
            if dx == 0 and dy == 0 and courier.stamina < courier.stamina_max:
                courier.recover_stamina(1.0) 
                
                
    def _update_ia(self, dt: float):
        """Actualiza movimiento de la IA con control de tiempo."""
        jobs = self.engine.jobs
        next_movement = self.engine.ia.next_movement_ia(jobs)
        

        # acumula tiempo del movimiento IA
        #   Tuve que usar su propio mover timer y delay por que sino anda todo loco
        self.ia_move_timer += dt

        if self.ia_move_timer >= self.ia_move_delay:
            self.ia_move_timer = 0.0

            dx = dy = 0
            prev_pos = self.engine.ia.position
            if next_movement[0] == 2:  # UP
                dy = -1
                self.current_direction_ia = 2
            elif next_movement[0] == 3:  # DOWN
                dy = 1
                self.current_direction_ia = 3
            elif next_movement[0] == 0:  # LEFT
                dx = -1
                self.current_direction_ia = 0
            elif next_movement[0] == 1:  # RIGHT
                dx = 1
                self.current_direction_ia = 1

            # Mover solo 1 celda por tick, evitando saltos grandes
            self.engine.move_ia(dx, dy)
            
            if not self.player_interacting:
                self._pickup_job_ia()

            # Recuperación de energía de la IA cuando no se mueve
            ia = self.engine.ia
            if ia.position == prev_pos and ia.stamina < ia.stamina_max:
                ia.recover_stamina(1.0)

    def _movement_ia(self, dt: float): 
        jobs = self.engine.jobs
        self.move_timer += dt
        
        if self.move_timer >= self.move_delay:
            info_ia = self.engine.ia.next_movement_ia(jobs)
            dx = dy = info_ia[1]
            self._pickup_job_ia() 
            
            if dx or dy:
                self._move_ia(dx, dy,True)
                self.move_timer = 0  

            ia = self.engine.ia
            if dx == 0 and dy == 0 and ia.stamina < ia.stamina_max:
                ia.recover_stamina(1.0) 

    def _draw(self):
        """Dibujar mapa, pedidos, courier y HUD."""
        self._draw_map()
        self._draw_jobs()
        self._draw_players()
        self._draw_hud()
        self._draw_reputation()
        self._draw_score()
        self._draw_weather_info()  
        if getattr(self, "show_controls", False):
            self._draw_controls()


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
        label_surface = self.small_font.render("Reputation", True, (200, 200, 200))
        self.screen.blit(label_surface, (text_x, top_left_y + 2))
        ratio_y = top_left_y + padding + 8
        ratio_text = self.small_font.render(f"{reputation:02d} / {max_reputation}", True, (255, 255, 255))
        self.screen.blit(ratio_text, (text_x, ratio_y))

        status_surface = None
        status_y = ratio_y + 18
        if reputation >= 90:
            status_surface = self.small_font.render("Bonus +5%", True, (255, 215, 0))
        elif reputation < 20:
            status_surface = self.small_font.render("Critical <20", True, (255, 80, 80))
        elif reputation < 40:
            status_surface = self.small_font.render("Warning", True, (255, 160, 60))

        if status_surface is not None:
            self.screen.blit(status_surface, (text_x, status_y))

    def _draw_score(self):
        score_manager = getattr(self.engine, "score_manager", None)
        if not score_manager:
            return

        breakdown = score_manager.get_breakdown()
        total_points = int(round(breakdown.total_points))
        score_text = self.small_font.render(f"Points: {total_points}", True, (255, 255, 255))

        padding = 8
        circle_radius = 6
        width = score_text.get_width() + padding * 2 + circle_radius * 2 + 8
        height = max(score_text.get_height() + padding * 2, circle_radius * 2 + padding)

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))

        screen_width = self.screen.get_width()
        target_x = screen_width // 2 + 60
        weather_left = screen_width - 210
        max_x = max(10, weather_left - width - 10)
        top_x = min(target_x, max_x)
        top_x = max(10, top_x)
        top_y = 10
        self.screen.blit(overlay, (top_x, top_y))

        circle_center = (top_x + padding + circle_radius, top_y + height // 2)
        pygame.draw.circle(self.screen, (255, 215, 0), circle_center, circle_radius)

        text_x = circle_center[0] + circle_radius + 6
        text_y = top_y + (height - score_text.get_height()) // 2
        self.screen.blit(score_text, (text_x, text_y))


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
    
      condition_text = self.small_font.render(f"Condition: {condition}", True, (255, 255, 255))
      self.screen.blit(condition_text, (text_x, weather_y))
    
      multiplier_text = self.small_font.render(f"Speed: {multiplier:.2f}x", True, (255, 255, 255))
      self.screen.blit(multiplier_text, (text_x, weather_y + 20))
    
      if is_transitioning:
        progress_text = self.small_font.render(f"Transition: {transition_progress*100:.0f}%", True, (255, 255, 150))
        self.screen.blit(progress_text, (text_x, weather_y + 40))
      else:
        time_text = self.small_font.render(f"Next change in: {time_remaining:.0f}s", True, (255, 255, 255))
        self.screen.blit(time_text, (text_x, weather_y + 40))
      self._draw_weather_effects(condition, intensity,is_transitioning)

    def _draw_weather_effects(self, condition, intensity,is_transitioning):
     if condition == "clear":
        self._draw_sun_effect(intensity,is_transitioning)
     elif condition == "clouds":
        self._draw_clouds_effect(intensity,is_transitioning)
     elif condition == "rain_light":
        self._draw_rain_light_effect(intensity,is_transitioning)
     elif condition == "rain":
        self._draw_rain_effect(intensity,is_transitioning)
     elif condition == "storm":
        self._draw_storm_effect(intensity,is_transitioning)
     elif condition == "fog":
        self._draw_fog_effect(intensity,is_transitioning)
     elif condition == "wind":
        self._draw_wind_effect(intensity,is_transitioning)
     elif condition == "heat":
        self._draw_heat_effect(intensity,is_transitioning)
     elif condition == "cold":
        self._draw_cold_effect(intensity,is_transitioning)

# MÃTODOS CON COLORES MUY CONTRASTANTES:

    def _draw_sun_effect(self, intensity,is_transitioning):
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

    def _draw_clouds_effect(self, intensity,is_transitioning):
     cloud_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     cloud_color = (50, 50, 50, int(80 * intensity))  # GRIS MUY OSCURO
     cloud_surface.fill(cloud_color)
     self.screen.blit(cloud_surface, (0, 0))

    def _draw_rain_light_effect(self, intensity,is_transitioning):
     if is_transitioning == True and hasattr(self, '_rain_ligth_played'):
        self.stop_Sound("rain")
        del self._rain_ligth_played
        return  # Salir temprano
    
     if is_transitioning == False and not hasattr(self, '_rain_ligth_played'):
        self.play_Sound("rain",1)
        self._rain_ligth_played = True
     for i in range(int(10 * intensity)):
        x = (pygame.time.get_ticks() // 12 + i * 55) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 6 + i * 35) % self.screen.get_height()
        # AZUL ELECTRICO muy visible
        pygame.draw.line(self.screen, (0, 100, 255), (x, y), (x, y + 8), 2)

    def _draw_rain_effect(self, intensity,is_transitioning):
     if is_transitioning == True and hasattr(self, '_rain_played'):
        self.stop_Sound("storm")
        del self._rain_played
        return  # Salir temprano
    
     if is_transitioning == False and not hasattr(self, '_rain_played'):
        self.play_Sound("storm",1)
        self._rain_played = True
     for i in range(int(15 * intensity)):
        x = (pygame.time.get_ticks() // 8 + i * 45) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 4 + i * 25) % self.screen.get_height()
        # AZUL MARINO muy oscuro
        pygame.draw.line(self.screen, (0, 0, 180), (x, y), (x, y + 12), 2)

    def _draw_storm_effect(self, intensity,is_transitioning):
     if not hasattr(self, '_last_thunder_time'):
      self._last_thunder_time = 0

     current_time = pygame.time.get_ticks()

     if current_time - self._last_thunder_time > 8000 and current_time % 8000 < 30:
      flash_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
      flash_surface.fill((255, 255, 255, int(150 * intensity)))
      self.screen.blit(flash_surface, (0, 0))
      self.play_Sound("thunder",0)
      self._last_thunder_time = current_time 
     if is_transitioning == True and hasattr(self, '_storm_played'):
        self.stop_Sound("storm")
        del self._storm_played
        return  # Salir temprano
    
     if is_transitioning == False and not hasattr(self, '_storm_played'):
        self.play_Sound("storm",1)
        self._storm_played = True
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

    def _draw_fog_effect(self, intensity,is_transitioning):
     if is_transitioning == True and hasattr(self, '_fog_played'):
        self.stop_Sound("fog")
        del self._fog_played
        return  # Salir temprano
    
     if is_transitioning == False and not hasattr(self, '_fog_played'):
        self.play_Sound("fog",1)
        self._fog_played = True
     fog_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     fog_color = (255, 255, 255, int(120 * intensity))  # BLANCO PURO
     fog_surface.fill(fog_color)
     self.screen.blit(fog_surface, (0, 0))

    def _draw_wind_effect(self, intensity,is_transitioning):
     if is_transitioning == True and hasattr(self, '_wind_played'):
        self.stop_Sound("wind")
        del self._wind_played
        return  # Salir temprano
    
     if is_transitioning == False and not hasattr(self, '_wind_played'):
        self.play_Sound("wind",1)
        self._wind_played = True
     for i in range(int(12 * intensity)):
        x = (pygame.time.get_ticks() // 4 + i * 50) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 12 + i * 15) % self.screen.get_height()
        # VERDE NEÃN muy visible
        offset = int(8 * intensity)
        pygame.draw.line(self.screen, (0, 255, 0), 
                        (x, y), (x - offset, y + 3), 2)

    def _draw_heat_effect(self, intensity,is_transitioning):
     if is_transitioning == True and hasattr(self, '_heat_played'):
        self.stop_Sound("heat")
        del self._heat_played
        return  # Salir temprano
    
     if is_transitioning == False and not hasattr(self, '_heat_played'):
        self.play_Sound("heat",3)
        self._heat_played = True
    # Brillo rojo-anaranjado constante
     heat_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     heat_color = (255, 50, 0, int(60 * intensity))  # ROJO ANARANJADO FUERTE
     heat_surface.fill(heat_color)
     self.screen.blit(heat_surface, (0, 0))
    
    # Ondas de calor (efecto de distorsiÃ³n visual)
     if pygame.time.get_ticks() % 1800 < 150:
        wave_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        wave_color = (255, 100, 0, int(80 * intensity))
        wave_surface.fill(wave_color)
        self.screen.blit(wave_surface, (0, 0))

    def _draw_cold_effect(self, intensity,is_transitioning):
     if is_transitioning == True and hasattr(self, '_cold_played'):
        self.stop_Sound("cold")
        del self._cold_played
        return  # Salir temprano
    
     if is_transitioning == False and not hasattr(self, '_cold_played'):
        self.play_Sound("cold",2)
        self._cold_played = True
    # Brillo azul constante
     cold_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
     cold_color = (100, 200, 255, int(50 * intensity))  # AZUL CIELO BRILLANTE
     cold_surface.fill(cold_color)
     self.screen.blit(cold_surface, (0, 0))
    
    # Copos de nieve/hielo
     for i in range(int(10 * intensity)):
        x = (pygame.time.get_ticks() // 10 + i * 60) % self.screen.get_width()
        y = (pygame.time.get_ticks() // 5 + i * 40) % self.screen.get_height()
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

        # ------ 1. DIBUJAR TODOS LOS PICKUPS QUE AÚN EXISTEN ------
        for job in self.engine.jobs:
            x, y = job.pickup
            img = self.tile_images.get("PE")
            self.screen.blit(img, (x * CELL_SIZE, y * CELL_SIZE))


        # ------ 2. DIBUJAR DROP-OFFS DEL JUGADOR ------
        for job in self.engine.courier.inventory.get_all():
            x, y = job.dropoff
            img = self.tile_images.get("W_NPC")
            if img:
                self.screen.blit(img, (x * CELL_SIZE, y * CELL_SIZE))


        # ------ 3. DIBUJAR DROP-OFFS DE LA IA ------
        for job in self.engine.ia.inventory.get_all():
            x, y = job.dropoff
            img = self.tile_images.get("W_NPC")
            if img:
                self.screen.blit(img, (x * CELL_SIZE, y * CELL_SIZE))

            


    def _update_job(self, job: Job):
        """Gestiona aceptacion, cancelacion y entrega del pedido cercano."""
        keys = pygame.key.get_pressed()
        courier_ref = self.engine.courier
        ia_ref = self.engine.ia
        score_manager = getattr(self.engine, "score_manager", None)
        
        
        if len(courier_ref.inventory.get_all())>0 and courier_ref.posibility_lose_job():
                lost_job = courier_ref.inventory.random_job()
                if lost_job:
                    self.engine.set_last_job(lost_job)
                    courier_ref.inventory.remove_job(lost_job)
                    self.play_Sound("fall",0)
                    if score_manager is not None:
                        score_manager.register_cancellation(job)
                        courier_ref.adjust_reputation(-6)  # posibilidad de extraviar un pedido


        if keys[pygame.K_e] and job is not None:
            if job not in self.engine.courier.inventory.get_all():  # aÃºn no tomado
                if self.engine.courier.pick_job(job):
                    x,y = job.dropoff 
                    self.prev = self.engine.city_map.tiles[y][x] # saca la posicion de donde se va anetregar a ver de que tipo es ante de actualizarlo
                    self.engine.jobs.remove(job)  # lo sacamos de la lista global
                    self.play_Sound("catch",0)
                else:
                    self.play_Sound("error",0)
                    
                   

        if keys[pygame.K_q] and job is not None:
            if job in courier_ref.inventory.get_all():
                  next_job = courier_ref.inventory.peek_next()
                  if next_job == job:
                    self.engine.set_last_job(job)
                    self.engine.courier.inventory.remove_job(job)
                    self.play_Sound("remove",0)
                    if score_manager is not None:
                       score_manager.register_cancellation(job)
                       courier_ref.adjust_reputation(-4)  # Penaliza reputaciÃ³n por cancelaciÃ³n (-4 en la rÃºbrica)
                       
            else:
              self.play_Sound("error",0)       
                       

        if keys[pygame.K_r] and job is not None:
            if job in courier_ref.inventory.get_all():
                next_job = courier_ref.inventory.peek_next()
                if next_job == job:
                    self.engine.set_last_job(job)
                    self.play_Sound("acept",0)
                    delivery_result = courier_ref.deliver_job(job)
                    if score_manager is not None:
                        score_manager.register_delivery(job, delivery_result)
                    earned_delta = float(delivery_result.get("payout_applied", getattr(job, "payout", 0.0)))
                    self.earned += earned_delta
                else:
                    self.play_Sound("error",0)
                    
    def _update_job_ia(self, jobs: Job):
        """Gestiona pickup y entrega de un job para la IA."""
        ia_ref = self.engine.ia
        score_manager = getattr(self.engine, "score_manager", None)

        if len(ia_ref.inventory.get_all())>0 and ia_ref.posibility_lose_job():
            lost_job = ia_ref.inventory.random_job()
            if lost_job:
                self.engine.set_last_job(lost_job)
                ia_ref.inventory.remove_job(lost_job)
                self.play_Sound("fall",0)
                if score_manager is not None:
                    score_manager.register_cancellation(jobs)
                    ia_ref.adjust_reputation(-6)  # posibilidad de extraviar un pedido

        # ----------------- PICKUP ------------------
        if jobs is not None:
            # Si aún no está en inventario, intentar recogerlo
            if jobs not in ia_ref.inventory.get_all():

                if ia_ref.pick_job(jobs):

                    # Guardamos el job como objetivo de entrega
                    ia_ref.prev = jobs  

                    # Sacarlo del mapa para que deje de dibujarse
                    if jobs in self.engine.jobs:
                        self.engine.jobs.remove(jobs)
                    else:
                        print(f"[WARN] Job {jobs} no estaba en la lista global.")

                    # Sonido de pickup
                    self.play_Sound("catch", 0)

                else:
                    # No pudo recogerlo
                    self.play_Sound("error", 0)

        # ----------------- DELIVERY ------------------
        next_job = ia_ref.inventory.peek_next()
        if next_job is not None:
            ia_x, ia_y = ia_ref.position
            drop_x, drop_y = next_job.dropoff
            if ia_x == drop_x and ia_y == drop_y:
                self.engine.set_last_job_ia(next_job)
                self.play_Sound("acept", 0)
                # recoger resultado de la entrega y actualizar earned de la IA
                delivery_result = ia_ref.deliver_job(next_job)
                ia_ref.prev = None

                # registrar en score manager si existe
                if score_manager is not None and delivery_result.get("success"):
                    score_manager.register_delivery(next_job, delivery_result, actor="ia")
                return

        # 2) Si el "job cercano" es del inventario y estamos lo bastante cerca, también entregar
        if jobs is not None and jobs in ia_ref.inventory.get_all():
            queued = ia_ref.inventory.peek_next()
            ia_x, ia_y = ia_ref.position
            drop_x, drop_y = jobs.dropoff
            distance = abs(ia_x - drop_x) + abs(ia_y - drop_y)
            if queued == jobs and distance <= 5:
                self.engine.set_last_job_ia(jobs)
                self.play_Sound("acept", 0)
                ia_ref.deliver_job(jobs)
                ia_ref.prev = None

                    
                    

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
        
    def _draw_ia(self):
        x, y = self.engine.ia.position
        px, py = x * CELL_SIZE, y * CELL_SIZE

        if self.alonso_images and self.current_direction_ia in self.alonso_images:
            courier_img = self.alonso_images[self.current_direction_ia]
            if courier_img is not None:
                img_width, img_height = courier_img.get_size()
                draw_x = px - (img_width - CELL_SIZE) // 2
                draw_y = py - (img_height - CELL_SIZE) // 2
                self.screen.blit(courier_img, (draw_x, draw_y))
                return
        
        center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
        pygame.draw.circle(self.screen, (255, 0, 0), center, CELL_SIZE // 3)
        
    def _draw_players(self):
        self._draw_courier()
        self._draw_ia()

    def _draw_hud(self):
        """Dibuja el HUD inferior con layout responsivo y sin solapamientos."""
        w, h = self.screen.get_size()
        hud_rect = pygame.Rect(0, h - HUD_HEIGHT, w, HUD_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 30), hud_rect)

        padding = 20
        gap = 12

        # medir alturas de texto
        main_h = self.font.get_height()
        small_h = self.small_font.get_height()

        # --- Left column: tiempo + earnings jugador ---
        left_x = padding
        left_y = h - HUD_HEIGHT + padding
        remaining_text = f"Time left: {self._format_time(self.remaining_time)}"
        time_surf = self.font.render(remaining_text, True, (255, 255, 255))
        self.screen.blit(time_surf, (left_x, left_y))

        earn_y = left_y + main_h + 6
        player_earned = int(getattr(self, "earned", 0.0) or 0.0)
        goal_value = int(getattr(self, "goal", 0.0) or 0.0)
        earn_surf = self.font.render(f"Earnings: {player_earned} / {goal_value}", True, (200, 200, 50))
        self.screen.blit(earn_surf, (left_x, earn_y))

        # --- Right column: IA block (fixed width) ---
        right_w = 260
        right_x = w - padding +20 - right_w
        right_y = h - HUD_HEIGHT + padding
        ia = getattr(self.engine, "ia", None)
        if ia:
            ia_earned = int(getattr(ia, "earned", 0.0) or 0.0)
            ia_rep = int(getattr(ia, "reputation", 0.0) or 0.0)
            ia_st = float(getattr(ia, "stamina", 0.0) or 0.0)
            ia_max = float(getattr(ia, "stamina_max", 100.0) or 100.0)

            self.screen.blit(self.small_font.render("IA", True, (200, 200, 200)), (right_x, right_y))
            self.screen.blit(self.small_font.render(f"Earnings: {ia_earned}", True, (200, 200, 50)), (right_x, right_y + small_h + 6))
            self.screen.blit(self.small_font.render(f"Rep: {ia_rep}", True, (200, 200, 200)), (right_x, right_y + 2 * (small_h + 6)))

            ia_bar_y = right_y + 3 * (small_h + 6)
            ia_bar_w, ia_bar_h = right_w - 10, 12
            ia_pct = max(0.0, min(1.0, ia_st / ia_max if ia_max > 0 else 0.0))
            pygame.draw.rect(self.screen, (60, 60, 60), (right_x, ia_bar_y, ia_bar_w, ia_bar_h))
            pygame.draw.rect(self.screen, (80, 200, 120), (right_x, ia_bar_y, int(ia_bar_w * ia_pct), ia_bar_h))
            self.screen.blit(self.small_font.render(f"Stamina: {int(ia_st)}/{int(ia_max)}", True, (200, 200, 200)), (right_x, ia_bar_y + ia_bar_h + 6))



        # --- Bottom-right: tres botones distribuidos sin solaparse ---
        btn_w = int(min(160, (right_w - 155)))  # botones dentro del área derecha
        btn_h = 30
        gap_btn = 10
        # calcular base para los 3 botones alineados antes del panel derecho
        total_btns_w = btn_w * 3 + gap_btn * 2
        btn_start_x = right_x - gap_btn - total_btns_w
        btn_y = h - HUD_HEIGHT + (HUD_HEIGHT - btn_h) // 1.5

        # Inventory
        self.inv_button = pygame.Rect(btn_start_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (70, 70, 200), self.inv_button, border_radius=6)
        self.screen.blit(self.small_font.render("Inventory (I)", True, (255, 255, 255)), (self.inv_button.x + 12, self.inv_button.y + 8))

        # Controls
        controls_x = btn_start_x + btn_w + gap_btn
        self.controls_button = pygame.Rect(controls_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (70, 200, 70), self.controls_button, border_radius=6)
        self.screen.blit(self.small_font.render("Controls (C)", True, (255, 255, 255)), (self.controls_button.x + 12, self.controls_button.y + 8))

        # Pause
        pause_x = controls_x + btn_w + gap_btn
        self.pause_button = pygame.Rect(pause_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, (180, 180, 180), self.pause_button, border_radius=6)
        self.screen.blit(self.small_font.render("Pause (P)", True, (20, 20, 20)), (self.pause_button.x + 12, self.pause_button.y + 8))
        
    def _draw_controls(self):
        """Muestra el panel de controles"""
        if not getattr(self, "show_controls", False):
           return
       
        w, h = self.screen.get_size()
        rect = pygame.Rect(w//2 - 220, h//2 - 180, 400, 340)
        pygame.draw.rect(self.screen, (40, 40, 40), rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2, border_radius=10)

        title = self.font.render("Controls", True, (255, 255, 255))
        self.screen.blit(title, (rect.x + 10, rect.y + 10))

        controls = [
            "Move: (up) (Down) (Left) (Right) ( WSAD ) ",
            "Retroceder: Backspace",
            "Caballito: A - D",
            "Pick up:   E",
            "Reject:   Q",
            "Deliver:   R",
            "Inventory:   I",
            "Controls:   C",
            "Pause:   P",
            "Exit:   ESC"
        ]
        for i, text in enumerate(controls):
            surf = self.small_font.render(text, True, (200, 200, 200))
            self.screen.blit(surf, (rect.x + 20, rect.y + 50 + i * 30))
            
            
    def _pickup_job_ia(self):
        self._update_job_ia(self.engine.job_nearly_ia())
    
    def _pickup_job(self):
        self._update_job(self.engine.job_nearly())
    
    def _draw_inventory(self):
       if not getattr(self, "show_inventory", False):
           return

       w, h = self.screen.get_size()
       inv_w, inv_h = 560, 360
       inv_rect = pygame.Rect((w - inv_w) // 2, (h - inv_h) // 2, inv_w, inv_h)
       pygame.draw.rect(self.screen, (50, 50, 50), inv_rect, border_radius=10)
       pygame.draw.rect(self.screen, (200, 200, 200), inv_rect, 2, border_radius=10)

       title = self.font.render("Inventory", True, (255, 255, 255))
       self.screen.blit(title, (inv_rect.x + 10, inv_rect.y + 10))
       capacity = self.font.render(f"Capacity: {self.engine.courier.inventory.max_weight} kg.", True, (255, 255, 255))
       self.screen.blit(capacity, (inv_rect.x + inv_w - capacity.get_width() - 12, inv_rect.y + 10))

       # Orden actual (establecido por teclas 1/2)
       order_label = getattr(self, "ordered_jobs_label", None)
       if order_label is None:
           order_label = "Default"
       order_surf = self.small_font.render(f"Order: {order_label}  (Press 1:Priority  2:Deadline)", True, (180, 180, 180))
       self.screen.blit(order_surf, (inv_rect.x + 12, inv_rect.y + 46))

       # Botones de orden (visual)
       self.priority_button = pygame.Rect(inv_rect.x + 10, inv_rect.y + 72, 140, 34)
       self.deadline_button = pygame.Rect(inv_rect.x + 160, inv_rect.y + 72, 140, 34)
       pygame.draw.rect(self.screen, (40, 40, 40), self.priority_button, border_radius=6)
       pygame.draw.rect(self.screen, (40, 40, 40), self.deadline_button, border_radius=6)
       txt_p = self.small_font.render("Priority (1)", True, (255, 255, 255))
       txt_d = self.small_font.render("Deadline (2)", True, (255, 255, 255))
       self.screen.blit(txt_p, (self.priority_button.x + 10, self.priority_button.y + 6))
       self.screen.blit(txt_d, (self.deadline_button.x + 10, self.deadline_button.y + 6))

       # Obtener lista de items ordenada
       items = getattr(self, "ordered_jobs", None)
       if items is None:
           items = self.engine.courier.inventory.get_all()

       # Selection index
       if not hasattr(self, "inv_index") or self.inv_index is None:
           self.inv_index = 0
       self.inv_index = max(0, min(self.inv_index, max(0, len(items) - 1)))

       # Área lista y detalles
       list_x = inv_rect.x + 12
       list_y = inv_rect.y + 120
       list_w = int(inv_w * 0.58)
       list_h = inv_h - (list_y - inv_rect.y) - 60
       detail_x = list_x + list_w + 12
       detail_w = inv_rect.x + inv_w - detail_x - 12

       # Draw headers
       header = self.small_font.render("ID   Priority   Weight   Payout   Dropoff", True, (190, 190, 190))
       self.screen.blit(header, (list_x, list_y - 26))

       # Show up to visible_count items with simple scrolling if needed
       visible_count = min(10, max(5, list_h // 28))
       # compute scroll offset so selected item is visible
       if len(items) > visible_count:
           top_index = max(0, min(self.inv_index - visible_count // 2, len(items) - visible_count))
       else:
           top_index = 0

       for i in range(visible_count):
           idx = top_index + i
           y = list_y + i * 28
           if idx >= len(items):
               break
           job = items[idx]
           jid = getattr(job, "id", "?")
           pr = getattr(job, "priority", 0)
           wt = getattr(job, "weight", 0.0)
           pay = int(getattr(job, "payout", 0))
           drop = getattr(job, "dropoff", (0, 0))
           line = f"{str(jid):<4}   {pr:<8}   {wt:<6.1f}   ${pay:<6}   {drop[0]},{drop[1]}"
           color = (230, 230, 230) if idx == self.inv_index else (200, 200, 200)
           # highlight background for selected
           if idx == self.inv_index:
               sel_rect = pygame.Rect(list_x - 6, y - 2, list_w + 8, 26)
               pygame.draw.rect(self.screen, (30, 100, 160), sel_rect, border_radius=4)
               text_color = (255, 255, 255)
           else:
               text_color = color
           surf = self.small_font.render(line, True, text_color)
           self.screen.blit(surf, (list_x, y))

       # Detalle del item seleccionado a la derecha
       detail_y = list_y
       detail_title = self.font.render("Item details", True, (240, 240, 240))
       self.screen.blit(detail_title, (detail_x, detail_y))
       detail_y += detail_title.get_height() + 8

       if items:
           sel = items[self.inv_index]
           d_lines = [
               f"ID: {getattr(sel, 'id', '?')}",
               f"Payout: ${int(getattr(sel, 'payout', 0))}",
               f"Weight: {getattr(sel, 'weight', 0):.1f} kg",
               f"Priority: {getattr(sel, 'priority', 0)}",
               f"Pickup: {tuple(getattr(sel, 'pickup', (0,0)))}",
               f"Dropoff: {tuple(getattr(sel, 'dropoff', (0,0)))}",
               f"Deadline: {getattr(sel, 'deadline', getattr(sel, 'deadline_raw', 'N/A'))}",
               f"Release time: {getattr(sel, 'release_time', 'N/A')}",
           ]
           for line in d_lines:
               surf = self.small_font.render(line, True, (220, 220, 220))
               self.screen.blit(surf, (detail_x, detail_y))
               detail_y += surf.get_height() + 6
       else:
           empty = self.small_font.render("Inventory is empty", True, (180, 180, 180))
           self.screen.blit(empty, (detail_x, detail_y))

       # Footer instructions
       footer = self.small_font.render("Up/Down: select   R: deliver selected   Q: reject selected   Esc: close", True, (170, 170, 170))
       self.screen.blit(footer, (inv_rect.x + 12, inv_rect.y + inv_h - 36))

