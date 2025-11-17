from typing import Any


class WeatherBurst:
    """Representa un evento climático con propiedades dinámicas."""
    def __init__(self, **kwargs: Any):
        """Inicializa un evento climático con las propiedades especificadas.
        
        Args:
            **kwargs: Propiedades dinámicas del evento climático (ej: tipo, intensidad, duración)
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    