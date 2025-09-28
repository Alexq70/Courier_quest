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
    
    def detectar_bloques(self):
        visited = [[False] * self.width for _ in range(self.height)]  # matriz de visitados
        bloques = []  # lista de bloques detectados

        for y in range(self.height):  # recorrer filas
            for x in range(self.width):  # recorrer columnas
                if self.tiles[y][x] == "B" and not visited[y][x]:  # Encontrar un nuevo bloque
                # Expandir hacia la derecha y abajo para encontrar el tamaño del bloque
                    w = 1
                # Expandir ancho
                    while (x + w < self.width and 
                       self.tiles[y][x + w] == "B" and 
                       not visited[y][x + w]):
                       w += 1
                
                # Expandir alto
                    h = 1
                    expand = True
                    while expand and y + h < self.height:
                    # Verificar que toda la fila sea "B" y no visitada
                        for i in range(w):
                            if (self.tiles[y + h][x + i] != "B" or 
                                visited[y + h][x + i]):
                                expand = False
                                break
                        if expand:
                            h += 1
                
                # Marcar todas las celdas del bloque como visitadas
                    for yy in range(y, y + h):
                        for xx in range(x, x + w):
                            visited[yy][xx] = True
                
                # Agregar bloque a la lista
                    bloques.append({
                        'x': x, 
                        'y': y, 
                        'width': w, 
                        'height': h,
                    })
    
        return bloques