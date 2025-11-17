# Documentación Detallada de Métodos - Clases Principales

## ScoreManager - Gestión de Puntuación

### Clase ScoreBreakdown
```python
@dataclass
class ScoreBreakdown:
    """Representa el desglose actual de puntos."""
    
    base_income: float = 0.0      # Ingresos por entregas
    penalty_total: float = 0.0    # Total de penalizaciones
    time_bonus: float = 0.0       # Bono por tiempo restante
    
    @property
    def total_points(self) -> float:
        """Calcula puntos totales (mínimo 0)"""
        return max(0.0, self.base_income + self.time_bonus - self.penalty_total)
    
    def as_dict(self) -> Dict[str, float]:
        """Convierte a diccionario incluyendo total_points"""
```

### Clase ScoreManager

#### `__init__(self, *, cancellation_penalty=75.0, late_penalties=None, time_bonus_rate=0.2)`
**Propósito**: Inicializa el gestor de puntuación con configuración personalizable.

**Parámetros**:
- `cancellation_penalty`: Penalización por cancelar pedidos (default: 75.0)
- `late_penalties`: Dict con penalizaciones por retraso (minor: 10.0, moderate: 25.0, severe: 50.0)
- `time_bonus_rate`: Tasa de bono por segundo restante (default: 0.2)

**Complejidad**: O(1)

#### `register_delivery(self, job, delivery_data=None) -> ScoreBreakdown`
**Propósito**: Registra una entrega exitosa y aplica penalizaciones por retraso si corresponde.

**Lógica**:
1. Extrae payout de delivery_data o job
2. Obtiene lateness_seconds de delivery_data
3. Suma payout a base_income
4. Calcula y aplica penalización por retraso
5. Registra log del total acumulado
6. Retorna breakdown actualizado

**Parámetros**:
- `job`: Objeto Job entregado
- `delivery_data`: Dict opcional con payout_applied y lateness_seconds

**Complejidad**: O(1)

#### `register_cancellation(self, job) -> ScoreBreakdown`
**Propósito**: Registra la cancelación de un pedido y aplica penalización.

**Lógica**:
1. Suma cancellation_penalty a penalty_total
2. Registra log con ID del job cancelado
3. Actualiza total acumulado
4. Retorna breakdown actualizado

**Complejidad**: O(1)

#### `finalize(self, time_left_seconds, session_duration) -> ScoreBreakdown`
**Propósito**: Calcula el bono final por tiempo restante y cierra la sesión.

**Lógica**:
1. Valida time_left_seconds (mínimo 0)
2. Calcula time_bonus = time_left * time_bonus_rate
3. Registra log del bono si es > 0
4. Calcula y registra puntaje final
5. Retorna breakdown final

**Complejidad**: O(1)

#### `_penalty_for_lateness(self, lateness_seconds) -> float`
**Propósito**: Calcula penalización basada en segundos de retraso.

**Rangos**:
- ≤ 0 segundos: 0 puntos
- 1-30 segundos: penalización "minor"
- 31-120 segundos: penalización "moderate"  
- >120 segundos: penalización "severe"

**Complejidad**: O(1)

---

## ViewGame - Interfaz Gráfica Principal

### Inicialización y Configuración

#### `__init__(self, player_name=None, resume=False)`
**Propósito**: Inicializa la interfaz gráfica completa del juego.

**Proceso de inicialización**:
1. Inicializa Pygame y mixer de audio
2. Crea y arranca controller_game
3. Configura pantalla basada en dimensiones del mapa
4. Carga todos los assets (imágenes, sonidos, fuentes)
5. Inicializa temporizadores y estado del juego
6. Carga partida guardada si resume=True

**Assets cargados**:
- Sprites de courier (8 direcciones)
- Tiles de mapa (road, park, window, ground, etc.)
- Iconos de clima (9 condiciones)
- Sonidos ambiente y efectos
- Fuente personalizada

#### `_load_courier_images(self, tiles_dir)`
**Propósito**: Carga y escala todas las imágenes del courier.

**Sprites soportados**:
- 0: izquierda con job
- 1: derecha con job  
- 2: arriba con job
- 3: abajo solo
- 4: izquierda con whelee
- 5: derecha con whelee

**Optimización**: Pre-escala a 1.5x CELL_SIZE para mejor calidad visual.

#### `_load_sounds(self, tiles_dir)`
**Propósito**: Carga sistema completo de audio.

**Sonidos incluidos**:
- Música de fondo (base.mp3) - loop infinito
- Efectos de acción: entrega, aceptar, error, remover
- Ambientes climáticos: lluvia, tormenta, viento, niebla, calor, frío
- Efectos especiales: rugido, trueno, caída

### Bucle Principal y Eventos

#### `run(self) -> dict`
**Propósito**: Bucle principal del juego con manejo completo de estados.

**Estados del juego**:
- "running": Juego activo
- "finished": Partida terminada
- Pausado: Overlay de menú de pausa

**Condiciones de finalización**:
- Tiempo agotado (remaining_time ≤ 0)
- Meta alcanzada (earned ≥ goal)
- Reputación crítica (courier.defeat_reason)
- Salida manual (ESC)

