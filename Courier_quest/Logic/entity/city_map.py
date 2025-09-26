from typing import Any, Dict, List


class CityMap:
    """
    Representa el mapa de la ciudad con sus tiles,
    leyenda y objetivo de puntaje o posición de meta.
    """

    def __init__(
        self,
        width: int,
        height: int,
        tiles: List[List[str]],
        legend: Dict[str, Dict[str, Any]],
        goal: Any,
    ):
        self.width = width
        self.height = height
        self.tiles = tiles
        self.legend = legend
        self.goal = goal

    def is_blocked(self, x: int, y: int) -> bool:
        """
        Devuelve True si la posición (x, y) está bloqueada.
        """
        key = self.tiles[y][x]
        return self.legend[key].get("blocked", False)

    def get_surface_weight(self, x: int, y: int) -> float:
        """
        Devuelve el peso de superficie para calcular costos de paso.
        """
        key = self.tiles[y][x]
        return self.legend[key].get("surface_weight", 1.0)