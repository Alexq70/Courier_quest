# Courier_quest

# Informacion Importante
# Se debe descargar la version de la rama ALEXX, ya que este contiene la version final
# El juego inicia desde la clase main.py ubicada en la carpeta Courier_quest



# Algoritmos y Complejidad Algorítmica

El proyecto incorpora varias estructuras de datos diseñadas para optimizar el manejo de trabajos (jobs), la navegación del jugador y de la IA, así como la administración de estados internos como stamina, inventario y retrocesos de movimiento. A continuación se detalla el análisis algorítmico de las estructuras principales utilizadas.

# Cola de Prioridad en la Gestión de Pedidos

Para la administración de los pedidos activos, el proyecto utiliza una cola de prioridad implementada con heapq, la cual funciona internamente como un heap binario mínimo. Esta estructura permite organizar los pedidos según criterios como prioridad, urgencia o distancia, garantizando siempre el acceso rápido al elemento más importante. Las operaciones fundamentales mantienen una alta eficiencia: insertar un pedido mediante heappush() tiene un coste de O(log n), lo que asegura un proceso rápido incluso cuando el número de pedidos crece significativamente. De igual forma, extraer el pedido de mayor prioridad con heappop() también requiere O(log n), manteniendo un rendimiento consistente. La consulta del siguiente pedido a procesar es inmediata, ya que acceder al primer elemento del heap cuesta únicamente O(1). Sin embargo, la eliminación de un pedido arbitrario —cuando es necesario retirarlo del sistema sin seguir el orden de prioridad— implica recorrer y reconstruir la estructura, alcanzando un coste de O(n), siendo esta la operación menos eficiente dentro del sistema. Aun así, dado que la mayoría de interacciones sobre los pedidos consisten en agregarlos o extraerlos en orden de prioridad, el uso de un heap binario resulta ideal y adecuado para el rendimiento general del juego.

# Gestión del Historial de Pasos (Backtracking) 

El sistema incorpora un mecanismo simple pero eficiente para almacenar y recuperar movimientos previos del jugador o la IA, permitiendo funcionalidades como retroceso o análisis del recorrido. Esta funcionalidad se implementa mediante dos estructuras lineales: una pila (pila) y una cola (cola). La pila se utiliza para registrar los pasos en orden LIFO, lo que permite recuperar el movimiento más reciente con una operación constante. Por su parte, la cola almacena nuevos movimientos en orden FIFO cuando se requiere un registro secuencial. Las tres operaciones fundamentales de este módulo —obtener el último paso, almacenar un nuevo paso y verificar si existen pasos almacenados— tienen un coste constante de O(1), lo que garantiza un rendimiento óptimo incluso durante un uso intensivo del sistema. Esto permite que la mecánica de retroceso sea inmediata y no genere impacto perceptible en el desempeño general del juego.

Código utilizado en esta estructura
        def get_steps(self):
            if self.pila: 
                return self.pila.pop()
            return (0, 0) 

        def include_new_step(self, pos):
            self.cola.append(pos)

        def has_steps(self):
            return len(self.pila) > 0

# Estructuras de Datos Utilizadas en los Modos de IA (Fácil, Medio y Difícil)

Los tres modos de la Inteligencia Artificial implementados en el juego —Fácil, Medio y Difícil— se basan en una serie de estructuras de datos eficientes que permiten decidir movimientos, seleccionar pedidos y navegar el mapa sin comprometer el rendimiento general del sistema. Aunque cada modo aplica estrategias distintas, todos comparten un conjunto común de estructuras optimizadas que garantizan un comportamiento coherente y estable en la IA.

# Lista de Pedidos Activos (jobs)

Los tres modos operan a partir de la lista de pedidos disponibles en el juego, la cual se recibe como un argumento externo. Esta lista permite:

    Seleccionar un pedido candidato (al azar o por heurísticas)
    Consultar posiciones de pickup o entrega
    Aplicar búsquedas simples si el modo de IA lo requiere

Razones para usar una lista:

    Acceso por índice: O(1)
    Selección aleatoria: O(1)
    Iteraciones controladas en modo medio/difícil: O(n) en el peor caso

Esto hace que la estructura sea flexible y eficiente para los tres niveles de complejidad.

# Representación de Coordenadas con Tuplas (x, y)

La IA utiliza tuplas para representar:

    Posición actual
    Posiciones objetivo
    Vectores de movimiento
    Puntos de pickup o entrega

    Ejemplo típico:

    (current_x, current_y)
    (new_x, new_y)
    (dx, dy)


Ventajas:

    Son inmutables, lo que evita inconsistencias.
    Tienen acceso y comparación O(1).
    Son ligeras y representan de forma natural el sistema de cuadrícula del mapa.
    Los tres modos (fácil, medio, difícil) se benefician por igual de esta representación simple y eficiente.

# Listas de Direcciones de Movimiento

Independientemente del modo, la IA utiliza una lista estática de direcciones cardinales para desplazarse:

    directions = [(-1,0), (1,0), (0,-1), (0,1)]


Esta estructura permite:

    Seleccionar un movimiento aleatorio (modo fácil)
    Evaluar caminos o restricciones de movimiento (modo medio)
    Simular decisiones más tácticas (modo difícil)
    Complejidad: O(1) para elegir o recorrer estas direcciones.

# Lectura Dinámica de Atributos del Objeto Job

Los modos de IA deben obtener información del pedido asociado, como:

    Posición de recogida
    Posición de entrega
    Peso o prioridad (dependiendo del modo)

Como los pedidos pueden tener distintas formas según el módulo en el que se definan, la IA utiliza evaluaciones genéricas:

    if hasattr(job, "pickup_position"):
        ...
    elif hasattr(job, "pickup"):
        ...
    elif hasattr(job, "get_pickup_position"):
        ...

Beneficios:

    Flexibilidad ante diferentes implementaciones de Job.
    Operaciones O(1) al leer los atributos.
    Evita errores si la estructura del pedido cambia.


# Aleatoriedad Controlada y Selección Probabilística

Los métodos de IA combinan elementos estocásticos como:

    random.choice(jobs)
    random.random()

Esto permite:

    Comportamiento natural e impredecible (modo fácil)
    Resolución de empates o dudas en decisiones (modo medio)
    Pequeñas desviaciones del movimiento óptimo (modo difícil)
    Estas operaciones tienen complejidad constante O(1) y aportan fluidez sin aumentar costo computacional.

# Uso de Temporizadores Internos para Control de Movimiento

Los modos de IA utilizan variables internas como:

    move_timer
    move_delay
    ia_move_timer

Estas estructuras definen la frecuencia con que la IA puede actuar, evitando:

    Movimientos demasiado rápidos
    Sobrecarga en el game loop
    Desincronización con el jugador
    Aunque no son estructuras de datos como tal, sí forman parte clave de la arquitectura de decisión.


[Documentación Completa sobre prompts](./src/DOCS/)