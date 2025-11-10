from Data.api_service import APIService
from Data.game_service import GameService
from Logic.entity.city_map import CityMap
from Logic.entity.job import Job
from Logic.entity.weather_burst import WeatherBurst
from Logic.entity.courier import Courier
from Logic.entity.ia import Ia

from Logic.weather_simulator import WeatherSimulator  
from Logic.score_manager import ScoreManager
import time
import json

class controller_game:
    """
    Motor del juego: carga mapa, pedidos, clima dinámico e inicializa Courier.
    """

    def __init__(self):
        self.ruta = ("C:/Users/ALEXQUESADABERMUDEZ/Documents/GitHub/Courier_quest/api_cache/city_jobs.json")
        self.api = APIService()
        self.game_service = None
        self.city_map = None
        self.jobs = []
        self.weather = []
        self.courier = None
        self.ia = None
        self.weather_simulator = None  # Nuevo atributo
        self.last_weather_update = 0
        self.weather_update_interval = 0.1  # Actualizar clima cada 100ms
        self.score_manager = ScoreManager()
        
    def _deep_unwrap(self, resp: dict) -> dict:
        """
        Retorna la informacion mas profunda del diccionario
        """
        current = resp
        while (
            isinstance(current, dict)
            and "data" in current
            and isinstance(current["data"], dict)
        ):
            current = current["data"]
        return current

    def _find_list_of_dicts(self, obj):
        """
        Busca la primera lista cuyos elementos sean dicts.
        """
        if isinstance(obj, dict):
            for v in obj.values():
                found = self._find_list_of_dicts(v)
                if found:
                    return found
        elif isinstance(obj, list):
            if obj and all(isinstance(i, dict) for i in obj):
                return obj
            for i in obj:
                found = self._find_list_of_dicts(i)
                if found:
                    return found
        return None
    
    def job_nearly(self):
        return self.game_service.job_most_nearly(self.courier.position)
    
    def job_nearly_ia(self):
            return self.game_service.job_most_nearly_ia(self.ia.position)
    
    def set_last_job(self, job):
        self.game_service.set_last_job(job)
        
    def get_last_job(self):
        return self.game_service.get_last_job()
    
    def set_last_job_ia(self, job):
        self.game_service.set_last_job(job)
    
    def get_last_job_ia(self):
          return self.game_service.get_last_job_ia()
        

    def load_world(self):
        # 1) Mapa
        print("Cargando mapa...")
        map_resp = self.api.fetch("city/map")
        raw_map = self._deep_unwrap(map_resp)
        self.city_map = CityMap(
            width=raw_map["width"],
            height=raw_map["height"],
            tiles=raw_map["tiles"],
            legend=raw_map["legend"],
            goal=raw_map["goal"],
        )
        print(f"Mapa cargado: {self.city_map.width}x{self.city_map.height}")
        
          # 2) Pedidos
        print("Cargando pedidos...")
        jobs_resp = self.api.fetch("city/jobs")
        raw_jobs = self._deep_unwrap(jobs_resp)
        raw_jobs = self._find_list_of_dicts(raw_jobs)
        if raw_jobs is None:
            raise RuntimeError("city/jobs no contiene lista de pedidos")
        print(f"Pedidos cargados: {len(raw_jobs)}")
        self.jobs = [Job(**d) for d in raw_jobs]


        # 3) Clima DINÁMICO - CORREGIDO
        print("Inicializando simulador de clima dinámico...")
        weather_resp = self.api.fetch("city/weather")
        raw_weather = self._deep_unwrap(weather_resp)
        
        # Crear el simulador de clima (nombre corregido)
        self.weather_simulator = WeatherSimulator(raw_weather)
        self.last_weather_update = time.time()
        
        # Generar bursts iniciales para compatibilidad
        self.weather = self._generate_initial_bursts()
        print(f"Clima dinámico inicializado: {self.weather_simulator.current_condition}")

        # 4) Courier
        self.courier = Courier(start_pos=(0, 0), max_weight=10)
        self.ia = Ia(start_pos=(0, 0), max_weight=10,city_map=self.city_map)
        print(f"Courier inicializado{self.courier.position}  e IA inicializada {self.ia.position}.")

    def _generate_initial_bursts(self):
        """Genera bursts iniciales para compatibilidad con código existente"""
        bursts = []
        # Crear algunos bursts iniciales basados en el clima actual
        for i in range(5):
            burst_data = {
                "hour": i,
                "condition": self.weather_simulator.current_condition,
                "intensity": self.weather_simulator.current_intensity,
                "city": self.weather_simulator.config["city"]
            }
            bursts.append(WeatherBurst(**burst_data))
        return bursts

    def start(self):
        """Arranca la carga del mundo y ejecuta el juego."""
        self.load_world()
        self.game_service = GameService(self.jobs, self.weather, self.city_map, self.courier , self.ia)
        print("Juego iniciado correctamente.")

    def update(self):
        """Mtodo principal de actualizacin del juego (llamar en cada frame)."""
        current_time = time.time()

        if len(self.jobs) <= 0 and len(self.courier.inventory.get_all()) <= 0:
            self.refresh_jobs()

        if current_time - self.last_weather_update >= self.weather_update_interval:
            self._update_weather()
            self.last_weather_update = current_time
            self.courier.weather = self.weather_simulator.current_condition

    def _update_weather(self):
        """Actualiza el estado del clima."""
        if not self.weather_simulator:
            return
        self.weather_simulator.update()

    def get_current_weather_info(self):
        """Obtiene informacin del clima actual para la vista."""
        if self.weather_simulator:
            return self.weather_simulator.get_weather_info()
        return {}

    def move_courier(self, dx, dy, record_step=True):
        self.courier.move_courier(self.city_map.width, self.city_map.height, self.city_map, dx, dy, record_step)
        
    def move_ia(self, dx, dy, record_step=True):
        self.ia.move_ia(self.city_map.width, self.city_map.height, self.city_map, dx, dy, record_step)

    def new_jobs(self):
        """Genera pedidos nuevos y actualiza la lista principal."""
        print("Cargando pedidos...")
        jobs_resp = self.api.fetch("city/jobs")
        raw_jobs = self._deep_unwrap(jobs_resp)
        raw_jobs = self._find_list_of_dicts(raw_jobs)
        if raw_jobs is None:
            raise RuntimeError("city/jobs no contiene lista de pedidos")
        print(f"Pedidos cargados: {len(raw_jobs)}")
        self.jobs = [Job(**d) for d in raw_jobs]
        if self.game_service:
            self.game_service.set_jobs(self.jobs)

    def refresh_jobs(self):
        """Carga una nueva lista de pedidos en la lista principal."""
        self.new_jobs()

    def get_steps(self):
        return self.game_service.get_steps()

    def include_step(self, pos):
        self.game_service.include_new_step(pos)