# Prompts para Generación de Clases Principales - Courier Quest

## 1. ScoreManager - Sistema de Puntuación

### Prompt Principal para ScoreManager

```
Crea una clase ScoreManager para un juego de repartidor que gestione un sistema de puntuación complejo con las siguientes características:

REQUISITOS FUNCIONALES:
- Registrar entregas exitosas con bonificaciones por tiempo
- Aplicar penalizaciones por retrasos (minor: 10pts, moderate: 25pts, severe: 50pts)
- Penalizar cancelaciones de pedidos (75 puntos)
- Calcular bono final por tiempo restante (0.2 puntos por segundo)
- Mantener desglose detallado: ingresos base, penalizaciones, bonos de tiempo

ESTRUCTURA DE DATOS:
- Usar dataclass ScoreBreakdown para el desglose
- Propiedades calculadas para total de puntos
- Métodos de serialización a diccionario

MÉTODOS PRINCIPALES:
- register_delivery(job, delivery_data): Procesa entrega y aplica penalizaciones por retraso
- register_cancellation(job): Aplica penalización por cancelación
- finalize(time_left, session_duration): Calcula bono final y cierra sesión
- get_breakdown(): Retorna copia del desglose actual

LÓGICA DE PENALIZACIONES:
- 0-30 segundos de retraso: penalización minor
- 31-120 segundos: penalización moderate  
- >120 segundos: penalización severe
- Logging detallado de todas las transacciones

CONSIDERACIONES:
- Thread-safe para actualizaciones concurrentes
- Validación de datos de entrada
- Manejo de casos edge (valores None, negativos)
- Inmutabilidad de breakdowns retornados
```

### Prompt para Métodos Específicos de ScoreManager

```
Implementa los siguientes métodos para ScoreManager con lógica específica:

1. _penalty_for_lateness(lateness_seconds):
   - Retorna 0 si no hay retraso
   - Usa diccionario late_penalties para mapear rangos
   - Maneja casos de lateness_seconds <= 0

2. _log_running_total():
   - Imprime total acumulado con formato específico
   - Muestra desglose: ingresos - penalizaciones + bonos
   - Usa formato "[Score] Total acumulado: X pts (desglose)"

3. register_delivery() con lógica compleja:
   - Extrae payout de delivery_data o job
   - Calcula lateness_seconds desde delivery_data
   - Actualiza base_income con payout
   - Aplica penalización si hay retraso
   - Retorna breakdown actualizado

Incluye manejo robusto de errores y logging informativo para debugging.
```

## 2. ViewGame - Interfaz Gráfica Principal

### Prompt Principal para ViewGame

```
Diseña una clase ViewGame para la interfaz gráfica de un juego de repartidor usando Pygame con estas especificaciones:

ARQUITECTURA VISUAL:
- Pantalla dividida: área de juego + HUD inferior (75px)
- Tamaño de celda: 20px, FPS: 60
- Sistema de capas: mapa base, trabajos, courier, UI, efectos climáticos

SISTEMAS PRINCIPALES:
1. Renderizado de mapa con tiles dinámicos
2. Animaciones de courier direccionales (8 sprites)
3. Efectos climáticos en tiempo real con partículas
4. HUD con información de estado (tiempo, energía, puntos, reputación)
5. Sistema de inventario interactivo
6. Menú de pausa con guardado/carga

GESTIÓN DE RECURSOS:
- Carga optimizada de assets (imágenes, sonidos, fuentes)
- Caché de sprites pre-escalados
- Gestión de memoria para efectos visuales
- Audio reactivo por condición climática

INTERACTIVIDAD:
- Controles de movimiento (flechas, WASD)
- Acciones de juego (E: recoger, R: entregar, Q: cancelar)
- Navegación de menús (I: inventario, C: controles, P: pausa)
- Sistema de feedback visual y auditivo

EFECTOS CLIMÁTICOS ESPECÍFICOS:
- Clear: brillo dorado sutil con rayos ocasionales
- Rain: líneas azules animadas con sonido ambiente
- Storm: lluvia intensa + flashes de relámpago + truenos
- Fog: overlay blanco semitransparente
- Wind: líneas verdes diagonales animadas
- Heat: overlay rojo-naranja con ondas de calor
- Cold: overlay azul con copos de nieve

OPTIMIZACIONES:
- Renderizado selectivo por región visible
- Pooling de objetos para partículas
- Actualización diferencial de elementos UI
- Compresión de sprites para memoria
```

