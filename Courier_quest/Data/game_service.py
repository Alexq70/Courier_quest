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
        for job in jobs_iterable:
            if hasattr(job, "bind_session_start"):
                job.bind_session_start(self.session_start)

    def job_most_nearly(self, curr_position):
        """Busca el job mas cercano a la posicion del jugador."""
        candidates = list(self.jobs) + list(self.courier.inventory.get_all())
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
        """
        Calcula el pedido mas cercano
        """
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def get_last_job(self):
        """Devuelve el ultimo trabajo tomado."""
        return self.last_job

    def set_last_job(self, job):
        """Actualiza el ultimo trabajo tomado."""
        self.last_job = job

    def set_jobs(self, jobs: Iterable[Job]) -> None:
        self.jobs = jobs
        self._bind_jobs_to_session(self.jobs)
    
    def get_steps(self):
        if self.pila: 
            return self.pila.pop()
        return (0, 0)
    
    def include_new_step(self,pos):
        self.pila.append(pos)
    
    def has_steps(self):
        return len(self.pila) > 0
    
    def next_job_ia(self):
        return 
    
    #---------------------- IA LOGIC -------------------------------
    def job_most_nearly_ia(self, ia_position):
        """Busca el job más cercano a la IA con distancia máxima 5."""
        candidates = list(self.jobs) + list(self.ia.inventory.get_all())
        if not candidates:
            return None

        nearest = None
        min_dist = float("inf")

        for job in candidates:
            # Si el job está en inventario → ir al dropoff
            if job in self.ia.inventory.get_all():
                dist = self.distance(job.dropoff, ia_position)
            else:
                dist = self.distance(job.pickup, ia_position)

            # Debe estar relativamente cerca para evitar IA perdida
            if dist <= 5 and dist < min_dist:
                min_dist = dist
                nearest = job

        return nearest

    
    def _next_movement_ia(self):
        return self.ia.next_movement_ia()
    
    def get_last_job_ia(self):
        """Devuelve el ultimo trabajo tomado de la IA."""
        return self.last_job_ia

    def set_last_job_ia(self, job):
        """Actualiza el ultimo trabajo tomado de la IA."""
        self.last_job_ia = job
        