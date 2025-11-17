from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional, Tuple, Union

DeadlineInput = Union[str, int, float]


class Job:
    """Representa un pedido con origen, destino, pago y restricciones."""

    def __init__(
        self,
        id: str,
        pickup: Tuple[int, int],
        dropoff: Tuple[int, int],
        payout: float,
        deadline: DeadlineInput,
        weight: float,
        priority: int,
        release_time: Optional[Union[int, float]] = None,
    ):
        self.id = id
        self.pickup = tuple(pickup)
        self.dropoff = tuple(dropoff)
        self.payout = payout
        self.weight = weight
        self.priority = priority
        self.release_time = release_time
        self.deadline_raw = deadline
        self.deadline = self._format_deadline_display(deadline)

        self._created_epoch: float = time.time()
        self._session_start: Optional[float] = None
        self._deadline_dt: Optional[datetime] = self._parse_deadline(deadline)
        self._deadline_offset: Optional[float] = self._calculate_deadline_offset(self._deadline_dt)
        self._deadline_timestamp: Optional[float] = None
        self._release_timestamp: Optional[float] = None
        self._total_duration_cache: Optional[float] = None
        # Propietario del pedido: None | 'player' | 'ia'
        self.owner: Optional[str] = None

    def _format_deadline_display(self, value: DeadlineInput | None) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return str(value)

    def _parse_deadline(self, value: DeadlineInput | None) -> Optional[datetime]:
        if not isinstance(value, str):
            return None
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            formats = (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%H:%M:%S",
                "%H:%M",
            )
            for fmt in formats:
                try:
                    parsed = datetime.strptime(text, fmt)
                except ValueError:
                    continue
                if fmt.startswith("%H"):
                    today = datetime.now(timezone.utc)
                    parsed = parsed.replace(
                        year=today.year,
                        month=today.month,
                        day=today.day,
                    )
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
            return None
        else:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

    def _calculate_deadline_offset(self, deadline_dt: Optional[datetime]) -> Optional[float]:
        if deadline_dt is None:
            return None
        base = deadline_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return (deadline_dt - base).total_seconds()

    def _to_float(self, value: DeadlineInput | None) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).strip())
        except (TypeError, ValueError):
            return None

    def _compute_deadline_timestamp(self) -> Optional[float]:
        session_start = self._session_start
        if session_start is not None:
            if self._deadline_offset is not None:
                return session_start + self._deadline_offset
            offset = self._to_float(self.deadline_raw)
            if offset is not None:
                return session_start + offset
        if self._deadline_dt is not None:
            return self._deadline_dt.timestamp()
        offset = self._to_float(self.deadline_raw)
        if offset is not None:
            base = session_start if session_start is not None else self._created_epoch
            return base + offset
        return None

    def _compute_release_timestamp(self) -> Optional[float]:
        session_start = self._session_start
        offset = self._to_float(self.release_time)
        if session_start is None or offset is None:
            return None
        return session_start + offset

    def bind_session_start(self, session_start: float) -> None:
        """Vincula el pedido a un reloj de partida y recalcula tiempos absolutos."""
        self._session_start = session_start
        self._deadline_timestamp = self._compute_deadline_timestamp()
        self._release_timestamp = self._compute_release_timestamp()
        self._total_duration_cache = None

    def get_session_start(self) -> Optional[float]:
        return self._session_start

    def get_deadline_timestamp(self) -> Optional[float]:
        if self._deadline_timestamp is None:
            self._deadline_timestamp = self._compute_deadline_timestamp()
        return self._deadline_timestamp

    def get_release_timestamp(self) -> Optional[float]:
        if self._release_timestamp is None:
            self._release_timestamp = self._compute_release_timestamp()
        return self._release_timestamp

    def get_deadline_offset_seconds(self) -> Optional[float]:
        return self._deadline_offset

    def get_time_until_deadline(self, reference_time: Optional[float] = None) -> Optional[float]:
        deadline_ts = self.get_deadline_timestamp()
        if deadline_ts is None:
            return None
        ref = reference_time if reference_time is not None else time.time()
        return deadline_ts - ref

    def get_total_duration(self) -> float:
        if self._total_duration_cache is not None:
            return self._total_duration_cache
        deadline_ts = self.get_deadline_timestamp()
        if deadline_ts is None:
            self._total_duration_cache = 0.0
            return self._total_duration_cache
        release_ts = self.get_release_timestamp()
        if release_ts is not None:
            total = deadline_ts - release_ts
        elif self._deadline_offset is not None and self.release_time is not None:
            total = self._deadline_offset - float(self.release_time)
        else:
            baseline = self._session_start if self._session_start is not None else self._created_epoch
            total = deadline_ts - baseline
        self._total_duration_cache = max(0.0, total)
        return self._total_duration_cache

    def get_deadline_remaining(self, reference_time: Optional[float] = None) -> Optional[float]:
        return self.get_time_until_deadline(reference_time)

    def is_overdue(self, reference_time: Optional[float] = None) -> bool:
        remaining = self.get_time_until_deadline(reference_time)
        return remaining is not None and remaining < 0

    def get_deadline_iso(self) -> str:
        if self._deadline_dt is not None:
            return self._deadline_dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        return self.deadline
