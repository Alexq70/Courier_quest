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
        """Inicializa la IA con posición inicial y capacidad máxima.
        
        Args:
            start_pos: Posición inicial (x, y) de la IA
            max_weight: Peso máximo que puede cargar la IA
            city_map: Instancia del mapa de la ciudad para navegación (opcional)
        """
        self.position: Tuple[int, int] = start_pos
        self.max_weight: float = max_weight
        self.current_load: float = 0.0
        self.inventory = Inventory(max_weight)  # si no existe ya
        self.delivered_jobs = []
        self.earned = 0.0  # ganancias acumuladas (usado en el resto del juego)
        self.total_earned = 0.0  # mantenido por compatibilidad histórica
        self.exhausted_lock: bool = False # Bloqueo por agotamiento
        self.weather = "clear"  # valor inicial por defecto
        self.reputation = 70  # valor inicial
        self.reputation_streak = 0  # para rachas sin penalización
        self.first_late_penalty_reduced = False  # control de tardanza reducida
        self.defeat_reason: Optional[str] = None  # motivo de derrota si ocurre
        self.mode_deliver = None
        self.prev = None
        self.last_pos: Optional[Tuple[int, int]] = None
        self.recent_positions: List[Tuple[int, int]] = []  # memoria corta anti-bucle
        self.city_map = city_map
        # Cache de ruta/objetivo para modo Difícil
        self._hard_target: Optional[Tuple[int, int]] = None
        self._hard_cached_path: Optional[List[Tuple[int, int]]] = None
        self._hard_path_idx: int = 0

        # Resistencia
        self.stamina_max: float = 100.0
        self.stamina: float = 100.0

    def can_carry(self, weight: float) -> bool:
        """Verifica si el pedido cabe en el inventario"""
        return self.inventory.can_add(Job(weight=weight, **{}))

    def pick_job(self, job: Job) -> bool:
        """Intenta aceptar un pedido"""
        # Solo puede tomar paquetes sin dueño o de la propia IA
        owner = getattr(job, "owner", None)
        if owner is not None and owner != "ia":
            return False
        # Marcar propietario y agregar al inventario
        job.owner = "ia"
        added = self.inventory.add_job(job)
        if added:
            self.current_load = self.inventory.total_weight()
        return added

    def deliver_job(self, job: Job) -> dict:
        """Entregar job: remover del inventario, agregar a entregados y sumar payout.
        Retorna un dict con el resultado y el payout aplicado.
        """
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

        # No sumar a total_earned aquí para evitar doble cuenta; usar self.earned
        removed = self.inventory.remove_job(job)
        if not removed:
            return {"success": False, "payout_applied": 0.0}

        self.delivered_jobs.append(job)
        payout = float(getattr(job, "payout", 0.0) or 0.0)
        # aplicar ajustes si hay reglas (por ejemplo penalizaciones o multiplicadores)
        self.earned += payout
        # mantener total_earned en sync (opcional)
        self.total_earned = self.earned
        return {"success": True, "payout_applied": payout}

    def move_ia(self, width, height, citymap, dx: int, dy: int, record_step: bool = True):
        """Mueve la IA en la dirección especificada si es posible.
        
        Args:
            width: Ancho del mapa
            height: Alto del mapa
            citymap: Instancia del mapa de la ciudad para verificar bloqueos
            dx: Desplazamiento en el eje x
            dy: Desplazamiento en el eje y
            record_step: Si es True, calcula la nueva posición desde la actual;
                        si es False, usa dx y dy como posición absoluta
        """
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
        """Mueve la IA a una posición específica y actualiza la resistencia.
        
        Args:
            position: Nueva posición (x, y) de la IA
        """
        prev = self.position
        # Memoriza la posición previa para evitar retrocesos inmediatos
        if prev is not None:
            self.last_pos = prev
            self.recent_positions.append(prev)
            # Mantener historial corto (últimas 12) para penalizar lazos
            if len(self.recent_positions) > 12:
                self.recent_positions = self.recent_positions[-12:]
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
        """Verifica si la IA puede moverse.
        
        Returns:
            bool: True si puede moverse, False si está exhausta
        """
        if self.exhausted_lock:
            return self.stamina >= 30.0
        return self.stamina > 0.0

    def get_speed_multiplier(self) -> float:
        """Obtiene el multiplicador de velocidad según el estado de resistencia.
        
        Returns:
            float: Multiplicador de velocidad (1.0 normal, 0.8 cansado, 0.0 exhausto)
        """
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
        """Verifica si la IA permanece en la misma posición.
        
        Args:
            previous_pos: Posición anterior a comparar
            
        Returns:
            bool: True si está en la misma posición, False si se movió
        """
        return self.position == previous_pos
    
    def trigger_defeat(self, reason: str) -> None:
        """Marca al courier como derrotado para que la vista maneje el final."""
        if self.defeat_reason is None:
            self.defeat_reason = reason

    def adjust_reputation(self, delta: int):
        """Ajusta la reputación de la IA dentro de los límites 0-100.
        
        Args:
            delta: Cantidad a sumar (positiva) o restar (negativa) a la reputación
        """
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
        
        Returns:
            bool: True si se pierde un pedido, False en caso contrario
        """
        r1,r2 = (random.randint(0,150),random.randint(0,150))
        if r1 == r2:
            return True
        return False
    
    
    def next_movement_ia(self,jobs):
        """
        Recibe los pedidos candidatos y retorna el proximo movimiento que va a hacer en la vista la ia
        
        Args:
            jobs: Lista de trabajos disponibles para la IA
            
        Returns:
            tuple: Tupla con (código de movimiento, coordenada objetivo)
        """
        # Incluir también los jobs que ya están en inventario para priorizar dropoffs
        try:
            inv_jobs = list(self.inventory.get_all())
        except Exception:
            inv_jobs = []
        all_jobs = list(jobs) + inv_jobs if jobs else inv_jobs

        options = (self.easy_mode(all_jobs),self.medium_mode(all_jobs),self.hard_mode(all_jobs)) # tupla con las opciones de recorrido
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
        
        Args:
            mode: Modo de búsqueda (1=Fácil, 2=Medio, 3=Difícil)
        """
        self.mode_deliver = mode
        return

    def easy_mode(self, jobs, city_map=None):
            """Modo fácil: movimiento semi-aleatorio con tendencia hacia objetivos.
            
            Args:
                jobs: Lista de trabajos disponibles
                city_map: Mapa de la ciudad (opcional)
                
            Returns:
                tuple: Siguiente posición (x, y) para la IA
            """
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
                    if self._is_valid_position(nx, ny) and (nx, ny) != self.last_pos:
                        return (nx, ny)

            # Movimiento aleatorio seguro
            directions = [(-1,0),(1,0),(0,-1),(0,1)]
            random.shuffle(directions)

            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if self._is_valid_position(nx, ny) and (nx, ny) != self.last_pos:
                    return (nx, ny)

            return (current_x, current_y)
        
    def _is_valid_position(self, x, y):
            """Verifica si (x,y) es transitable según CityMap (dentro de límites y no bloqueado).
        
            Args:
                x: Coordenada x
                y: Coordenada y
                
            Returns:
                bool: True si la posición es válida y transitable, False en caso contrario
            """
            if self.city_map is None:
                return False
            try:
                width = getattr(self.city_map, 'width', None)
                height = getattr(self.city_map, 'height', None)
                if width is None or height is None:
                    return False
                if not (0 <= x < width and 0 <= y < height):
                    return False
                # is_blocked debe devolver booleano; si no, usar bool() para normalizar
                blocked = self.city_map.is_blocked(x, y)
                return not bool(blocked)
            except Exception:
                return False
        

    def medium_mode(self, jobs):
        """
        Greedy avanzado:
        Se dirige al pickup o dropoff más cercano evitando edificios.
        Rodea obstáculos si la ruta directa está bloqueada.
        
        Args:
            jobs: Lista de trabajos disponibles
            
        Returns:
            tuple: Siguiente posición (x, y) para la IA
        """
        if not jobs:
            return self.easy_mode(jobs)

        cx, cy = self.position
        
        # 1) Seleccionar objetivo por prioridad (luego deadline, luego distancia)
        sel = self._select_best_target(jobs)
        if sel is None:
            return self.easy_mode(jobs)

        _, (tx, ty) = sel

        # 2) Si la celda objetivo está bloqueada, aproximar a la más cercana transitable
        if not self._is_valid_position(tx, ty):
            alt = self._closest_reachable_to(tx, ty, max_radius=6)
            if alt is not None:
                tx, ty = alt

        # 2) Generar candidatos ordenados por distancias, evitando retrocesos/loops
        candidates = []
        directions = [
            (cx + 1, cy),  # derecha
            (cx - 1, cy),  # izquierda
            (cx, cy + 1),  # abajo
            (cx, cy - 1),  # arriba
        ]

        recent = set(self.recent_positions[-6:])
        for nx, ny in directions:
            if self._is_valid_position(nx, ny):
                d = abs(nx - tx) + abs(ny - ty)
                penalty = 0.0
                if self.last_pos and (nx, ny) == self.last_pos:
                    penalty += 0.5
                if (nx, ny) in recent:
                    penalty += 1.0
                # Penalización adicional proporcional a visitas recientes
                try:
                    visit_count = sum(1 for p in self.recent_positions if p == (nx, ny))
                except Exception:
                    visit_count = 0
                if visit_count:
                    penalty += min(2.0, 0.3 * visit_count)
                candidates.append(((nx, ny), d, penalty))

        if not candidates:
            return self.easy_mode(jobs)

        # 3) Ordenar por reducción de distancia con penalización de bucle
        candidates.sort(key=lambda x: (x[1] + x[2], x[2], x[1]))

        return candidates[0][0]

            
            
    def hard_mode(self, jobs):
        """
        Hard Mode: A* pathfinding real.
        Rodea los edificios, evita loops y encuentra la ruta óptima.
        
        Args:
            jobs: Lista de trabajos disponibles
            
        Returns:
            tuple: Siguiente posición (x, y) para la IA
        """
        if not jobs:
            return self.easy_mode(jobs)

        # 1) Selección de objetivo estable
        sel = self._select_best_target(jobs)
        if not sel:
            return self.medium_mode(jobs)
        _, target = sel

        # Normalizar objetivo si está bloqueado
        tx, ty = target
        if not self._is_valid_position(tx, ty):
            adjusted = self._closest_reachable_to(tx, ty, max_radius=8)
            if adjusted is None:
                return self.medium_mode(jobs)
            target = adjusted

        # 2) Cachear y mantener ruta mientras el objetivo no cambie
        need_recalc = False
        if self._hard_target != target:
            need_recalc = True
        elif not self._hard_cached_path:
            need_recalc = True
        else:
            # si nuestra posición no coincide con el segmento actual, intentar resincronizar
            if self.position not in self._hard_cached_path:
                need_recalc = True
            else:
                # actualizar índice al punto actual
                try:
                    self._hard_path_idx = self._hard_cached_path.index(self.position)
                except ValueError:
                    need_recalc = True

        if need_recalc:
            path = self.astar(self.position, target)
            if not path or len(path) < 2:
                # fallo de planificación: recurrir a medio
                return self.medium_mode(jobs)
            self._hard_target = target
            self._hard_cached_path = path
            self._hard_path_idx = 0
        else:
            path = self._hard_cached_path

        # 3) Avanzar un paso en la ruta cacheada
        # asegurar índice en el nodo actual
        if self._hard_path_idx < len(path) and path[self._hard_path_idx] != self.position:
            try:
                self._hard_path_idx = path.index(self.position)
            except ValueError:
                # desincronizado, recalcular en próxima iteración
                return self.medium_mode(jobs)

        next_idx = self._hard_path_idx + 1
        if next_idx < len(path):
            return path[next_idx]

        # estamos en el objetivo; no hay siguiente paso
        return (self.position[0], self.position[1])

    def _get_target_for_job(self, job: Job) -> Optional[Tuple[int, int]]:
        """Obtiene la posición objetivo para un trabajo (pickup o dropoff).
        
        Args:
            job: Trabajo del cual obtener la posición objetivo
            
        Returns:
            Optional[Tuple[int, int]]: Posición objetivo o None si no está disponible
        """
        if job in self.inventory.get_all():
            return getattr(job, "dropoff_position", None) or getattr(job, "dropoff", None)
        return getattr(job, "pickup_position", None) or getattr(job, "pickup", None)

    def _select_best_target(self, jobs) -> Optional[Tuple[Job, Tuple[int, int]]]:
        """
        Selecciona (job, target) priorizando:
        1) mayor prioridad
        2) deadline más cercano
        3) menor distancia desde la posición actual
        Prefiere objetivos válidos (con coordenadas)
        Args:
            jobs: Lista de trabajos disponibles
            
        Returns:
            Optional[Tuple[Job, Tuple[int, int]]]: Tupla con trabajo y posición objetivo, o None
        """
        if not jobs:
            return None
        cx, cy = self.position
        best = None
        best_key = None
        for job in jobs:
            target = self._get_target_for_job(job)
            if not target:
                continue
            tx, ty = target
            prio = getattr(job, "priority", 0)
            deadline_ts = job.get_deadline_timestamp() if hasattr(job, "get_deadline_timestamp") else None
            if deadline_ts is None:
                deadline_ts = float("inf")
            dist = abs(cx - tx) + abs(cy - ty)
            key = (-int(prio), float(deadline_ts), int(dist))
            if best_key is None or key < best_key:
                best_key = key
                best = (job, (tx, ty))
        return best

    def _closest_reachable_to(self, tx: int, ty: int, max_radius: int = 6) -> Optional[Tuple[int, int]]:
        """
        Busca una celda transitable cercana a (tx, ty). Explora anillos crecientes hasta max_radius
        y selecciona la más cercana al objetivo (y luego al agente) para minimizar bucles.
        """
        if self._is_valid_position(tx, ty):
            return (tx, ty)

        cx, cy = self.position
        best: Optional[Tuple[int, int]] = None
        best_key = (float('inf'), float('inf'))

        for r in range(1, max_radius + 1):
            # recorrer el contorno manhattan de radio r
            for dx in range(-r, r + 1):
                dy_candidates = [r - abs(dx), -(r - abs(dx))]
                for dy in dy_candidates:
                    nx, ny = tx + dx, ty + dy
                    if self._is_valid_position(nx, ny):
                        key = (abs(nx - tx) + abs(ny - ty), abs(nx - cx) + abs(ny - cy))
                        if key < best_key:
                            best_key = key
                            best = (nx, ny)
            if best is not None:
                return best

        return None
    
    def _neighbors(self, node):
        """Obtiene los vecinos transitables de un nodo.
        
        Args:
            node: Tupla (x, y) representando el nodo actual
            
        Returns:
            List[Tuple[int, int]]: Lista de posiciones vecinas transitables
        """
        x, y = node
        candidates = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        return [(nx,ny) for nx,ny in candidates if self._is_valid_position(nx,ny)]
    
    def astar(self, start, goal, max_nodes=8000):
        """Algoritmo A* para encontrar el camino más corto entre dos puntos.
        
        Args:
            start: Posición inicial (x, y)
            goal: Posición objetivo (x, y)
            max_nodes: Número máximo de nodos a procesar
            
        Returns:
            Optional[List[Tuple[int, int]]]: Camino desde start hasta goal, o None si no se encuentra"""
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

        # Mapeo correcto: 0=LEFT,1=RIGHT,2=UP,3=DOWN
        if self.position[1] > oy:
            return 2  # UP
        if self.position[1] < oy:
            return 3  # DOWN
        if self.position[0] > ox:
            return 0  # LEFT
        if self.position[0] < ox:
            return 1  # RIGHT

        # Si ya estamos en la misma celda
        return None
