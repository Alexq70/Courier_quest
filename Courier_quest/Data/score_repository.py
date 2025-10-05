import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ScoreRepository:
    """Persistencia simple de puntajes en un archivo JSON."""

    def __init__(self, storage_path: Path | str | None = None) -> None:
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
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=True, indent=2)
