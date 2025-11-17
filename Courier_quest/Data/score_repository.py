import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ScoreRepository:
    """Persistencia simple de puntajes en un archivo JSON."""

    def __init__(self, storage_path: Path | str | None = None) -> None:
        """Inicializa el repositorio de puntajes con la ruta de almacenamiento.
        
        Args:
            storage_path: Ruta al archivo JSON para almacenar los puntajes. 
                        Si es None, usa "scores.json" por defecto.
        """
        self.storage_path = Path(storage_path or "scores.json")

    # ------------------------------------------------------------------
    def append(self, record: Dict[str, Any]) -> None:
        """Agrega un nuevo puntaje y mantiene la lista ordenada."""
        data = self._load_all()
        if "player_name" not in record:
            record["player_name"] = None
        data.append(record)
        data.sort(key=lambda item: float(item.get("total_points", 0.0)), reverse=True)
        self._write_all(data)

    def top(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Devuelve los primeros N puntajes almacenados."""
        data = self._load_all()
        return data[: max(0, limit)]

    # ------------------------------------------------------------------
    def _load_all(self) -> List[Dict[str, Any]]:
        """Carga todos los puntajes desde el archivo de almacenamiento.
        
        Returns:
            List[Dict[str, Any]]: Lista de registros de puntajes. 
            Retorna lista vacía si el archivo no existe o hay error de lectura.
        """
        if not self.storage_path.exists():
            return []
        try:
            with self.storage_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, list):
                return data
        except Exception:
            pass
        return []

    def _write_all(self, data: List[Dict[str, Any]]) -> None:
        """Escribe todos los puntajes al archivo de almacenamiento.
        
        Args:
            data: Lista de registros de puntajes a escribir
        """
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=True, indent=2)
