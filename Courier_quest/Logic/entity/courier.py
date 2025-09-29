# src/models/courier.py

from typing import Tuple, List
from Logic.entity.job import Job
from Logic.entity.inventory import Inventory
from Logic.entity.city_map import CityMap


class Courier:
    """
    Representa al repartidor:
      - posición en el mapa
      - stamina, reputación, cargas
      - inventario y entregas
    """

    def __init__(
        self,
        start_pos: Tuple[int, int],
        max_weight: float,
    ):
        self.position: Tuple[int, int] = start_pos
        self.max_weight: float = max_weight
        self.current_load: float = 0.0
        self.inventory: Inventory = Inventory(max_weight)
        self.delivered_jobs: List[Job] = []

    def can_carry(self, weight: float) -> bool:
        """
        retorna si el peso del pedido nosobrepasa la carga maxima
        """
        return self.inventory.can_add(Job(weight=weight, **{}))

    def pick_job(self, job: Job) -> bool:
        """
        Intenta aceptar un pedido:
        - Si cabe en el inventario, lo añade y actualiza carga.
        """
        added = self.inventory.add_job(job)
        if added:
            self.current_load = self.inventory.total_weight()
        return added

    def deliver_job(self, job: Job) -> bool:
        """
        Intenta entregar un pedido:
        - Si estaba en inventory, lo remueve y pasa a delivered_jobs.
        """
        removed = self.inventory.remove_job(job)
        if removed:
            self.delivered_jobs.append(job)
            self.current_load = self.inventory.total_weight()
        return removed
    
    def move_courier(self,width,height,citymap, dx: int, dy: int):
        x, y = self.position
        nx, ny = x + dx, y + dy
        cmap = citymap
        if (0 <= nx < width and 0 <= ny < height and not cmap.is_blocked(nx, ny)):
            self.move_to((nx, ny))

    def move_to(self, position: Tuple[int, int]) -> None:
        """
        Actualiza la posición del repartidor.
        Se puede conectar aquí lógica de stamina, clima, etc.
        """
        self.position = position

   