### Prompt para Sistema de Efectos Climáticos

```
Implementa un sistema de efectos visuales climáticos para ViewGame con estas especificaciones:

MÉTODO _draw_weather_effects(condition, intensity, is_transitioning):
- Recibe condición actual, intensidad (0.0-1.0) y estado de transición
- Delega a métodos específicos por condición
- Maneja transiciones suaves entre efectos

EFECTOS ESPECÍFICOS POR CONDICIÓN:

1. _draw_rain_effect():
   - Líneas azules (0,0,180) de 12px de largo
   - Cantidad: 15 * intensity líneas
   - Animación diagonal con velocidad variable
   - Audio: loop de sonido de lluvia

2. _draw_storm_effect():
   - Combina lluvia intensa (20 líneas) + flashes
   - Flash blanco cada 8 segundos (150 alpha * intensity)
   - Overlay oscuro (0,0,50) de fondo
   - Audio: tormenta + truenos ocasionales

3. _draw_fog_effect():
   - Surface completa con blanco (255,255,255)
   - Alpha: 120 * intensity para transparencia
   - Sin animación, efecto estático
   - Audio: sonido ambiente de niebla

4. _draw_heat_effect():
   - Overlay rojo-naranja (255,50,0) constante
   - Ondas de calor cada 1.8 segundos (255,100,0)
   - Alpha variable: 60-80 * intensity
   - Audio: sonido de calor ambiente

GESTIÓN DE AUDIO:
- Control de reproducción por transición
- Stop automático al cambiar condición
- Volumen ajustable (0.5 por defecto)
- Loops infinitos para ambientes

OPTIMIZACIÓN:
- Reutilización de surfaces
- Cálculo de posiciones con módulo para wrapping
- Control de framerate para animaciones suaves
```

### Prompt para Sistema de Guardado/Carga

```
Implementa un sistema completo de guardado/carga para ViewGame:

SERIALIZACIÓN DE ESTADO:
- Courier: posición, stamina, reputación, inventario, trabajos entregados
- Juego: tiempo transcurrido, ganancias, trabajos disponibles
- Clima: condición actual, intensidad, temporizadores de transición
- Score: desglose completo de puntuación

MÉTODOS PRINCIPALES:

1. _save_game_snapshot():
   - Serializa estado completo a JSON
   - Incluye timestamp de guardado
   - Maneja errores de escritura
   - Feedback visual al usuario

2. _load_game_snapshot_if_available():
   - Verifica existencia de archivo
   - Deserializa y valida datos
   - Aplica estado a objetos del juego
   - Manejo robusto de errores

3. _serialize_job(job) / _deserialize_job(data):
   - Convierte Job a/desde diccionario
   - Preserva todos los atributos críticos
   - Maneja campos opcionales y tipos

4. _apply_snapshot(snapshot):
   - Restaura estado del courier
   - Reconstruye inventario con heap
   - Restaura temporizadores de clima
   - Vincula trabajos a sesión actual

CONSIDERACIONES ESPECIALES:
- Preservación de session_start para cálculos temporales
- Reconstrucción correcta de estructuras heap
- Validación de integridad de datos
- Limpieza automática de snapshots al finalizar
- Manejo de versiones de formato de guardado

RUTA DE GUARDADO:
- Usar Path relativo: saves/pause_save.json
- Crear directorios automáticamente
- Codificación UTF-8 con ensure_ascii=True
- Formato JSON indentado para debugging
```

