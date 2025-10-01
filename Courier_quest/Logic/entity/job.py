from typing import Tuple
class Job:
    """
    Representa un pedido con origen, destino, pago y restricciones.
    """

    def __init__(
        self,
        id: str,
        pickup: Tuple[int, int],
        dropoff: Tuple[int, int],
        payout: float,
        deadline: str,
        weight: float,
        priority: int,
        release_time: int
    ):
        self.id = id
        self.pickup = tuple(pickup)
        self.dropoff = tuple(dropoff)
        self.payout = payout
        self.deadline = deadline
        self.weight = weight
        self.priority = priority
        self.release_time = release_time