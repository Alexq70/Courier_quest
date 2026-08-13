# Courier_quest
## Resumen del proyecto

Courier Quest es un juego/simulador en Python que modela la entrega de pedidos por mensajería y permite explorar algoritmos y estructuras de datos aplicados al problema (colas de prioridad, gestión de pasos, simulación de clima y cálculo de puntuación). Está pensado para quien quiera estudiar o probar estrategias de despacho y la interacción entre clima, rutas y pedidos.

### Stack
- Lenguaje: Python 3
- Runtime: CPython (sin framework web explícito)
- Librerías notables: heapq (cola de prioridad). La interfaz gráfica parece usar una librería como pygame; revisa los imports en `Courier_quest/Presentation/view_game.py` y `controller_game.py` para confirmar las dependencias exactas.

### Organización (alto nivel)
- `Courier_quest/` — paquete principal con el punto de entrada `main.py`.
- `Courier_quest/Logic/` — motor del juego: entidades, simulador de clima y gestión de puntuaciones (`score_manager.py`, `weather_simulator.py`, `Logic/entity/*`).
- `Courier_quest/Presentation/` — capa de presentación: controlador, pathfinder y vista (`controller_game.py`, `pathfinder.py`, `view_game.py`).
- `saves/`, `scores.json`, `api_cache/`, `src/assets/` — datos, persistencia y recursos auxiliares.

### Cómo ejecutar (rápido)
1. Crear un entorno virtual e instalar dependencias necesarias (revisar imports en `Presentation/view_game.py` y `controller_game.py`).
2. Ejecutar el punto de entrada:

```
python3 Courier_quest/main.py
```

Si la interfaz gráfica usa pygame u otra librería, instálala antes con `pip install <paquete>`.

---

Si quieres, puedo añadir instrucciones más detalladas (requisitos exactos, ejemplos de configuración, o una sección de Contribución) directamente al README.
