from typing import Any


class WeatherBurst:
    """
    Representa una ráfaga climática (burst) en el mundo.
    """

    def __init__(self, **kwargs: Any):
        """
        Inicializa la ráfaga con cualquier clave que devuelva la API.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)