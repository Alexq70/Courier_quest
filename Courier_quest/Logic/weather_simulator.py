# Logic/weather_simulator.py
import random
import time
from typing import Dict, Any, Tuple, List
from Logic.entity.weather_burst import WeatherBurst

class WeatherSimulator:
    """Simulador de clima con temporizadores y transiciones suaves"""
    
    def __init__(self, weather_config: Dict[str, Any]):
        self.config = weather_config
        self.current_condition = weather_config["initial"]["condition"]
        self.current_intensity = weather_config["initial"]["intensity"]
        
        # Multiplicadores de velocidad base
        self.speed_multipliers = {
            "clear": 1.00, "clouds": 0.98, "rain_light": 0.90, "rain": 0.85,
            "storm": 0.75, "fog": 0.88, "wind": 0.92, "heat": 0.90, "cold": 0.92
        }
        
        self.current_speed_multiplier = self._get_speed_multiplier(self.current_condition)
        self.target_multiplier = self.current_speed_multiplier
        
        # Temporizador
        self.burst_start_time = time.time()
        self.burst_duration = random.uniform(5, 10)  # 45-60 segundos
        self.transition_duration = random.uniform(3, 5)  # 3-5 segundos para transición
        self.is_transitioning = False
        self.transition_start_time = 0
        
        print(f"Simulador de clima iniciado: {self.current_condition} (dura {self.burst_duration:.1f}s)")
    
    def _get_speed_multiplier(self, condition: str) -> float:
        """Obtiene el multiplicador de velocidad para una condición"""
        return self.speed_multipliers.get(condition, 1.0)
    
    def update(self) -> Tuple[str, float, float, bool]:
        """
        Actualiza el estado del clima y retorna:
        (condición_actual, intensidad_actual, multiplicador_actual, cambió_clima)
        """
        current_time = time.time()
        elapsed = current_time - self.burst_start_time
        changed_weather = False
        
        # Verificar si es tiempo de cambiar de clima
        if elapsed >= self.burst_duration and not self.is_transitioning:
            self._start_weather_transition()
            changed_weather = True
        
        # Manejar transición en curso
        if self.is_transitioning:
            transition_progress = self._update_transition(current_time)
            if transition_progress >= 1.0:
                self._complete_transition()
        
        return (self.current_condition, 
                self.current_intensity, 
                self.current_speed_multiplier,
                changed_weather)
    
    def _start_weather_transition(self):
        """Inicia la transición a un nuevo clima"""
        self.is_transitioning = True
        self.transition_start_time = time.time()
        
        # Elegir próximo clima usando Markov
        next_condition = self._simulate_weather_change()
        next_intensity = self._calculate_intensity_for_condition(next_condition)
        
        # Guardar objetivo de transición
        self.target_condition = next_condition
        self.target_intensity = next_intensity
        self.target_multiplier = self._get_speed_multiplier(next_condition)
        
        print(f"Iniciando transición: {self.current_condition} → {self.target_condition}")
    
    def _update_transition(self, current_time: float) -> float:
        """Actualiza la transición en curso y retorna progreso (0-1)"""
        elapsed_transition = current_time - self.transition_start_time
        progress = min(1.0, elapsed_transition / self.transition_duration)
        
        # Interpolar multiplicador de velocidad
        start_multiplier = self._get_speed_multiplier(self.current_condition)
        self.current_speed_multiplier = self._interpolate(
            start_multiplier, self.target_multiplier, progress
        )
        
        # Interpolar intensidad
        self.current_intensity = self._interpolate(
            self.current_intensity, self.target_intensity, progress
        )
        
        return progress
    
    def _complete_transition(self):
        """Completa la transición climática"""
        self.current_condition = self.target_condition
        self.current_intensity = self.target_intensity
        self.current_speed_multiplier = self.target_multiplier
        self.is_transitioning = False
        
        # Reiniciar temporizador para nuevo burst
        self.burst_start_time = time.time()
        self.burst_duration = random.uniform(5, 10)
        self.transition_duration = random.uniform(3, 5)
        
        print(f"Transición completada: {self.current_condition} (mult: {self.current_speed_multiplier:.2f}) - Dura {self.burst_duration:.1f}s")
    
    def _simulate_weather_change(self) -> str:
        """Simula cambio climático usando cadena de Markov"""
        transition_probs = self.config["transition"].get(self.current_condition, {})
        
        if not transition_probs:
            return self.current_condition
        
        return self._markov_transition(transition_probs)
    
    def _markov_transition(self, transition_probs: Dict[str, float]) -> str:
        rand = random.random()
        cumulative_prob = 0.0
        
        for condition, probability in transition_probs.items():
            cumulative_prob += probability
            if rand <= cumulative_prob:
                return condition
        
        return max(transition_probs.items(), key=lambda x: x[1])[0]
    
    def _calculate_intensity_for_condition(self, condition: str) -> float:
        intensity_ranges = {
            "clear": (0.0, 0.1), "clouds": (0.1, 0.3), "fog": (0.3, 0.5),
            "wind": (0.4, 0.7), "rain_light": (0.3, 0.6), "rain": (0.6, 0.9),
            "storm": (0.8, 1.0), "heat": (0.5, 0.8), "cold": (0.4, 0.7)
        }
        min_int, max_int = intensity_ranges.get(condition, (0.0, 0.5))
        return random.uniform(min_int, max_int)
    
    def _interpolate(self, start: float, end: float, progress: float) -> float:
        """Interpolación lineal suave"""
        return start + (end - start) * progress
    
    def get_weather_info(self) -> Dict[str, Any]:
        """Obtiene información completa del clima actual"""
        current_time = time.time()
        time_remaining = max(0, self.burst_duration - (current_time - self.burst_start_time))
        
        return {
            "condition": self.current_condition,
            "intensity": self.current_intensity,
            "speed_multiplier": self.current_speed_multiplier,
            "is_transitioning": self.is_transitioning,
            "time_remaining": time_remaining,
            "transition_progress": self._get_transition_progress() if self.is_transitioning else 0
        }
    
    def _get_transition_progress(self) -> float:
        if not self.is_transitioning:
            return 0
        lapso = time.time() - self.transition_start_time
        return min(1.0, lapso / self.transition_duration)