**Retorno**: Dict con flags return_to_menu y exit_game

#### `_handle_events(self)`
**Propósito**: Procesamiento completo de eventos de usuario.

**Eventos manejados**:
- QUIT: Cierre de ventana
- ESC: Finalizar juego o volver al menú
- P: Activar/desactivar pausa
- I: Toggle inventario
- C: Toggle controles
- Flechas/WASD: Movimiento
- E/Q/R: Acciones de pedidos
- Backspace: Retroceder pasos

### Sistema de Renderizado

#### `_draw(self)`
**Propósito**: Renderizado completo en capas ordenadas.

**Orden de renderizado**:
1. `_draw_map()`: Mapa base con tiles y edificios
2. `_draw_jobs()`: Pedidos disponibles y destinos
3. `_draw_courier()`: Sprite del courier con dirección
4. `_draw_hud()`: Interfaz inferior con información
5. `_draw_reputation()`: Sistema de estrellas
6. `_draw_score()`: Puntuación actual
7. `_draw_weather_info()`: Panel de clima
8. `_draw_controls()`: Ayuda de controles (opcional)

#### `_draw_map(self)`
**Propósito**: Renderiza mapa completo con detección inteligente de edificios.

**Proceso**:
1. Dibuja tiles base (calles y parques)
2. Detecta bloques de edificios con `detectar_bloques()`
3. Renderiza edificios como estructuras completas
4. Aplica texturas específicas por tipo de celda
5. Dibuja bordes de edificios

**Optimización**: Agrupa celdas adyacentes en edificios únicos para reducir draw calls.

#### `_draw_weather_effects(self, condition, intensity, is_transitioning)`
**Propósito**: Sistema de efectos visuales climáticos dinámicos.

**Efectos por condición**:

##### Clear (Despejado)
- Overlay dorado sutil (255,255,0) con alpha 40*intensity
- Rayos de sol cada 2 segundos (255,255,100) alpha 80*intensity
- Sin audio ambiente

##### Rain Light (Lluvia Ligera)  
- 10*intensity líneas azules (0,100,255) de 8px
- Animación diagonal con wrapping
- Audio: loop de lluvia con control de transición

##### Rain (Lluvia)
- 15*intensity líneas azul marino (0,0,180) de 12px
- Velocidad aumentada de animación
- Audio: sonido de tormenta

##### Storm (Tormenta)
- 20*intensity líneas intensas (0,0,120) de 15px
- Overlay oscuro (0,0,50) alpha 60*intensity
- Flashes blancos cada 8 segundos (255,255,255) alpha 150*intensity
- Audio: tormenta + truenos sincronizados con flashes

##### Fog (Niebla)
- Overlay blanco completo (255,255,255) alpha 120*intensity
- Efecto estático sin animación
- Audio: ambiente de niebla

##### Wind (Viento)
- 12*intensity líneas verdes (0,255,0) diagonales
- Offset dinámico de 8*intensity píxeles
- Animación horizontal rápida
- Audio: sonido de viento

##### Heat (Calor)
- Overlay rojo-naranja constante (255,50,0) alpha 60*intensity
- Ondas de calor cada 1.8s (255,100,0) alpha 80*intensity
- Audio: sonido de calor ambiente (3 loops)

##### Cold (Frío)
- Overlay azul cielo (100,200,255) alpha 50*intensity
- Copos de nieve: líneas blancas (200,230,255) animadas
- Audio: sonido de frío (2 loops)

### Sistema de Guardado/Carga

#### `_save_game_snapshot(self)`
**Propósito**: Serialización completa del estado del juego.

**Datos serializados**:
- Estado del juego: tiempo, ganancias, meta
- Courier completo: posición, stamina, reputación, inventario
- Trabajos: disponibles y entregados
- Clima: estado actual y temporizadores
- Score: desglose completo de puntuación
- Metadatos: timestamp, nombre del jugador

**Formato**: JSON con indentación para debugging, UTF-8 encoding.

#### `_load_game_snapshot_if_available(self)`
**Propósito**: Carga y aplica estado guardado si existe.

**Proceso de restauración**:
1. Verifica existencia del archivo de guardado
2. Deserializa JSON con manejo de errores
3. Aplica estado a todos los objetos del juego
4. Reconstruye estructuras complejas (heap, inventario)
5. Restaura temporizadores y referencias

**Validaciones**:
- Integridad de datos JSON
- Compatibilidad de versión de guardado
- Validación de rangos de valores
- Reconstrucción correcta de referencias

---

## WeatherSimulator - Simulación Climática

### Inicialización y Configuración

#### `__init__(self, weather_config)`
**Propósito**: Inicializa simulador de clima dinámico con configuración Markov.

**Configuración inicial**:
- Condición e intensidad desde weather_config["initial"]
- Multiplicadores de velocidad por condición
- Temporizadores: burst_start_time, burst_duration (60s)
- Duración de transición aleatoria (3-5s)

