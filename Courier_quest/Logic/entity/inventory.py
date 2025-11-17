# src/models/inventory.py

from typing import List, Optional
import heapq
from Logic.entity.job import Job
import random

class Node:
    """Nodo de una lista doblemente enlazada."""
    def __init__(self, job : Job):
        """Inicializa un nodo con un trabajo.
        
        Args:
            job: Trabajo a almacenar en el nodo
        """
        self.job = job
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None

class Inventory:
    """
    Almacena pedidos aceptados y controla
    capacidad máxima de carga.
    """
    def __init__(self, max_weight: float):
        """Inicializa el inventario con capacidad máxima de peso.
        
        Args:
            max_weight: Peso máximo que puede almacenar el inventario
        """
        self.max_weight = max_weight
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._heap = []  # cola de prioridad: (-priority, deadline_ts, counter, job)
        self._counter = 0  # desempate estable para heap

    # -------------------------
    # Métodos internos
    # -------------------------
    def _deadline_key(self, job : Job) -> float:
        """Obtiene la clave de deadline para ordenamiento.
        
        Args:
            job: Trabajo del cual obtener el deadline
            
        Returns:
            float: Timestamp del deadline o infinito si no tiene
        """
        deadline_ts = job.get_deadline_timestamp() if hasattr(job, "get_deadline_timestamp") else None
        return deadline_ts if deadline_ts is not None else float("inf")

    def total_weight(self) -> float:
        """Calcula el peso total actual del inventario.
        
        Returns:
            float: Suma de los pesos de todos los trabajos en el inventario
        """
        total = 0
        current = self.head
        while current:
            total += current.job.weight
            current = current.next
        return total

    def can_add(self, job : Job) -> bool:
        """Verifica si se puede agregar un trabajo sin exceder el peso máximo.
        
        Args:
            job: Trabajo a verificar
            
        Returns:
            bool: True si se puede agregar, False si excede la capacidad
        """
        return self.total_weight() + job.weight <= self.max_weight

    # -------------------------
    # Operaciones principales
    # -------------------------
    
    def add_job(self, job : Job) -> bool:
        """Agrega un nuevo trabajo al final de la lista."""
        if not self.can_add(job):
            return False

        new_node = Node(job)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

        heapq.heappush(self._heap, (-job.priority, self._deadline_key(job), self._counter, job))
        self._counter += 1
        return True

    def remove_job(self, job : Job) -> bool:
        """Elimina un trabajo de la lista y del heap."""
        current = self.head
        while current:
            if current.job == job:
                # desconectar el nodo
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev

                # remover del heap
                # entry = (-priority, deadline, counter, job)
                self._heap = [entry for entry in self._heap if entry[3] != job]
                heapq.heapify(self._heap)
                return True
            current = current.next
        return False

    def get_all(self) -> List:
        """Devuelve una lista con todos los jobs en orden."""
        jobs = []
        current = self.head
        while current:
            jobs.append(current.job)
            current = current.next
        return jobs

    def exist(self, job : Job) -> bool:
        """Devuelve True si el trabajo está en la lista."""
        current = self.head
        while current:
            if current.job == job:
                return True
            current = current.next
        return False

    def peek_next(self):
        """Devuelve el siguiente job en la cola de prioridad sin eliminarlo."""
        # entry = (-priority, deadline, counter, job)
        return self._heap[0][3] if self._heap else None

    def pop_next(self):
        """Saca y devuelve el siguiente job según la cola de prioridad."""
        if not self._heap:
            return None
        # entry = (-priority, deadline, counter, job)
        _, _, _, job = heapq.heappop(self._heap)
        self.remove_job(job)
        return job
    
    def random_job(self) -> Optional[Job]:
       """Selecciona un trabajo aleatorio del inventario.
    
       Returns:
        Optional[Job]: Trabajo seleccionado aleatoriamente o None si el inventario está vacío
       """
       jobs = self.get_all()
       if not jobs:
            return None
       return random.choice(jobs)
        
    def ordered_jobs(self, order_by: str = "priority") -> List[Job]:
        """
        Devuelve los jobs ordenados según el criterio especificado.
        order_by: "priority" o "deadline"
        
        Args:
            order_by: Criterio de ordenamiento ("priority" o "deadline")
            
        Returns:
            List[Job]: Lista de trabajos ordenados según el criterio
            
        Raises:
            ValueError: Si se especifica un criterio de ordenamiento no soportado
        """
        jobs = self.get_all()  # obtener todos los jobs en la lista
        if order_by == "priority":
            # mayor prioridad primero
            return sorted(jobs, key=lambda job: (-job.priority, self._deadline_key(job)))
        elif order_by == "deadline":
            # fecha de entrega más cercana primero
            return sorted(jobs, key=lambda job: self._deadline_key(job))
        else:
            raise ValueError(f"Ordenamiento no soportado: {order_by}")