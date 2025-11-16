import requests
import json
from pathlib import Path


class APIService:
    """
    Servicio para interactuar con la API del juego Courier Quest y manejar cache.
    
    Esta clase proporciona métodos para realizar peticiones HTTP a la API del juego
    y almacenar en cache las respuestas para uso offline o en caso de fallos de conexión.
    
    Attributes:
        BASE_URL (str): URL base de la API del juego Courier Quest.
    """

    BASE_URL = (
        "https://tigerds-api.kindflower-ccaf48b6."
        "eastus.azurecontainerapps.io"
    )

    def fetch(self, endpoint: str) -> dict:
        """
        Obtiene datos de un endpoint de la API, con fallback a cache si falla la petición.
        
        Intenta hacer una petición HTTP GET al endpoint especificado. Si la petición
        es exitosa, guarda la respuesta en cache y la retorna. Si falla, carga la
        versión en cache más reciente.
        
        Args:
            endpoint (str): Endpoint de la API a consultar (ej: 'city', 'weather')
            
        Returns:
            dict: Datos JSON de la respuesta de la API o del archivo de cache.
            
        Example:
            >>> api = APIService()
            >>> city_data = api.fetch('city')
            >>> weather_data = api.fetch('weather')
        """
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            self._save_cache(endpoint, data)
            return data
        except Exception:
            return self._load_cache(endpoint)

    def _save_cache(self, endpoint: str, data: dict) -> None:
        """
        Guarda los datos de la API en un archivo JSON local para cache.
        
        Args:
            endpoint (str): Endpoint de la API usado para generar el nombre del archivo.
            data (dict): Datos JSON a guardar en cache.
            
        Note:
            Los archivos se guardan en la carpeta 'api_cache/' con nombres seguros.
        """
        safe_name = endpoint.replace("/", "_") + ".json"
        path = Path("api_cache") / safe_name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _load_cache(self, endpoint: str) -> dict:
        """
        Carga datos desde el archivo de cache local.
        
        Args:
            endpoint (str): Endpoint de la API para identificar el archivo de cache.
            
        Returns:
            dict: Datos JSON cargados desde el archivo de cache.
            
        Raises:
            FileNotFoundError: Si no existe un archivo de cache para el endpoint.
            JSONDecodeError: Si el archivo de cache está corrupto o mal formado.
        """
        safe_name = endpoint.replace("/", "_") + ".json"
        path = Path("api_cache") / safe_name
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)