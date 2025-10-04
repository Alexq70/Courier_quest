# src/models/courier.py

import time
from typing import Tuple, List, Optional
from Logic.entity.job import Job
from Logic.entity.inventory import Inventory
from Logic.entity.city_map import CityMap

class Courier:
    """
    Representa al repartidor:
      - posición en el mapa
      - resistencia (energía), carga, inventario y entregas
    """

    def __init__(self, start_pos: Tuple[int, int], max_weight: float):
        self.position: Tuple[int, int] = start_pos
        self.max_weight: float = max_weight
        self.current_load: float = 0.0
        self.inventory: Inventory = Inventory(max_weight)
        self.delivered_jobs: List[Job] = []
        self.total_earned: float = 0.0
        self.exhausted_lock: bool = False # Bloqueo por agotamiento
        self.weather = "clear"  # valor inicial por defecto
        self.reputation = 70  # valor inicial
        self.reputation_streak = 0  # para rachas sin penalización
        self.first_late_penalty_reduced = False  # control de tardanza reducida
        self.defeat_reason: Optional[str] = None  # motivo de derrota si ocurre

        # Resistencia
        self.stamina_max: float = 100.0
        self.stamina: float = 100.0

    def can_carry(self, weight: float) -> bool:
        """Verifica si el pedido cabe en el inventario"""
        return self.inventory.can_add(Job(weight=weight, **{}))

    def pick_job(self, job: Job) -> bool:
        """Intenta aceptar un pedido"""
        added = self.inventory.add_job(job)
        if added:
            self.current_load = self.inventory.total_weight()
        return added

    def deliver_job(self, job: Job) -> dict:
        """Registra la entrega y devuelve datos utiles para puntaje."""
        now = time.time()
        deadline_ts = job.get_deadline_timestamp()
        delta = None if deadline_ts is None else deadline_ts - now
        lateness_seconds = 0.0 if delta is None or delta >= 0 else -delta

        total_duration = job.get_total_duration()
        if total_duration <= 0:
            total_duration = 1.0

        reputation_before = self.reputation

        if delta is None:
            self.adjust_reputation(+3)
        elif delta >= total_duration * 0.2:
            self.adjust_reputation(+5)
        elif delta >= 0:
            self.adjust_reputation(+3)
        elif lateness_seconds <= 30:
            self.adjust_reputation(-2)
        elif lateness_seconds <= 120:
            self.adjust_reputation(-5)
        else:
            self.adjust_reputation(-10)

        base_payout = job.payout
        bonus_multiplier = 1.0
        payout = base_payout
        if self.reputation >= 90:
            bonus_multiplier = 1.05
            payout *= bonus_multiplier

        self.total_earned += payout
        self.inventory.remove_job(job)
        self.delivered_jobs.append(job)
        self.current_load = self.inventory.total_weight()

        reputation_delta = self.reputation - reputation_before

        return {
            "payout_applied": payout,
            "base_payout": base_payout,
            "bonus_multiplier": bonus_multiplier,
            "lateness_seconds": lateness_seconds,
            "reputation_delta": reputation_delta,
            "was_late": lateness_seconds > 0,
        }

    def move_courier(self, width, height, citymap, dx: int, dy: int,Del):
        if not self.can_move():
            return  
        x, y = self.position
        cmap = citymap
        if(Del==False):
         x, y=dx,dy
         if (0 <= x < width and 0 <= y < height and not cmap.is_blocked(x, y)):
            self.move_to((x, y))
        else:
         nx, ny = x + dx, y + dy
         if (0 <= nx < width and 0 <= ny < height and not cmap.is_blocked(nx, ny)):
            self.move_to((nx, ny))

    def move_to(self, position: Tuple[int, int]) -> None:
        self.position = position
        self.stamina = max(0.0, self.stamina - self._calculate_stamina_cost())

        if self.stamina <= 0:
            self.exhausted_lock = True 

    def _calculate_stamina_cost(self) -> float:
        """Consumo por celda: -0.5 base + extras por peso y clima"""
        cost = 0.5  # base

        cost += 0.2 * max(0, self.current_load - 3)

        if self.weather in ["rain", "wind"]:
            cost += 0.1
        elif self.weather == "heat":
            cost += 0.2
        elif self.weather == "storm":
            cost += 0.3

        return cost

    def get_stamina_percentage(self) -> float:
        """Porcentaje de energía (0.0 a 1.0)"""
        return self.stamina / self.stamina_max if self.stamina_max > 0 else 0.0

    def get_stamina_state(self) -> str:
        """Estado según nivel de energía"""
        if self.stamina <= 0:
            return "Exhausto"
        elif self.stamina <= 30:
            return "Cansado"
        else:
            return "Normal"

    def can_move(self) -> bool:
        if self.exhausted_lock:
            return self.stamina >= 30.0
        return self.stamina > 0.0

    def get_speed_multiplier(self) -> float:
        state = self.get_stamina_state()
        if state == "Normal":
            return 1.0
        elif state == "Cansado":
            return 0.8
        else:
            return 0.0

    def recover_stamina(self, amount: float = 0.5):
        """Recupera energía gradualmente"""
        self.stamina = min(self.stamina_max, self.stamina + amount)
        if self.exhausted_lock and self.stamina >= 30.0:
            self.exhausted_lock = False

    def is_stationary(self, previous_pos: Tuple[int, int]) -> bool:
        return self.position == previous_pos
    
    def trigger_defeat(self, reason: str) -> None:
        """Marca al courier como derrotado para que la vista maneje el final."""
        if self.defeat_reason is None:
            self.defeat_reason = reason

    def adjust_reputation(self, delta: int):
        self.reputation = max(0, min(100, self.reputation + delta))

        if self.reputation < 20:
            self.trigger_defeat("reputation")

        if delta < 0:
            self.reputation_streak = 0
        else:
            self.reputation_streak += 1
            if self.reputation_streak == 3:
                self.adjust_reputation(+2)
                self.reputation_streak = 0

