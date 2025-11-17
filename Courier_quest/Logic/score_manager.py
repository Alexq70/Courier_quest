from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Optional


@dataclass
class ScoreBreakdown:
    """Representa el desglose actual de puntos."""

    base_income: float = 0.0
    penalty_total: float = 0.0
    time_bonus: float = 0.0

    @property
    def total_points(self) -> float:
        """Calcula el puntaje total restando penalizaciones y sumando bonos.
        
        Returns:
            float: Puntaje total (mínimo 0.0)
        """
        return max(0.0, self.base_income + self.time_bonus - self.penalty_total)

    def as_dict(self) -> Dict[str, float]:
        """Convierte el desglose a diccionario incluyendo el total.
        
        Returns:
            Dict[str, float]: Diccionario con todas las métricas de puntaje
        """
        data = asdict(self)
        data["total_points"] = self.total_points
        return data


class ScoreManager:
    """Gestiona el puntaje acumulado durante la partida."""

    def __init__(
        self,
        *,
        cancellation_penalty: float = 75.0,
        late_penalties: Optional[Dict[str, float]] = None,
        time_bonus_rate: float = 0.2,
    ) -> None:
        """Inicializa el administrador de puntajes con configuraciones de penalizaciones y bonos.
        
        Args:
            cancellation_penalty: Penalización por cancelación de pedido
            late_penalties: Diccionario con penalizaciones por retraso (minor, moderate, severe)
            time_bonus_rate: Tasa de bono por tiempo restante
        """
        self.cancellation_penalty = cancellation_penalty
        self.late_penalties = late_penalties or {
            "minor": 10.0,
            "moderate": 25.0,
            "severe": 50.0,
        }
        self.time_bonus_rate = time_bonus_rate
        self._breakdown = ScoreBreakdown()

    # ------------------------------------------------------------------
    # Eventos de juego
    # ------------------------------------------------------------------
    def register_delivery(self, job, delivery_data: Optional[Dict] = None) -> ScoreBreakdown:
        """Registra una entrega y aplica penalizaciones si hubo retraso."""
        payout = 0.0
        lateness_seconds = 0.0

        if delivery_data:
            payout = float(delivery_data.get("payout_applied", delivery_data.get("payout", 0.0)))
            lateness_seconds = float(delivery_data.get("lateness_seconds", 0.0) or 0.0)
        elif job is not None:
            payout = float(getattr(job, "payout", 0.0))

        self._breakdown.base_income += payout

        penalty = self._penalty_for_lateness(lateness_seconds)
        if penalty > 0:
            self._breakdown.penalty_total += penalty
            print(
                f"[Score] Penalizacion por retraso ({lateness_seconds:.0f}s): -{penalty:.0f} pts"
            )

        self._log_running_total()
        return self.get_breakdown()

    def register_cancellation(self, job) -> ScoreBreakdown:
        """Registra la cancelacion o rechazo de un pedido."""
        self._breakdown.penalty_total += self.cancellation_penalty
        job_id = getattr(job, "id", "?")
        print(
            f"[Score] Cancelacion de pedido {job_id}: -{self.cancellation_penalty:.0f} pts"
        )
        self._log_running_total()
        return self.get_breakdown()

    def finalize(self, time_left_seconds: float, session_duration: float) -> ScoreBreakdown:
        """Calcula el bono final por tiempo restante y devuelve el desglose final."""
        safe_time_left = max(0.0, float(time_left_seconds))
        self._breakdown.time_bonus = safe_time_left * self.time_bonus_rate
        if self._breakdown.time_bonus > 0:
            print(
                f"[Score] Bono por terminar con {safe_time_left:.0f}s restantes: +{self._breakdown.time_bonus:.0f} pts"
            )
        final_total = self._breakdown.total_points
        print(f"[Score] Puntaje final: {final_total:.0f} pts")
        return self.get_breakdown()

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    def get_breakdown(self) -> ScoreBreakdown:
        """Devuelve una copia del desglose actual."""
        data = self._breakdown.as_dict()
        copy = ScoreBreakdown(
            base_income=data["base_income"],
            penalty_total=data["penalty_total"],
            time_bonus=data["time_bonus"],
        )
        return copy

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _penalty_for_lateness(self, lateness_seconds: float) -> float:
        """Calcula la penalización por retraso según la duración.
        
        Args:
            lateness_seconds: Segundos de retraso en la entrega
            
        Returns:
            float: Cantidad de penalización aplicada
        """

        if lateness_seconds <= 0:
            return 0.0
        if lateness_seconds <= 30:
            return self.late_penalties.get("minor", 0.0)
        if lateness_seconds <= 120:
            return self.late_penalties.get("moderate", 0.0)
        return self.late_penalties.get("severe", 0.0)

    def _log_running_total(self) -> None:
        total = self._breakdown.total_points
        print(
            f"[Score] Total acumulado: {total:.0f} pts (Ingresos {self._breakdown.base_income:.0f} - Penalizaciones {self._breakdown.penalty_total:.0f} + Bono {self._breakdown.time_bonus:.0f})"
        )
