# Documentacion completa sobre los prompts usados en la segunda version del proyecto CourierQuest

# La estructura de cada prompt esta por: fecha | Prompt usado | Resumen de la respuesta | Modificaciones en el codigo.

06/11/2025 | “Necesito implementar el modo fácil para la IA según las especificaciones del proyecto: elección aleatoria de trabajos, movimiento aleatorio y cambio ocasional de objetivo” |
Resumen de la respuesta:
La IA proporcionó una implementación completa del patrón Strategy para el modo fácil, incluyendo selección aleatoria de trabajos, movimiento aleatorio con persistencia de dirección y un mecanismo de timeout para cambiar de objetivo cuando la IA se estanca. También explicó cómo la clase Ia debía delegar la lógica de decisión en el ConcreteStrategy.
Modificaciones en el código:
    Se implementó la clase EasyMode con los métodos get_next_move(), choose_job() y on_job_delivered(). Además, se adaptó la clase Ia para utilizar correctamente el patrón Strategy sin alterar la lógica principal del juego.

06/11/2025 | “La IA no se mueve en el juego, necesito ayuda para debuggear el problema” |
Resumen de la respuesta:
La IA detectó que el problema no estaba en la clase Ia, sino en la integración entre View_game y controller_game. Aunque la IA se inicializaba correctamente, jamás se llamaba a su actualización periódica. También se revisaron timers e intervalos de actualización.
Modificaciones en el código:
    Se agregó el método _update_ia() dentro de controller_game.update() y se configuró un sistema de temporización usando last_ia_update y ia_update_interval. Esto permitió que la IA recibiera actualizaciones regulares sin modificar otros subsistemas.

06/11/2025 | “Cómo integrar correctamente la IA en el View_game sin romper la funcionalidad existente?” |
Resumen de la respuesta:
La IA recomendó mantener separación clara de responsabilidades: la lógica debe permanecer en controller_game, y View_game debe limitarse a renderizar y ejecutar inputs del usuario. Para evitar conflictos, se propuso mover toda la lógica de IA al método controller_game.update().
Modificaciones en el código:
    Se integró el proceso de actualización de IA dentro de controller_game.update(), manteniendo intactas las funcionalidades de clima, jobs y courier. Se agregaron los métodos auxiliares _ia_pickup_jobs() y _ia_deliver_jobs() para que la IA operara como el jugador humano sin duplicar código.

06/11/2025 | “Recibo error ‘TypeError: < not supported between instances of Job and Job’ al ejecutar el juego con IA” |
Resumen de la respuesta:
La IA identificó que el error provenía del uso de heapq dentro del inventario, ya que Job no tenía métodos de comparación y Python no podía ordenar objetos de esta clase. Se presentaron tres posibles soluciones y se explicó cuál era más segura para la arquitectura actual.
Modificaciones en el código:
    Se añadieron los métodos __lt__ y __eq__ a la clase Job, permitiendo comparaciones seguras basadas en prioridad y deadline. Esto solucionó el problema sin alterar la lógica de inventario ni la mecánica de IA.

07/11/2025 | “Cómo configurar correctamente la IA desde main.py sin causar errores de atributo?” |
Resumen de la respuesta:
La IA detectó que el error provenía del uso de un atributo incorrecto (controller en lugar de engine) y que la IA ya se inicializaba automáticamente en controller_game.load_world(). Configurarla nuevamente en main.py causaba conflictos y referencias inválidas.
Modificaciones en el código:
    Se eliminaron las líneas redundantes de main.py que intentaban configurar la IA manualmente. Se dejó que controller_game manejara completamente la inicialización del jugador IA.

08/11/2025 | “Ocupo agregar una opción más de dificultad” |
Resumen de la respuesta:
La IA propuso un menú interactivo de selección de dificultad compatible con el sistema visual existente. Se agregó retroalimentación al usuario y un flujo simple para seleccionar entre Easy, Normal y Hard.
Modificaciones en el código:
    Se implementó choose_difficulty() con navegación por teclas, se integró al menú principal mediante run_start_menu(), y se agregó un sistema de feedback temporal para mostrar la dificultad seleccionada.

