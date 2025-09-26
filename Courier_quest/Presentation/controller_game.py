from Data.api_service import APIService
from Logic.entity.city_map import CityMap
from Logic.entity.job import Job
from Logic.entity.weather_burst import WeatherBurst
from Logic.entity.courier import Courier


class controller_game:
    """
    Motor del juego: carga mapa, pedidos, clima (stub) e inicializa Courier.
    """

    def __init__(self):
        self.api = APIService()
        self.city_map = None
        self.jobs = []
        self.weather = []
        self.courier = None

    def _deep_unwrap(self, resp: dict) -> dict:
        """
        Elimina niveles anidados de 'data' hasta el dict interno.
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

        # 3) Clima (stub)
        print("Cargando clima (stub)…")
        weather_resp = self.api.fetch("city/weather")
        raw = weather_resp.get("data", {}) if isinstance(weather_resp, dict) else {}
        bursts = raw.get("bursts", [])
        if not isinstance(bursts, list):
            bursts = []
        print(f"Ráfagas climáticas (stub): {len(bursts)}")
        self.weather = [WeatherBurst(**w) for w in bursts]

        # 4) Courier
        self.courier = Courier(start_pos=(0, 0), max_weight=10)
        print(f"Courier inicializado en {self.courier.position}")

    def start(self):
        """
        Arranca la carga del mundo y ejecuta el juego.
        """
        self.load_world()
        print("Juego iniciado correctamente.")