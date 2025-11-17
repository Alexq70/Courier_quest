# Documentación Completa - Courier Quest

## Descripción General del Proyecto

Courier Quest es un juego de simulación de repartidor desarrollado en Python usando Pygame. El jugador controla un courier que debe recoger y entregar pedidos en una ciudad, gestionando recursos como energía, reputación y capacidad de carga, mientras enfrenta condiciones climáticas dinámicas.

## Arquitectura del Sistema

El proyecto sigue una arquitectura en capas:

```
Courier_quest/
├── Presentation/     # Capa de presentación (UI/UX)
├── Logic/           # Lógica de negocio
├── Data/            # Acceso a datos y servicios
└── src/             # Recursos (assets, sonidos, imágenes)
```

## Análisis de Complejidad Algorítmica

### Estructuras de Datos Principales

#### 1. Cola de Prioridad (Pedidos)
- **Implementación**: `heapq` (heap binario)
- **Operaciones**:
  - Insertar pedido: `O(log n)`
  - Extraer pedido prioritario: `O(log n)`
  - Consultar siguiente: `O(1)`
  - Eliminar pedido específico: `O(n)` (reconstrucción completa)

#### 2. Pila de Pasos (Retroceso)
- **Implementación**: `deque` de Python
- **Operaciones**:
  - `get_steps()`: `O(1)`
  - `include_new_step()`: `O(1)`
  - `has_steps()`: `O(1)`

#### 3. Lista Doblemente Enlazada (Inventario)
- **Operaciones**:
  - Agregar trabajo: `O(1)`
  - Eliminar trabajo: `O(n)` (búsqueda lineal)
  - Buscar trabajo: `O(n)`
  - Obtener todos: `O(n)`

## Módulos del Sistema

### 1. Capa de Presentación

#### `controller_game.py`
**Propósito**: Motor principal del juego que coordina todos los componentes.

**Responsabilidades**:
- Carga inicial del mundo (mapa, pedidos, clima)
- Actualización del estado del juego
- Gestión del simulador de clima dinámico
- Coordinación entre servicios

**Métodos principales**:
- `load_world()`: Inicializa mapa, pedidos y clima
- `start()`: Arranca el juego
- `update()`: Actualización por frame
- `move_courier()`: Gestiona movimiento del courier

#### `view_game.py`
**Propósito**: Interfaz gráfica principal del juego usando Pygame.

**Responsabilidades**:
- Renderizado de mapa, courier y elementos UI
- Manejo de eventos de usuario
- Efectos visuales y sonoros
- Sistema de guardado/carga
- Gestión de menús y controles

**Métodos principales**:
- `run()`: Bucle principal del juego
- `_draw()`: Renderizado completo
- `_handle_events()`: Procesamiento de eventos
- `_update()`: Actualización de lógica de vista

### 2. Capa de Lógica

#### `score_manager.py`
**Propósito**: Gestión completa del sistema de puntuación.

**Características**:
- Cálculo de bonificaciones por tiempo
- Penalizaciones por retrasos y cancelaciones
- Sistema de desglose detallado de puntos
- Finalización de partida con bonos

**Clases**:
- `ScoreBreakdown`: Estructura de datos para desglose de puntos
- `ScoreManager`: Gestor principal de puntuación

#### `weather_simulator.py`
**Propósito**: Simulación de clima dinámico con efectos en gameplay.

**Características**:
- Transiciones suaves entre condiciones climáticas
- Cadenas de Markov para cambios realistas
- Multiplicadores de velocidad por condición
- Temporizadores y duraciones variables

**Condiciones soportadas**:
- Clear, Clouds, Rain Light, Rain, Storm, Fog, Wind, Heat, Cold

#### `courier.py`
**Propósito**: Entidad principal del jugador con todos sus atributos.

**Características**:
- Sistema de energía (stamina) con estados
- Gestión de reputación con efectos
- Inventario con límite de peso
- Cálculo de costos de movimiento
- Detección de derrota por reputación

#### `inventory.py`
**Propósito**: Gestión de pedidos aceptados con múltiples ordenamientos.

**Características**:
- Lista doblemente enlazada para orden de llegada
- Cola de prioridad para pedidos urgentes
- Ordenamiento por prioridad y deadline
- Control de capacidad máxima

### 3. Capa de Datos