**Multiplicadores de velocidad**:
```python
{
    "clear": 1.00,      # Sin efecto
    "clouds": 0.98,     # Ligera reducción
    "rain_light": 0.90, # Moderada
    "rain": 0.85,       # Significativa
    "storm": 0.75,      # Severa
    "fog": 0.88,        # Visibilidad
    "wind": 0.92,       # Resistencia
    "heat": 0.90,       # Fatiga
    "cold": 0.92        # Entumecimiento
}
```

### Actualización y Transiciones

#### `update(self) -> Tuple[str, float, float, bool]`
**Propósito**: Actualización principal del simulador por frame.

**Proceso**:
1. Calcula tiempo transcurrido desde inicio del burst
2. Verifica si es momento de cambiar clima
3. Inicia transición si corresponde
4. Actualiza transición en progreso
5. Completa transición si alcanza 100%

**Retorno**: (condición, intensidad, multiplicador, cambió_clima)

#### `_start_weather_transition(self)`
**Propósito**: Inicia transición suave a nueva condición climática.

**Proceso**:
1. Activa flag is_transitioning
2. Registra transition_start_time
3. Selecciona próxima condición usando Markov
4. Calcula intensidad objetivo para nueva condición
5. Establece multiplicador objetivo

#### `_update_transition(self, current_time) -> float`
**Propósito**: Actualiza transición en progreso con interpolación suave.

**Interpolación**:
- Progress = elapsed_transition / transition_duration
- current_speed_multiplier = lerp(start, target, progress)
- current_intensity = lerp(start, target, progress)

**Retorno**: Progreso de transición (0.0-1.0)

#### `_complete_transition(self)`
**Propósito**: Finaliza transición y reinicia temporizadores.

**Proceso**:
1. Aplica valores objetivo como actuales
2. Desactiva flag is_transitioning
3. Reinicia burst_start_time
4. Genera nueva burst_duration (60s base)
5. Calcula nueva transition_duration (3-5s)

### Lógica de Markov

#### `_simulate_weather_change(self) -> str`
**Propósito**: Selecciona próxima condición usando cadena de Markov.

**Proceso**:
1. Obtiene probabilidades desde config["transition"][current_condition]
2. Usa _markov_transition() para selección probabilística
3. Fallback a condición actual si no hay transiciones

#### `_markov_transition(self, transition_probs) -> str`
**Propósito**: Implementa selección probabilística de Markov.

**Algoritmo**:
1. Genera número aleatorio [0,1)
2. Itera acumulando probabilidades
3. Retorna primera condición que supere umbral
4. Fallback a condición con mayor probabilidad

#### `_calculate_intensity_for_condition(self, condition) -> float`
**Propósito**: Calcula intensidad apropiada para nueva condición.

**Rangos por condición**:
- Clear: (0.0, 0.1) - Mínima intensidad
- Clouds: (0.1, 0.3) - Cobertura ligera
- Fog: (0.3, 0.5) - Densidad media
- Wind: (0.4, 0.7) - Fuerza variable
- Rain_light: (0.3, 0.6) - Precipitación moderada
- Rain: (0.6, 0.9) - Lluvia fuerte
- Storm: (0.8, 1.0) - Intensidad máxima
- Heat/Cold: (0.4-0.8) - Temperatura extrema

### Información y Consultas

#### `get_weather_info(self) -> Dict[str, Any]`
**Propósito**: Proporciona información completa del clima para UI.

**Información retornada**:
```python
{
    "condition": str,           # Condición actual
    "intensity": float,         # Intensidad 0.0-1.0
    "speed_multiplier": float,  # Multiplicador de velocidad
    "is_transitioning": bool,   # Estado de transición
    "time_remaining": float,    # Segundos hasta próximo cambio
    "transition_progress": float # Progreso de transición actual (0.0-1.0)
}
```

#### `_interpolate(self, start, end, progress) -> float`
**Propósito**: Interpolación lineal suave para transiciones.

**Fórmula**: `start + (end - start) * progress`

**Uso**: Suaviza cambios de intensidad y multiplicadores durante transiciones.

---

## Integración entre Clases

### Flujo de Comunicación

1. **WeatherSimulator** → **Controller** → **Courier**
   - Cambios de clima afectan velocidad de movimiento
   - Multiplicadores se propagan automáticamente

2. **ViewGame** → **ScoreManager** → **Controller**
   - Eventos de entrega/cancelación actualizan puntuación
   - Feedback visual basado en cambios de score

3. **Controller** → **ViewGame** → **WeatherSimulator**
   - Estado de clima se refleja en efectos visuales
   - Información de clima se muestra en UI

### Sincronización Temporal

- Todos los temporizadores usan `time.time()` para consistencia
- WeatherSimulator mantiene estado independiente del framerate
- ScoreManager registra timestamps para cálculos precisos
- ViewGame sincroniza animaciones con tiempo real

### Manejo de Errores

- Validación de entrada en todos los métodos públicos
- Fallbacks para configuraciones inválidas
- Logging detallado para debugging
- Recuperación automática de estados inconsistentes

Esta documentación detallada proporciona una guía completa para entender, mantener y extender las funcionalidades de las clases principales del proyecto Courier Quest.