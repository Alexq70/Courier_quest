# src/engine/pathfinder.py

import heapq
from typing import Dict, List, Optional, Tuple

from entity.city_map import CityMap


class PathFinder:
    """
    Calcula rutas óptimas en un CityMap usando A* con heurística Manhattan
    y costos de superficie.
    """

    def __init__(self, city_map: CityMap):
        self.city_map = city_map

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Devuelve la lista de coordenadas (x, y) del camino más corto
        desde 'start' hasta 'goal'. Si no hay ruta, devuelve lista vacía.
        """
        open_set: List[Tuple[float, Tuple[int, int]]] = []
        heapq.heappush(open_set, (0.0, start))

        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {
            start: None
        }
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}

        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            # Distancia Manhattan
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            x, y = current
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                neighbor = (x + dx, y + dy)
                nx, ny = neighbor

                # Verificar dentro de límites
                if not (0 <= nx < self.city_map.width and
                        0 <= ny < self.city_map.height):
                    continue

                # Saltar bloqueados
                if self.city_map.is_blocked(nx, ny):
                    continue

                # Coste de movimiento
                tentative_g = (
                    g_score[current]
                    + self.city_map.get_surface_weight(nx, ny)
                )

                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))

        # No existe ruta
        return []

    def _reconstruct_path(
        self,
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
        current: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Reconstruye el camino a partir de 'came_from' desde el goal.
        """
        path: List[Tuple[int, int]] = [current]
        while came_from[current] is not None:
            current = came_from[current]  # type: ignore
            path.append(current)
        path.reverse()
        return path