# src/models/inventory.py

from typing import List, Optional
from models.job import Job


class Inventory:
    """
    Almacena pedidos aceptados y controla
    capacidad máxima de carga.
    """

    def __init__(self, max_weight: float):
        self.max_weight: float = max_weight
        self.items: List[Job] = []

    def total_weight(self) -> float:
        return sum(job.weight for job in self.items)

    def can_add(self, job: Job) -> bool:
        return self.total_weight() + job.weight <= self.max_weight

    def add_job(self, job: Job) -> bool:
        if self.can_add(job):
            self.items.append(job)
            return True
        return False

    def remove_job(self, job_id: str) -> bool:
        """
        Elimina el pedido con id == job_id.
        Devuelve True si se borró, False si no existía.
        """
        for job in self.items:
            if job.id == job_id:
                self.items.remove(job)
                return True
        return False

    def reorder(self, key_func) -> None:
        """
        Reordena self.items según la función key_func.
        Ejemplo: key=lambda j: (-j.priority, j.deadline)
        """
        self.items.sort(key=key_func)