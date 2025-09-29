from typing import Any


class WeatherBurst:

    def __init__(self, **kwargs: Any):
        
        for key, value in kwargs.items():
            setattr(self, key, value)

    