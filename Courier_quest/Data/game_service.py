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
           self.last_job = self.job_example

    def job_most_nearly(self, curr_position):
       """
       Busca el job más cercano a la posición del jugador.
       - Si está en el mapa: compara distancia al pickup.
       - Si está en el inventario: compara distancia al dropoff.
        """
       # juntar jobs en el mapa + en el inventario
       candidates = list(self.jobs) + list(self.courier.inventory.items)
       if not candidates:
           return None

       nearest: Job = None
       min_dist = float("inf")

       for job in candidates:
            if job in self.courier.inventory.items:
               d = self.distance(job.dropoff, curr_position)
            else:
               d = self.distance(job.pickup, curr_position)

            if d <= 5 and d < min_dist:
               nearest = job
               min_dist = d

       return nearest

    def distance(self,a, b):
      return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


    
    def get_last_job(self):
        """"
        Devuelve el último trabajo recogido o tomado del mapa.
        """
        return self.last_job
    
    def set_last_job(self,job):
        """
        Establece el último trabajo recogido o tomado del mapa.
        """
        self.last_job = job
    