## 3. WeatherSimulator - Simulación Climática Dinámica

### Prompt Principal para WeatherSimulator

```
Crea una clase WeatherSimulator que simule clima dinámico realista para un juego de repartidor:

SISTEMA DE TRANSICIONES:
- Cadenas de Markov para cambios climáticos naturales
- Transiciones suaves con interpolación lineal (3-5 segundos)
- Duraciones variables por burst (60 segundos base)
- Estados: clear, clouds, rain_light, rain, storm, fog, wind, heat, cold

MULTIPLICADORES DE VELOCIDAD:
- Clear: 1.00 (sin efecto)
- Clouds: 0.98 (ligera reducción)
- Rain_light: 0.90, Rain: 0.85, Storm: 0.75 (progresivamente más lento)
- Fog: 0.88 (visibilidad reducida)
- Wind: 0.92, Heat: 0.90, Cold: 0.92 (efectos moderados)

TEMPORIZACIÓN AVANZADA:
- burst_start_time: inicio del clima actual
- burst_duration: duración total del burst
- transition_duration: tiempo de cambio suave
- is_transitioning: flag de estado de transición

MÉTODOS PRINCIPALES:

1. update() -> (condition, intensity, multiplier, changed):
   - Verifica si es tiempo de cambio
   - Maneja transiciones en progreso
   - Retorna estado actual y flag de cambio

2. _start_weather_transition():
   - Inicia cambio usando Markov
   - Calcula intensidad objetivo
   - Establece temporizadores de transición

3. _update_transition(current_time) -> progress:
   - Interpola valores durante transición
   - Retorna progreso (0.0-1.0)
   - Actualiza multiplicadores suavemente

4. get_weather_info() -> dict:
   - Información completa para UI
   - Tiempo restante hasta próximo cambio
   - Progreso de transición actual

CONFIGURACIÓN MARKOV:
- Probabilidades de transición por estado actual
- Rangos de intensidad por condición climática
- Duración variable con randomización
- Fallback a condición más probable
```

### Prompt para Lógica de Transiciones Markov

```
Implementa la lógica de cadenas de Markov para WeatherSimulator:

MÉTODO _simulate_weather_change():
- Obtiene probabilidades desde config["transition"][current_condition]
- Usa _markov_transition() para selección probabilística
- Fallback a condición actual si no hay transiciones

MÉTODO _markov_transition(transition_probs):
- Genera número aleatorio [0,1)
- Itera acumulando probabilidades
- Retorna primera condición que supere el umbral
- Fallback a condición con mayor probabilidad

CÁLCULO DE INTENSIDADES:
- Rangos específicos por condición:
  * Clear: (0.0, 0.1) - casi sin intensidad
  * Clouds: (0.1, 0.3) - ligera cobertura
  * Rain_light: (0.3, 0.6) - lluvia moderada
  * Rain: (0.6, 0.9) - lluvia fuerte
  * Storm: (0.8, 1.0) - intensidad máxima
  * Fog: (0.3, 0.5) - densidad media
  * Wind: (0.4, 0.7) - viento variable
  * Heat/Cold: (0.4-0.8) - temperatura extrema

INTERPOLACIÓN SUAVE:
- _interpolate(start, end, progress): start + (end - start) * progress
- Aplicar a intensity y speed_multiplier durante transición
- Progress calculado como elapsed_time / transition_duration
- Clamp progress entre 0.0 y 1.0

EJEMPLO DE CONFIGURACIÓN MARKOV:
```json
{
  "transition": {
    "clear": {"clouds": 0.3, "wind": 0.2, "heat": 0.1},
    "clouds": {"rain_light": 0.4, "clear": 0.3, "fog": 0.2},
    "rain_light": {"rain": 0.3, "clouds": 0.4, "clear": 0.2},
    "rain": {"storm": 0.2, "rain_light": 0.5, "clouds": 0.3}
  }
}
```
```

