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
Esto significa que agregar y extraer pedidos es eficiente incluso con muchos elementos, pero eliminar un pedido específico requiere recorrer toda la estructura y reconstruir el heap, lo que es menos eficiente.

Para retroceder en los pedidos: 

    def get_steps(self):
        if self.pila: 
            return self.pila.pop()
        return (0, 0) 
    
    def include_new_step(self,pos):
        self.cola.append(pos)
    
    def has_steps(self):
        return len(self.pila) > 0

    Todos son de O(1)