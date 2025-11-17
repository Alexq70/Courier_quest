
import time
from typing import Tuple, List, Optional
from Logic.entity.job import Job
from Logic.entity.inventory import Inventory
from Logic.entity.city_map import CityMap
import random

class Ia:
    """
    Representa a la IA:
        - posición en el mapa
        - resistencia (energía), carga, inventario y entregas
    """

    def __init__(self, start_pos: Tuple[int, int], max_weight: float,city_map=None):
        self.position: Tuple[int, int] = start_pos
        self.max_weight: float = max_weight
        self.current_load: float = 0.0
        self.inventory: Inventory = Inventory(max_weight)
        self.delivered_jobs: List[Job] = []
        self.total_earned: float = 0.0
        self.exhausted_lock: bool = False # Bloqueo por agotamiento
        self.weather = "clear"  # valor inicial por defecto
        self.reputation = 70  # valor inicial
        self.reputation_streak = 0  # para rachas sin penalización
        self.first_late_penalty_reduced = False  # control de tardanza reducida
        self.defeat_reason: Optional[str] = None  # motivo de derrota si ocurre
        self.mode_deliver = None
        self.prev = None
        self.city_map = city_map

        # Resistencia
        self.stamina_max: float = 100.0
        self.stamina: float = 100.0

    def can_carry(self, weight: float) -> bool:
        """Verifica si el pedido cabe en el inventario"""
        return self.inventory.can_add(Job(weight=weight, **{}))

    def pick_job(self, job: Job) -> bool:
        """Intenta aceptar un pedido"""
        added = self.inventory.add_job(job)
        if added:
            self.current_load = self.inventory.total_weight()
        return added

    def deliver_job(self, job: Job) -> dict:
        """Registra la entrega y devuelve datos utiles para puntaje."""
        now = time.time()
        deadline_ts = job.get_deadline_timestamp()
        delta = None if deadline_ts is None else deadline_ts - now
        lateness_seconds = 0.0 if delta is None or delta >= 0 else -delta

        total_duration = job.get_total_duration()
        if total_duration <= 0:
            total_duration = 1.0

        reputation_before = self.reputation

        if delta is None:
            self.adjust_reputation(+3)
        elif delta >= total_duration * 0.2:
            self.adjust_reputation(+5)
        elif delta >= 0:
            self.adjust_reputation(+3)
        elif lateness_seconds <= 30:
            self.adjust_reputation(-2)
        elif lateness_seconds <= 120:
            self.adjust_reputation(-5)
        else:
            self.adjust_reputation(-10)

        base_payout = job.payout
        bonus_multiplier = 1.0
        payout = base_payout
        if self.reputation >= 90:
            bonus_multiplier = 1.05
            payout *= bonus_multiplier

        self.total_earned += payout
        self.inventory.remove_job(job)
        self.delivered_jobs.append(job)
        self.current_load = self.inventory.total_weight()

        reputation_delta = self.reputation - reputation_before

        return {
            "payout_applied": payout,
            "base_payout": base_payout,
            "bonus_multiplier": bonus_multiplier,
            "lateness_seconds": lateness_seconds,
            "reputation_delta": reputation_delta,
            "was_late": lateness_seconds > 0,
        }

    def move_ia(self, width, height, citymap, dx: int, dy: int, record_step: bool = True):
        """va a recibir en view game la coordenada cambiada"""
        if not self.can_move():
            return

        cmap = citymap

        if record_step:
            x, y = self.position
            nx, ny = x + dx, y + dy
        else:
            nx, ny = dx, dy

        if 0 <= nx < width and 0 <= ny < height and not cmap.is_blocked(nx, ny):
            self.move_to((nx, ny))

    def move_to(self, position: Tuple[int, int]) -> None:
        self.position = position
        self.stamina = max(0.0, self.stamina - self._calculate_stamina_cost())

        if self.stamina <= 0:
            self.exhausted_lock = True 

    def _calculate_stamina_cost(self) -> float:
        """Consumo por celda: -0.5 base + extras por peso y clima"""
        cost = 0.5  # base

        cost += 0.2 * max(0, self.current_load - 3)

        if self.weather in ["rain", "wind"]:
            cost += 0.1
        elif self.weather == "heat":
            cost += 0.2
        elif self.weather == "storm":
            cost += 0.3

        return cost

    def get_stamina_percentage(self) -> float:
        """Porcentaje de energía (0.0 a 1.0)"""
        return self.stamina / self.stamina_max if self.stamina_max > 0 else 0.0

    def get_stamina_state(self) -> str:
        """Estado según nivel de energía"""
        if self.stamina <= 0:
            return "Exhausted"
        elif self.stamina <= 30:
            return "Tired"
        else:
            return "Normal"

    def can_move(self) -> bool:
        if self.exhausted_lock:
            return self.stamina >= 30.0
        return self.stamina > 0.0

    def get_speed_multiplier(self) -> float:
        state = self.get_stamina_state()
        if state == "Normal":
            return 1.0
        elif state == "Tired":
            return 0.8
        else:
            return 0.0

    def recover_stamina(self, amount: float = 0.5):
        """Recupera energía gradualmente"""
        self.stamina = min(self.stamina_max, self.stamina + amount)
        if self.exhausted_lock and self.stamina >= 30.0:
            self.exhausted_lock = False

    def is_stationary(self, previous_pos: Tuple[int, int]) -> bool:
        return self.position == previous_pos
    
    def trigger_defeat(self, reason: str) -> None:
        """Marca al courier como derrotado para que la vista maneje el final."""
        if self.defeat_reason is None:
            self.defeat_reason = reason

    def adjust_reputation(self, delta: int):
        self.reputation = max(0, min(100, self.reputation + delta))

        if self.reputation < 20:
            self.trigger_defeat("reputation")

        if delta < 0:
            self.reputation_streak = 0
        else:
            self.reputation_streak += 1
            if self.reputation_streak == 3:
                self.adjust_reputation(+2)
                self.reputation_streak = 0
                
    def posibility_lose_job(self):
        """
        Probabilidad del 0,06% de perder un pedido en cada refresco del juego
        """
        r1,r2 = (random.randint(0,150),random.randint(0,150))
        if r1 == r2:
            return True
        return False
    
    
    def next_movement_ia(self,jobs):
        """
        Recibe los pedidos candidatos y retorna el proximo movimiento que va a hacer en la vista la ia
        """
        options = (self.easy_mode(jobs),self.medium_mode(jobs),self.hard_mode(jobs)) # tupla con las opciones de recorrido
        tupla = [None,None] # tupla que va a retornar (movimiento,coordenada)
        
        if self.mode_deliver == 1:   #Facil
            tupla[0] = self.obtain_movement(options[0]) # le mandamos la coordenada nueva
            tupla[1] = options[0]
            
        if self.mode_deliver == 2:   #Medio
            tupla[0] = self.obtain_movement(options[1]) # le mandamos la coordenada nueva
            tupla[1] = options[1]
        
        if self.mode_deliver == 3:    #Dificil
            tupla[0] = self.obtain_movement(options[2]) # le mandamos la coordenada nueva
            tupla[1] = options[2]
            
        return tupla # tupla con el movimiento para el view y la coordenada
    
    def set_mode(self,mode):
        """
        cambia el modo de busqueda del pedido
        """
        self.mode_deliver = mode
        return

    def easy_mode(self, jobs, city_map=None):
            current_x, current_y = self.position

            job = None
            if jobs:
                job = self.prev if self.prev else random.choice(jobs)

            target = None
            if job:
                if job in self.inventory.get_all():
                    target = getattr(job, "dropoff_position", None) or getattr(job, "dropoff", None)
                else:
                    target = getattr(job, "pickup_position", None) or getattr(job, "pickup", None)

            # Movimiento dirigido
            if target:
                tx, ty = target
                dx = 1 if tx > current_x else -1 if tx < current_x else 0
                dy = 1 if ty > current_y else -1 if ty < current_y else 0

                if random.random() < 0.9:
                    nx, ny = current_x + dx, current_y + dy
                    if self._is_valid_position(nx, ny) and (nx, ny) != self.prev:
                        return (nx, ny)

            # Movimiento aleatorio seguro
            directions = [(-1,0),(1,0),(0,-1),(0,1)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if self._is_valid_position(nx, ny) and (nx, ny) != self.prev:
                    return (nx, ny)

            return (current_x, current_y)
        
    def _is_valid_position(self, x, y):
            """Verifica si (x,y) es una calle ('C') y no edificio."""
            if 0 <= x < 29 and 0 <= y < 29 and self.city_map is not None:
                try:
                    if hasattr(self.city_map, 'tiles'):
                        return self.city_map.tiles[y][x] == 'C'
                    elif hasattr(self.city_map, 'get_tile'):
                        return self.city_map.get_tile(x, y) == 'C'
                    else:
                        return self.city_map[y][x] == 'C'
                except Exception:
                    return False
            return False
        

    def medium_mode(self, jobs):
        """
        Greedy avanzado:
        Se dirige al pickup o dropoff más cercano evitando edificios.
        Rodea obstáculos si la ruta directa está bloqueada.
        """
        if not jobs:
            return self.easy_mode(jobs)

        cx, cy = self.position
        
        # 1) Seleccionar objetivo más cercano
        best_target = None
        best_dist = float("inf")

        for job in jobs:
            if job in self.inventory.get_all():
                tx, ty = getattr(job, "dropoff_position", None) or getattr(job, "dropoff", None)
            else:
                tx, ty = getattr(job, "pickup_position", None) or getattr(job, "pickup", None)

            if tx is None or ty is None:
                continue

            d = abs(cx - tx) + abs(cy - ty)
            if d < best_dist:
                best_dist = d
                best_target = (tx, ty)

        if best_target is None:
            return self.easy_mode(jobs)

        tx, ty = best_target

        # 2) Generar candidatos ordenados por distancias
        candidates = []
        directions = [
            (cx + 1, cy),  # derecha
            (cx - 1, cy),  # izquierda
            (cx, cy + 1),  # abajo
            (cx, cy - 1),  # arriba
        ]

        for nx, ny in directions:
            if self._is_valid_position(nx, ny):
                d = abs(nx - tx) + abs(ny - ty)
                candidates.append(((nx, ny), d))

        if not candidates:
            return self.easy_mode(jobs)

        # 3) Ordenar por el movimiento que más reduce la distancia
        candidates.sort(key=lambda x: x[1])

        return candidates[0][0]

            
            
    def hard_mode(self, jobs):
        """
        Hard Mode: A* pathfinding real.
        Rodea los edificios, evita loops y encuentra la ruta óptima.
        """

        if not jobs:
            return self.easy_mode(jobs)

        cx, cy = self.position

        # buscar job objetivo
        best_job = None
        best_dist = float("inf")

        for job in jobs:
            if job in self.inventory.get_all():
                tx, ty = getattr(job, "dropoff_position", None) or getattr(job, "dropoff", None)
            else:
                tx, ty = getattr(job, "pickup_position", None) or getattr(job, "pickup", None)

            if tx is None or ty is None:
                continue

            d = abs(cx - tx) + abs(cy - ty)
            if d < best_dist:
                best_dist = d
                best_job = job

        if not best_job:
            return self.medium_mode(jobs)

        if best_job in self.inventory.get_all():
            target = getattr(best_job, "dropoff_position", None) or getattr(best_job, "dropoff", None)
        else:
            target = getattr(best_job, "pickup_position", None) or getattr(best_job, "pickup", None)

        if not target:
            return self.medium_mode(jobs)

        # ejecutar A*
        path = self.astar(self.position, target)

        if path and len(path) > 1:
            return path[1]   # siguiente paso

        # si A* falla, fallback al greedy
        return self.medium_mode(jobs)
    
    def _neighbors(self, node):
        x, y = node
        candidates = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        return [(nx,ny) for nx,ny in candidates if self._is_valid_position(nx,ny)]
    
    def astar(self, start, goal, max_nodes=8000):
        import heapq

        def h(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))

        came_from = {start: None}
        g = {start: 0}

        processed = 0

        while open_set and processed < max_nodes:
            _, current = heapq.heappop(open_set)
            processed += 1

            if current == goal:
                # reconstruir ruta
                path = []
                c = current
                while c:
                    path.append(c)
                    c = came_from[c]
                return list(reversed(path))

            for nb in self._neighbors(current):
                new_cost = g[current] + 1
                if new_cost < g.get(nb, float("inf")):
                    g[nb] = new_cost
                    f = new_cost + h(nb, goal)
                    came_from[nb] = current
                    heapq.heappush(open_set, (f, nb))

        return None



    def obtain_movement(self, other):
        """
        Recibe una coordenada objetivo 'other' (x,y) y devuelve un código de dirección entero:
        2 = UP, 3 = DOWN, 0 = LEFT, 1 = RIGHT
        Si other es None, retorna None.
        """
        if other is None:
            return None

        # asegurarnos que other tiene formato (x,y)
        try:
            ox, oy = int(other[0]), int(other[1])
        except Exception:
            return None

        if self.position[0] > ox:
            return 2  # UP
        if self.position[0] < ox:
            return 3  # DOWN
        if self.position[1] > oy:
            return 0  # LEFT
        if self.position[1] < oy:
            return 1  # RIGHT

        # Si ya estamos en la misma celda
        return None
