# Courier_quest
Algoritmos y complejidad algortimica: 

Estructuras usadas: 

Cola de prioridad en pedidos:
La cola de prioridad de los pedidos en el proyecto utiliza heapq, que implementa un heap binario.
Las operaciones principales tienen las siguientes complejidades:

Insertar un pedido (heappush): O(log n)
Extraer el pedido de mayor prioridad (heappop): O(log n)
Consultar el siguiente pedido (heap[0]): O(1)
Eliminar un pedido arbitrario (reconstruyendo el heap): O(n)
Esto significa que agregar y extraer pedidos es eficiente incluso con muchos elementos, pero eliminar un pedido específico requiere recorrer toda la estructura y reconstruir el heap, lo que es menos [...]

Para retroceder en los pedidos: 
```Python
    def get_steps(self):
        if self.pila: 
            return self.pila.pop()
        return (0, 0) 
    
    def include_new_step(self,pos):
        self.cola.append(pos)
    
    def has_steps(self):
        return len(self.pila) > 0
```
    Todos son de O(1)

[Documentación Completa](./src/DOCS/)

---

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