### Prompt para Integración con Gameplay

```
Integra WeatherSimulator con el sistema de juego para afectar mecánicas:

EFECTOS EN COURIER:
- Actualizar courier.weather en cada cambio
- Modificar stamina_cost según condición climática
- Ajustar move_delay usando speed_multiplier

INTEGRACIÓN EN CONTROLLER:
- Llamar weather_simulator.update() cada frame
- Propagar cambios a courier automáticamente
- Exponer get_weather_info() para UI

SINCRONIZACIÓN TEMPORAL:
- Usar time.time() para consistencia
- Mantener temporizadores independientes del framerate
- Preservar estado en sistema de guardado

MÉTODO get_weather_info() COMPLETO:
```python
{
    "condition": str,           # condición actual
    "intensity": float,         # intensidad 0.0-1.0
    "speed_multiplier": float,  # multiplicador de velocidad
    "is_transitioning": bool,   # en transición
    "time_remaining": float,    # segundos hasta próximo cambio
    "transition_progress": float # progreso de transición actual
}
```

CONFIGURACIÓN INICIAL:
- Leer condición inicial desde weather_config
- Establecer multiplicador base correspondiente
- Inicializar temporizadores con valores aleatorios
- Logging detallado para debugging

MANEJO DE ERRORES:
- Validar configuración al inicializar
- Fallbacks para condiciones no reconocidas
- Clamp de valores fuera de rango
- Recuperación automática de estados inválidos
```

## Prompts de Integración y Optimización

### Prompt para Optimización de Rendimiento

```
Optimiza las tres clases principales (ScoreManager, ViewGame, WeatherSimulator) para rendimiento:

SCOREMANAGER:
- Caché de cálculos de penalizaciones frecuentes
- Lazy evaluation para breakdown.total_points
- Inmutabilidad de objetos retornados para thread-safety
- Batch processing para múltiples eventos simultáneos

VIEWGAME:
- Dirty rectangle rendering para actualizaciones parciales
- Sprite batching para elementos similares
- Audio streaming para efectos largos
- Texture atlasing para reducir draw calls
- Culling de elementos fuera de pantalla

WEATHERSIMULATOR:
- Precálculo de tablas de interpolación
- Caché de multiplicadores por condición
- Reducir frecuencia de update() si no hay cambios
- Pooling de objetos para datos temporales

OPTIMIZACIONES GENERALES:
- Profiling con cProfile para identificar bottlenecks
- Uso de __slots__ en clases de datos frecuentes
- Minimizar allocaciones en loops críticos
- Lazy loading de recursos pesados
```

### Prompt para Testing y Validación

```
Crea suite de tests para validar las tres clases principales:

SCOREMANAGER TESTS:
- Test de cálculo correcto de penalizaciones por rango
- Validación de bono por tiempo restante
- Test de inmutabilidad de breakdowns
- Casos edge: valores negativos, None, overflow

VIEWGAME TESTS:
- Mock de Pygame para testing sin ventana
- Validación de carga/guardado de estado
- Test de manejo de eventos simulados
- Verificación de cleanup de recursos

WEATHERSIMULATOR TESTS:
- Test de transiciones Markov con seed fijo
- Validación de interpolación suave
- Test de sincronización temporal
- Verificación de rangos de intensidad

INTEGRATION TESTS:
- Test de comunicación entre clases
- Validación de estado consistente
- Test de performance bajo carga
- Verificación de memory leaks

HERRAMIENTAS:
- pytest para framework de testing
- unittest.mock para mocking
- pytest-benchmark para performance
- coverage.py para cobertura de código
```

Estos prompts están diseñados para generar código robusto, bien estructurado y optimizado para cada una de las clases principales del proyecto Courier Quest.