08/11/2025 | “me sale el ‘use arrow keys’ muy arriba” |
Resumen de la respuesta:
La IA detectó que el texto estaba siendo renderizado en una coordenada Y incorrecta. Se analizó la sección de dibujo del menú para ubicar la línea exacta responsable.
Modificaciones en el código:
    Se ajustaron las coordenadas del renderizado:
    screen.blit(instruction, (320 - instruction.get_width() // 2, 400))
    screen.blit(instruction2, (320 - instruction2.get_width() // 2, 430))
    lo que corrigió la alineación visual.

08/11/2025 | “if difficulty: feedback = f'Difficulty set to: {difficulty}' ... quiero que ese texto salga más abajo” |
Resumen de la respuesta:
La IA recomendó no solo ajustar la posición, sino mejorar el sistema de feedback para permitir persistencia del mensaje y evitar parpadeos o superposiciones no deseadas.
Modificaciones en el código:
    Se introdujo la variable global CURRENT_DIFFICULTY, se rediseñó el sistema de feedback para mostrarse en una posición inferior estable y se evitó su borrado inmediato durante el refresco del menú.

08/11/2025 | “Que se mantenga en el menú principal hasta que comience una nueva partida” |
Resumen de la respuesta:
Se explicó cómo la persistencia del estado de dificultad podía mantenerse durante toda la ejecución, sin necesidad de mensajería transitoria.
Modificaciones en el código:
    choose_difficulty() fue adaptado para recordar la dificultad seleccionada. También se añadió un texto permanente debajo del título del menú:
    "Current Difficulty: {dificultad}"

08/11/2025 | “Ayudame en esta clase ViewGame.py” |
Resumen de la respuesta:
La IA integró el sistema de dificultad del menú principal con los modos existentes de IA, explicando cómo mapear cada nivel de dificultad a la lógica interna.
Modificaciones en el código:
    Se añadió soporte para difficulty en el constructor de View_game, se implementó difficulty_map = {"Easy":1, "Normal":2, "Hard":3}, y se invocó engine.ia.set_mode() correctamente.

08/11/2025 | “Traceback: TypeError: cannot unpack non-iterable NoneType object”
Resumen de la respuesta:
La IA identificó que el error provenía de un movimiento inválido o un retorno None dentro del flujo de IA. Se explicó cómo la vista debía validar los movimientos recibidos.
Modificaciones en el código:
    Se reforzó _update_ia() con validaciones de coordenadas, manejo de errores, logs de debugging y ajustes dinámicos de velocidad basados en dificultad (0.5s Easy, 0.3s Normal, 0.2s Hard).

|08/11/2025 | "Tengo dos problemas: uno que cuando sale el pedido se pierde la cuadrícula y dos que el jugador IA solo pasa al norte de la pantalla, agarra dos pedidos y ya" |
Resumen de la respuesta: La IA identificó que ambos problemas requerían análisis de múltiples clases. Para el problema de la cuadrícula, se enfocó en el renderizado del mapa en view_game.py. Para el problema de la IA, detectó que la lógica de movimiento en ia.py tenía direcciones invertidas y comportamiento errático.

Modificaciones en el código:
    Se solicitó revisión de view_game.py, controller_game.py, city_map.py, ia.py, game_service.py y courier.py para diagnóstico completo.

|09/11/2025 | "Revisa el código de view_game, controller_game, city_map, ia, game_service y courier que te pasé" |
Resumen de la respuesta: La IA detectó problemas críticos en tres áreas: 1) En city_map.py el método is_blocked() retornaba una tupla en lugar de bool, 2) En ia.py el método obtain_movement() tenía las direcciones invertidas, 3) En view_game.py el método _update_ia() recalculaba dx/dy incorrectamente.

Modificaciones en el código:

    city_map.py: Corrección de return "blocked",False a return False

    ia.py: Inversión de direcciones en obtain_movement()

    view_game.py: Eliminación del recálculo de dx/dy en _update_ia()

|09/11/2025 | "Podríamos hacer lo siguiente: la matriz está por letras, los edificios no pueden ser visitados, podríamos estar recalculando las rutas solo por las calles?" |
Resumen de la respuesta: La IA implementó un sistema de navegación inteligente que solo considera celdas de tipo 'C' (calles) y 'P' (parques) como válidas para el movimiento. Esto previene que la IA incluso intente moverse hacia edificios.

Modificaciones en el código:

    ia.py: En easy_mode() se agregó filtro para direcciones válidas usando citymap.tiles[new_y][new_x] in ['C', 'P']

    Se mantuvo la verificación de colisiones en move_ia() como capa de seguridad adicional


08/11/2025 | “Hola, estoy intentando agregar un jugador IA a mi juego pero no se mueve, ¿podés ayudarme?” |
Resumen de la respuesta:
La IA explicó qué clases intervenían en el movimiento (Ia, controller_game y view_game) y determinó que la IA no avanzaba porque next_movement_ia() no devolvía un movimiento válido para la vista. También se detectó que view_game estaba invocando incorrectamente el método, pasando argumentos que no correspondían.
Modificaciones en el código:
    No se alteró la lógica interna; únicamente se corrigió la forma en que view_game llamaba a next_movement_ia(), asegurando que recibiera correctamente la tupla (movimiento, coordenada) y evitando enviar parámetros inválidos.


08/11/2025 | “Me puedes dar un método como easy_mode pero que solo se mueva aleatoriamente y revise los pedidos, es para probar si la logica de la IA esta funcionando?” |
Resumen de la respuesta:
La IA generó un easy_mode(jobs) más completo, explicando cómo combinar movimientos aleatorios con una ligera tendencia hacia un pedido cercano, sin modificar lógica existente. Se detalló cómo obtener las posiciones de pickup sin romper la estructura actual.
Modificaciones en el código:
    Se mejoró easy_mode para aceptar la lista de jobs, leer la posición del pickup y seleccionar una dirección adecuada. No se cambió la lógica de movimiento de la IA; solo se ajustó el valor retornado para mantener compatibilidad con next_movement_ia().

09/11/2025 | “La IA se mueve pero no agarra ningún pedido, ¿qué está pasando?” |
Resumen de la respuesta:
La IA explicó que easy_mode únicamente genera movimiento y que el problema era que la IA nunca ejecutaba la lógica de recogida de pedidos. Se identificó que _pickup_job_ia() no se estaba llamando después de mover a la IA, por lo que nunca se detectaba cuando llegaba a un pickup. También se encontró que job_nearly_ia() estaba siendo invocado con parámetros incorrectos.
Modificaciones en el código:
    Se ajustó _update_ia para llamar _pickup_job_ia() inmediatamente después de move_ia(). Asimismo, se corrigió la invocación a job_nearly_ia() para que no recibiera argumentos indebidos.

09/11/2025 | “Me da este error: ‘AttributeError: list object has no attribute pickup_position’, ¿qué hago?” |
Resumen de la respuesta:
La IA explicó que el error surgía porque se estaba enviando accidentalmente una lista completa al método next_movement_ia() en lugar de un solo objeto Job. Por eso Python trataba a la lista como si fuera un Job y fallaba al buscar pickup_position. Se aclaró la diferencia entre enviar listas versus objetos individuales y cómo identificar este tipo de errores.
Modificaciones en el código:
    Se reemplazó la llamada incorrecta next_movement_ia([nearest_job]) por next_movement_ia(nearest_job) dentro de _update_ia(). 
    Además, se recomendó validar dentro de next_movement_ia() si el parámetro es lista u objeto, sin modificar la lógica central del sistema.






















# Ultimos prompts

| 11/11/2025 | "Necesito implementar docstrings completos para todas las clases del proyecto Courier Quest siguiendo un formato específico" |
Resumen de la respuesta: La IA se comprometió a crear docstrings completos para métodos que no los tuvieran, respetando los existentes y manteniendo intacta la lógica del código. Se estableció el formato a seguir: descripción, parámetros y retornos.

Modificaciones en el código: Se implementaron docstrings iniciales para GameService, ScoreRepository y CityMap, estableciendo el estándar de documentación para todo el proyecto.

| 12/11/2025 | "Implementar docstrings para las entidades principales: Courier, Ia e Inventory" |
Resumen de la respuesta: La IA documentó exhaustivamente las clases centrales del dominio, incluyendo métodos de movimiento, gestión de inventario y lógica de IA. Se mantuvo coherencia en la descripción de parámetros y valores de retorno.

Modificaciones en el código: Se añadieron docstrings para 15+ métodos entre Courier e Ia, documentando especialmente la lógica de movimientos, stamina y los tres modos de IA (fácil, medio, difícil).

| 13/11/2025 | "Documentar el sistema de jobs y weather con todos sus métodos de cálculo temporal" |
Resumen de la respuesta: Se documentó la compleja lógica de manejo de tiempos en la clase Job, incluyendo parsing de deadlines, cálculos de timestamps y gestión de sesiones. También se documentó WeatherBurst.

Modificaciones en el código: Se implementaron docstrings para métodos críticos como _parse_deadline, _compute_deadline_timestamp, get_total_duration y is_overdue, esenciales para la simulación temporal del juego.

| 15/11/2025 | "Completar documentación del sistema de puntuación y simulación climática" |
Resumen de la respuesta: La IA documentó el ScoreManager con su sistema de penalizaciones y bonificaciones, y el WeatherSimulator con transiciones Markovianas y efectos visuales.

Modificaciones en el código: Se añadieron docstrings para register_delivery, register_cancellation, finalize en ScoreManager, y para el sistema completo de transiciones climáticas en WeatherSimulator.

| 16/11/2025 | "Documentar el controlador principal y la vista de PyGame" |
Resumen de la respuesta: Se documentó el controller_game que orquesta todo el sistema, y la extensa clase View_game con toda la lógica de renderizado, sonidos y gestión de estados de UI.

Modificaciones en el código: Se implementaron 40+ docstrings para View_game, cubriendo desde carga de assets hasta efectos climáticos visuales, sistema de guardado y gestión del bucle principal.

| 17/11/2025 | "Finalizar documentación con el sistema de menús y función principal" |
Resumen de la respuesta: La IA completó la documentación con los menús de inicio, selección de dificultad y entrada de nickname, cerrando el ciclo completo de documentación del proyecto.

Modificaciones en el código: Se añadieron docstrings para run_start_menu, run_difficulty_menu, prompt_for_name y main, documentando el flujo completo de la aplicación desde el inicio hasta la ejecución del juego.
