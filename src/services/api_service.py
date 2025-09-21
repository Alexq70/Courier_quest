import requests
import json
from pathlib import Path


class APIService:
    """
    Servicio para llamar a la API y cachear respuestas.
    """

    BASE_URL = (
        "https://tigerds-api.kindflower-ccaf48b6."
        "eastus.azurecontainerapps.io"
    )

    def fetch(self, endpoint: str) -> dict:
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
        safe_name = endpoint.replace("/", "_") + ".json"
        path = Path("api_cache") / safe_name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _load_cache(self, endpoint: str) -> dict:
        safe_name = endpoint.replace("/", "_") + ".json"
        path = Path("api_cache") / safe_name
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)