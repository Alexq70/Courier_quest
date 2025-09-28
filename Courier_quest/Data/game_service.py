import math
from Logic.entity.job import Job
from Logic.entity.weather_burst import WeatherBurst 
from Logic.entity.city_map import CityMap
from Logic.entity.courier import Courier

class GameService:

    job_example = Job( id = 1, pickup=(0, 0), dropoff=(0, 0), payout=100, deadline=60, weight=10, priority=1, release_time=0)
    def __init__(self,jobs : Job ,weather : WeatherBurst ,map : CityMap ,courier : Courier):
           self.jobs = jobs
           self.weather = weather
           self.map = map
           self.courier = courier
           self.last_picked = self.job_example

    def job_most_nearly(self, curr_position):
      """
      Busca el job más cercano a la posición del jugador.
      """
      if not self.jobs:
        return None  # Si la lista está vacía

      nearest: Job = None
      min_dist = float("inf")

      for job in self.jobs:
          d = self.distance(job.pickup, curr_position)
          if d <= 5 and d < min_dist:  # 🔥 dentro del rango y más cercano
             nearest = job
             min_dist = d

      return nearest

    def distance(self,a, b):
      """Distancia euclidiana entre dos puntos (x1, y1) y (x2, y2).
      """
      return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


    
    def get_last_picked(self):
        """"
        Devuelve el último trabajo recogido.
        """
        return self.last_picked
    
    def set_last_picked(self,job):
        """
        Establece el último trabajo recogido.
        """
        self.last_picked = job

    def sort_jobs_by_priority(self):
        """Ordena la lista de trabajos por prioridad (mayor prioridad primero)."""
        self.courier.inventory.items.sort(key=lambda job: job.priority, reverse=True)

    def sort_jobs_by_deadline(self):
        """Ordena la lista de trabajos por fecha límite (más cercana primero)."""
        self.courier.inventory.items.sort(key=lambda job: job.deadline)

    
