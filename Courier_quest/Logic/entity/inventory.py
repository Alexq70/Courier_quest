# src/models/inventory.py

from typing import List, Optional
import heapq
from Logic.entity.job import Job


class Inventory:
    """
    Almacena pedidos aceptados y controla
    capacidad máxima de carga.
    """
    def __init__(self, max_weight: float):
        self.max_weight: float = max_weight
        self.items: List[Job] = []
        self._heap = []  # heap de prioridad para los jobs

    def total_weight(self) -> float:
        return sum(job.weight for job in self.items)

    def can_add(self, job: Job) -> bool:
        return self.total_weight() + job.weight <= self.max_weight

    def add_job(self, job: Job) -> bool:
        if self.can_add(job):
            self.items.append(job)
            # insertamos en el heap con prioridad por defecto (priority > deadline)
            heapq.heappush(self._heap, (-job.priority, job.deadline, job))
            return True
        return False

    def remove_job(self, job: Job) -> bool:
        """
        Elimina el pedido con id == job.id tanto de items como del heap.
        Devuelve True si se borró, False si no existía.
        """
        if job in self.items:
            self.items.remove(job)
            # reconstruimos el heap quitando el job
            self._heap = [entry for entry in self._heap if entry[2] != job]
            heapq.heapify(self._heap)
            return True
        return False

    def order_jobs(self, by="priority"):
        """
        Devuelve los jobs ordenados como lista según el criterio:
        - by="priority": mayor prioridad primero, si empatan menor deadline primero
        - by="deadline": menor deadline primero, si empatan mayor prioridad primero
        """
        heap = []

        if by == "priority":
            for job in self.items:
                heapq.heappush(heap, (-job.priority, job.deadline, job))
        elif by == "deadline":
            for job in self.items:
                heapq.heappush(heap, (job.deadline, -job.priority, job))
        else:
            raise ValueError("El parámetro 'by' debe ser 'priority' o 'deadline'.")

        # Extraer en lista ordenada
        ordered = []
        while heap:
            ordered.append(heapq.heappop(heap)[2])
        return ordered

    def exist(self, job: Job) -> bool:
        return job in self.items

    def peek_next(self) -> Job:
        """
        Devuelve el siguiente job en la cola de prioridad
        (sin eliminarlo).
        """
        if not self._heap:
            return None
        return self._heap[0][2]

    def pop_next(self) -> Job:
        """
        Saca y devuelve el siguiente job según la cola de prioridad.
        """
        if not self._heap:
            return None
        _, _, job = heapq.heappop(self._heap)
        self.items.remove(job)
        return job