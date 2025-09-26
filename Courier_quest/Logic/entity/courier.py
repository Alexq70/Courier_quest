# src/models/courier.py

from typing import Tuple, List
from Logic.entity.job import Job
from Logic.entity.inventory import Inventory


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
        removed = self.inventory.remove_job(job.id)
        if removed:
            self.delivered_jobs.append(job)
            self.current_load = self.inventory.total_weight()
        return removed

    def move_to(self, position: Tuple[int, int]) -> None:
        """
        Actualiza la posición del repartidor.
        Se puede conectar aquí lógica de stamina, clima, etc.
        """
        self.position = position