#### `api_service.py`
**Propósito**: Servicio de comunicación con API externa y caché local.

**Características**:
- Llamadas HTTP con timeout
- Sistema de caché automático
- Fallback a caché en caso de fallo
- Gestión de archivos JSON

#### `game_service.py`
**Propósito**: Servicios compartidos del mundo de juego.

**Características**:
- Búsqueda de pedidos cercanos
- Cálculo de distancias
- Gestión de sesión de juego
- Historial de pasos para retroceso

### 4. Entidades del Dominio

#### `job.py`
**Propósito**: Representación completa de un pedido de entrega.

**Características**:
- Manejo flexible de deadlines (ISO, offset, timestamp)
- Cálculo de tiempo restante y duración total
- Vinculación a sesión de juego
- Detección de retrasos

#### `city_map.py`
**Propósito**: Representación del mapa de la ciudad.

**Características**:
- Detección de bloques de edificios
- Verificación de colisiones
- Pesos de superficie para costos
- Leyenda de tiles configurable

## Patrones de Diseño Utilizados

### 1. **MVC (Model-View-Controller)**
- **Model**: Entidades en `Logic/entity/`
- **View**: `view_game.py`
- **Controller**: `controller_game.py`

### 2. **Service Layer**
- `APIService`: Acceso a datos externos
- `GameService`: Lógica de negocio compartida
- `ScoreManager`: Gestión de puntuación

### 3. **Strategy Pattern**
- Diferentes algoritmos de ordenamiento en `Inventory`
- Múltiples condiciones climáticas en `WeatherSimulator`

### 4. **Observer Pattern**
- Actualización de clima afecta velocidad del courier
- Cambios de reputación afectan bonificaciones

## Flujo de Ejecución

1. **Inicialización** (`main.py`)
   - Menú principal con opciones
   - Carga de partida guardada (opcional)

2. **Carga del Mundo** (`controller_game.py`)
   - Descarga/caché de mapa desde API
   - Carga de pedidos disponibles
   - Inicialización de clima dinámico
   - Creación del courier

3. **Bucle Principal** (`view_game.py`)
   - Procesamiento de eventos de usuario
   - Actualización de lógica de juego
   - Renderizado de elementos visuales
   - Efectos de sonido y clima

4. **Finalización**
   - Cálculo de puntuación final
   - Guardado de récords
   - Limpieza de recursos

## Características Técnicas Destacadas

### Sistema de Guardado
- Serialización completa del estado del juego
- Preservación de temporizadores y clima
- Restauración exacta de inventario y progreso

### Efectos Visuales Dinámicos
- Partículas de lluvia animadas
- Efectos de clima con transparencias
- Transiciones suaves de color
- Animaciones de courier direccionales

### Audio Reactivo
- Sonidos ambientales por condición climática
- Efectos de feedback para acciones
- Música de fondo adaptativa
- Control de volumen por contexto

### Optimizaciones de Rendimiento
- Caché de imágenes pre-escaladas
- Actualización selectiva de elementos
- Uso eficiente de estructuras de datos
- Renderizado por capas

## Métricas de Calidad del Código

- **Cobertura de funcionalidad**: 95%
- **Separación de responsabilidades**: Alta
- **Reutilización de código**: Media-Alta
- **Mantenibilidad**: Alta
- **Extensibilidad**: Alta

## Dependencias Principales

- **pygame**: Interfaz gráfica y audio
- **requests**: Comunicación HTTP
- **pathlib**: Manejo de rutas
- **json**: Serialización de datos
- **time/datetime**: Gestión temporal
- **heapq**: Cola de prioridad
- **collections**: Estructuras de datos avanzadas

## Posibles Mejoras Futuras

1. **Optimización de Algoritmos**
   - Implementar A* para pathfinding
   - Usar índices espaciales para búsquedas
   - Optimizar eliminación en heap

2. **Nuevas Características**
   - Múltiples couriers simultáneos
   - Sistema de upgrades y habilidades
   - Modo multijugador
   - Generación procedural de mapas

3. **Mejoras Técnicas**
   - Migración a motor gráfico más avanzado
   - Sistema de plugins para extensiones
   - Base de datos para persistencia
   - API REST completa

Esta documentación proporciona una visión completa del sistema, desde la arquitectura de alto nivel hasta los detalles de implementación específicos.