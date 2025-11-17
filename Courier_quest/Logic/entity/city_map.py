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
        # Normalizar siempre a booleano; si no hay 'blocked' en la leyenda, se asume transitable
        if key == 'D':
            # Si en algún mapa aparece 'D' (punto de entrega/edificio), tratarlo como bloqueado
            return True
        return bool(self.legend.get(key, {}).get("blocked", False))

    def get_surface_weight(self, x: int, y: int) -> float:
        """
        Devuelve el peso de superficie para calcular costos de paso.
        """
        key = self.tiles[y][x]
        return self.legend[key].get("surface_weight", 1.0)
    
    def detectar_bloques(self):
      visited = [[False] * self.width for _ in range(self.height)] 
      bloques = []  

      for y in range(self.height): 
        for x in range(self.width):  
            if (self.tiles[y][x] == "B" or self.tiles[y][x] == "D") and not visited[y][x]:
                w = 1
                while (x + w < self.width and 
                   (self.tiles[y][x + w] == "B" or self.tiles[y][x + w] == "D") and 
                   not visited[y][x + w]):
                   w += 1
                
                h = 1
                expand = True
                while expand and y + h < self.height:
                    for i in range(w):
                        if ((self.tiles[y + h][x + i] != "B" and self.tiles[y + h][x + i] != "D") or 
                            visited[y + h][x + i]):
                            expand = False
                            break
                    if expand:
                        h += 1
                
                for yy in range(y, y + h):
                    for xx in range(x, x + w):
                        visited[yy][xx] = True
                
                bloques.append({
                    'x': x, 
                    'y': y, 
                    'width': w, 
                    'height': h,
                })
    
      return bloques