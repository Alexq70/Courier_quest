from collections import deque
import math
import time
from typing import Iterable, Tuple

from Logic.entity.job import Job
from Logic.entity.weather_burst import WeatherBurst
from Logic.entity.city_map import CityMap
from Logic.entity.courier import Courier
from Logic.entity.ia import Ia


class GameService:
    """Gestiona estado compartido del mundo de juego y ayuda con consultas comunes."""

    job_example = Job(
        id=1,
        pickup=(0, 0),
        dropoff=(0, 0),
        payout=100,
        deadline=60,
        weight=10,
        priority=1,
        release_time=0,
    )

    def __init__(self, jobs: Iterable[Job], weather: Iterable[WeatherBurst], map: CityMap, courier: Courier, ia : Ia):
        
        """Inicializa el servicio del juego con los componentes principales.
        
        Args:
            jobs: Iterable de trabajos disponibles en el juego
            weather: Iterable de eventos climáticos
            map: Mapa de la ciudad
            courier: Entidad del mensajero/jugador
            ia: Entidad de inteligencia artificial
        """
        self.session_start = time.time()
        self.jobs = jobs
        self.weather = weather
        self.map = map
        self.courier = courier
        self.ia = ia
        self.last_job = self.job_example
        self.last_job_ia = self.job_example
        self._bind_jobs_to_session(self.jobs)
        if hasattr(self.job_example, "bind_session_start"):
            self.job_example.bind_session_start(self.session_start)
        self.pila = deque()

    def _bind_jobs_to_session(self, jobs_iterable: Iterable[Job]) -> None:
        
        """Vincula los trabajos al tiempo de inicio de la sesión actual.
        
        Args:
            jobs_iterable: Iterable de trabajos a vincular
        """
        for job in jobs_iterable:
            if hasattr(job, "bind_session_start"):
                job.bind_session_start(self.session_start)

    def job_most_nearly(self, curr_position):
        """Busca el job mas cercano a la posicion del jugador.
        Considera solo jobs del mapa sin dueño y los del inventario del jugador."""
        jobs_on_map = [j for j in self.jobs if getattr(j, "owner", None) in (None, "player")]
        candidates = jobs_on_map + list(self.courier.inventory.get_all())
        if not candidates:
            return None

        nearest: Job | None = None
        min_dist = float("inf")

        for job in candidates:
            if job in self.courier.inventory.get_all():
                dist = self.distance(job.dropoff, curr_position)
            else:
                dist = self.distance(job.pickup, curr_position)

            if dist <= 5 and dist < min_dist:
                nearest = job
                min_dist = dist

        return nearest

    def distance(self, a, b):
        """Calcula la distancia euclidiana entre dos puntos.
        
        Args:
            a: Tupla (x, y) representando el primer punto
            b: Tupla (x, y) representando el segundo punto
            
        Returns:
            float: Distancia euclidiana entre los puntos a y b
        """
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def get_last_job(self):
        """Devuelve el ultimo trabajo tomado."""
        return self.last_job

    def set_last_job(self, job):
        """Actualiza el ultimo trabajo tomado."""
        self.last_job = job

    def set_jobs(self, jobs: Iterable[Job]) -> None:
        """Establece la lista de trabajos disponibles y los vincula a la sesión.
        
        Args:
            jobs: Iterable de trabajos a establecer
        """
        self.jobs = jobs
        self._bind_jobs_to_session(self.jobs)
    
    def get_steps(self):
        """Obtiene el siguiente paso de la pila de movimientos.
        
        Returns:
            tuple: Coordenadas (x, y) del siguiente paso, o (0, 0) si la pila está vacía
        """
        if self.pila: 
            return self.pila.pop()
        return (0, 0)
    
    def include_new_step(self,pos):
        """Agrega un nuevo paso a la pila de movimientos.
        
        Args:
            pos: Tupla (x, y) representando la posición a agregar
        """
        self.pila.append(pos)
    
    def has_steps(self):
        """Verifica si hay pasos pendientes en la pila.
        
        Returns:
            bool: True si hay pasos pendientes, False en caso contrario
        """
        return len(self.pila) > 0
    
    def next_job_ia(self):
        """Obtiene el próximo trabajo para la IA.
        
        Returns:
            Job | None: Próximo trabajo para la IA o None si no hay
        """
        return 
    
    #---------------------- IA LOGIC -------------------------------
    def job_most_nearly_ia(self, ia_position):
        """Selecciona el job cercano (<=5) priorizando prioridad; empates por distancia.
        Prefiere entregar (inventario) sobre recoger si todo lo demás empata.
        Considera solo jobs del mapa sin dueño o asignados a IA."""
        jobs_on_map = [j for j in self.jobs if getattr(j, "owner", None) in (None, "ia")]
        candidates = jobs_on_map + list(self.ia.inventory.get_all())
        if not candidates:
            return None

        best = None
        best_key = None
        inv_jobs = set(self.ia.inventory.get_all())

        for job in candidates:
            if job in inv_jobs:
                target = job.dropoff
                is_inv = 0  # preferir entregar sobre recoger
            else:
                target = job.pickup
                is_inv = 1

            dist = self.distance(target, ia_position)
            if dist > 5:
                continue
            prio = getattr(job, "priority", 0)
            key = (-int(prio), float(dist), is_inv)
            if best_key is None or key < best_key:
                best_key = key
                best = job

        return best

    
    def _next_movement_ia(self):
        """Calcula el próximo movimiento de la IA.
        
        Returns:
            tuple: Próxima posición (x, y) para la IA
        """
        return self.ia.next_movement_ia()
    
    def get_last_job_ia(self):
        """Devuelve el ultimo trabajo tomado de la IA."""
        return self.last_job_ia

    def set_last_job_ia(self, job):
        """Actualiza el ultimo trabajo tomado de la IA."""
        self.last_job_ia = job
        