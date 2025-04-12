# JUGADOR DE HEX CON IA

Este repositorio contiene implementaciones de algoritmos de Inteligencia Artificial para el juego Hex.

En la carpeta **utils** se encuentran otros jugadores de IA con distintos algoritmos. Estos están implementados para competir entre sí y así evaluar cuáles ofrecen los mejores resultados.

La implementación más destacada es **MonteCarloHexPlayer**, ubicada en el archivo **best_players.py**. Se ha demostrado que es el jugador más competitivo, por lo que DEBE SER EL UTILIZADO en la competición.

## Estructura del repositorio

- **best_players.py**: Implementación del jugador _MonteCarloHexPlayer_ que utiliza una combinación de MCTS y RAVE.
- **hex_match.py**: Script para ejecutar partidas y torneos entre los jugadores de IA.
- **basic_classes.py**: Definiciones básicas para el juego (por ejemplo, clases de tablero y jugador).
- **utils/**: Contiene otros jugadores de IA implementados con distintos algoritmos para evaluar su rendimiento.

## Cómo utilizar

Para ejecutar una partida o torneo de Hex, utilice el script `hex_match.py`. Asegúrese de que la implementación de **MonteCarloHexPlayer** sea la que se utiliza en la competición para obtener los mejores resultados.

## Cómo funciona MonteCarloHexPlayer

La clase **MonteCarloHexPlayer** (definida en _best_players.py_) implementa un algoritmo de búsqueda basado en MCTS (Monte Carlo Tree Search) combinado con el método RAVE para mejorar la estimación de los movimientos.

El funcionamiento detallado es el siguiente:

1. **Inicialización del Árbol y Control de Tiempo**

   - Se crea una raíz "dummy" a partir de una copia del tablero (usando el método `clone()`).
   - La raíz se inicializa sin movimiento asignado y se le asigna como jugador el opuesto a `self.player_id`, para que el siguiente movimiento sea del jugador real.
   - El proceso de búsqueda se ejecuta dentro de un bucle que dura hasta alcanzar el límite de tiempo (definido en `self.time_limit`).

2. **Fase de Selección**

   - Desde la raíz, se recorre el árbol utilizando la función `best_child()`, que combina la tasa de victoria del nodo con las estadísticas RAVE y un término de exploración basado en UCT.
   - Esta traversa se realiza mientras el nodo actual esté completamente expandido (es decir, no tenga movimientos sin probar) y posea nodos hijos.

3. **Fase de Expansión**

   - Si en el nodo actual aún hay movimientos sin explorar (`untried_moves`), se selecciona uno al azar.
   - Se aplica el movimiento al tablero (utilizando `place_piece`) para generar un nuevo estado, y se crea un nodo hijo que representa este movimiento.
   - El movimiento se elimina del listado de movimientos por probar en el nodo padre.

4. **Fase de Simulación (Rollout)**

   - Desde el nuevo estado, se realiza una simulación aleatoria completa del juego mediante la función `rollout()`.
   - Durante la simulación, se registran los movimientos y los jugadores que los realizaron, hasta que se detecta un ganador (o se agotan los movimientos).

5. **Fase de Backpropagation**

   - Al finalizar la simulación, se recorre el árbol desde el nodo terminal hasta la raíz.
   - En cada nodo se actualizan:
     - El número de visitas (`visits`).
     - El número de victorias (`wins`), incrementado si el jugador en ese nodo ganó la partida simulada.
     - Las estadísticas RAVE, que registran para cada movimiento la cantidad de veces que ha sido jugado y cuántas veces ha conducido a una victoria.

6. **Selección del Mejor Movimiento**
   - Una vez agotado el tiempo de simulación, se selecciona el hijo de la raíz con el mayor número de visitas.
   - Este movimiento se retorna como el movimiento elegido para la jugada actual.

Esta combinación de MCTS y RAVE permite que **MonteCarloHexPlayer** explore el árbol de juego de manera eficiente y utilice información compartida entre ramas para estimar la calidad de los movimientos, logrando resultados muy competitivos en el juego Hex.

¡Disfrute de la experiencia y que gane el mejor!
