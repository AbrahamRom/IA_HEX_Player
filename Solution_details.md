# Teoría Detrás de la Solución de un Jugador de Hex con MCTS y RAVE

La solución del jugador de Hex con MCTS y RAVE se apoya en dos técnicas principales: la búsqueda Monte Carlo Tree Search (MCTS) y la mejora conocida como Rapid Action Value Estimation (RAVE). A continuación se desglosa la teoría detrás de cada componente y cómo se integran para generar un agente competitivo.

---

## 1. Búsqueda Monte Carlo Tree Search (MCTS)

La MCTS es un método de búsqueda utilizado ampliamente en juegos de información perfecta como Hex o Go. Su fortaleza radica en no requerir una heurística de evaluación específica, sino en emplear simulaciones aleatorias (rollouts) para estimar la calidad de los movimientos. El algoritmo se divide en cuatro fases principales:

### a. **Selección**

- **Objetivo:**  
  Partiendo de la raíz (estado actual del juego), se desciende por el árbol de búsqueda seleccionando en cada paso el hijo que maximice una fórmula de equilibrio entre exploración y explotación.
- **Técnica:**  
  Utiliza la ecuación UCT (Upper Confidence Bound for Trees), que combina:
  - **Explotación:** Basada en la tasa de victorias del nodo, es decir, si un nodo ha demostrado buenos resultados en simulaciones anteriores.
  - **Exploración:** Se añade un término que favorece a nodos menos explorados (con pocas visitas), garantizando la prueba de jugadas nuevas y potencialmente efectivas.
- **Resultado:**  
  Se avanza por el árbol hasta llegar a un nodo que no esté completamente expandido o que represente un estado terminal.

### b. **Expansión**

- **Objetivo:**  
  Al alcanzar un nodo con movimientos no explorados, se expande el árbol creando un hijo que corresponde a uno de estos movimientos.
- **Técnica:**  
  Se selecciona aleatoriamente (o con otro criterio) uno de los movimientos no probados y se crea un nuevo nodo a partir del estado resultante, clonando el tablero y aplicando el movimiento.
- **Resultado:**  
  Se añade un nuevo nodo al árbol que representa una posible jugada.

### c. **Simulación (Rollout)**

- **Objetivo:**  
  Desde el estado del nuevo nodo, se simula una partida completa de forma aleatoria hasta alcanzar un estado terminal (por ejemplo, cuando un jugador completa la conexión ganadora en Hex).
- **Técnica:**  
  Durante el rollout se registra toda la secuencia de jugadas (incluyendo el jugador que las ejecuta). Este registro es crucial para la actualización de estadísticas RAVE.
- **Resultado:**  
  Se obtiene el ganador de la simulación (o en casos excepcionales, un empate) y se registra la secuencia de movimientos realizados.

### d. **Backpropagation**

- **Objetivo:**  
  Actualizar las estadísticas del árbol (nodos y movimientos) de acuerdo con el resultado de la simulación.
- **Técnica:**  
  Se retrocede desde el nodo de la simulación hasta la raíz, actualizando en cada nodo:
  - **Visitas:** Incremento del contador de visitas.
  - **Victorias:** Incremento del contador de victorias si el jugador asociado al nodo es el ganador.
  - **RAVE:** Actualización de las estadísticas RAVE para cada movimiento registrado en la secuencia de la simulación.
- **Resultado:**  
  Se refuerzan las estadísticas en cada nodo, integrando información tanto local (directa del nodo) como global (movimientos presentes en la simulación).

---

## 2. Rapid Action Value Estimation (RAVE)

RAVE es una mejora para la MCTS que aprovecha la información de las simulaciones de manera más eficiente, especialmente útil cuando el árbol es muy extenso.

### a. **Información Compartida de Acciones**

- **Idea Central:**  
  En MCTS tradicional, solo se actualizan las estadísticas de un nodo basado en las simulaciones que han pasado directamente por él. Sin embargo, RAVE permite aprovechar la utilidad de jugadas que, aunque no fueron elegidas directamente en un nodo particular, aparecen frecuentemente en rollouts.
- **Implementación:**  
  Se almacenan estadísticas globales para cada acción en cada nodo, en forma de:
  - Número de veces que el movimiento apareció en una simulación.
  - Número de veces que dicho movimiento condujo a una victoria.

### b. **Integración en la Fórmula UCT**

- **Combinación de Valores:**  
  Para cada nodo hijo, se calcula una combinación ponderada de:
  - **El win rate directo del nodo:** Basado en visitas y victorias específicas.
  - **El valor RAVE:** Basado en las estadísticas agregadas del movimiento en diversas simulaciones.
- **Fórmula:**  
  La combinación se realiza mediante un factor beta:

$$
\text{Valor combinado} = (1 - \beta) \times \text{win rate} + \beta \times \text{RAVE win rate} + \text{término de exploración}
$$

donde $\beta$ se define típicamente como:

$$
\beta = \sqrt{\frac{\text{rave\_constant}}{3 \times \text{visitas del nodo} + \text{rave\_constant}}}
$$

- **Interpretación:**  
  Al inicio, con pocas visitas, $\beta$ es alto, otorgando mayor peso a las estadísticas RAVE. Conforme el nodo se explora más, el win rate específico gana relevancia y $\beta$ disminuye.

### c. **Ventajas de RAVE**

- **Convergencia Más Rápida:**  
  Al utilizar información global de las simulaciones, se identifican jugadas prometedoras más tempranamente, evitando la exploración excesiva de opciones subóptimas.
- **Eficiencia en la Búsqueda:**  
  Movimientos efectivos, al aparecer repetidamente en diferentes contextos, aceleran la convergencia del algoritmo hacia decisiones óptimas.

---

## 3. Integración en la Implementación

La solución implementada integra MCTS y RAVE de la siguiente manera:

- **Selección:**  
  Se utiliza un método `best_child()` que combina la fórmula UCT tradicional con el componente RAVE. Esto permite elegir la rama a explorar basándose en estadísticas locales y globales.

- **Expansión y Simulación:**

  - Se clona el estado del juego (para no afectar el tablero original) y se expande el árbol mediante movimientos no explorados.
  - Durante la simulación, se registra la secuencia de movimientos (junto con el jugador que los realizó), lo que es esencial para la actualización RAVE.

- **Backpropagation:**

  - Se retrocede desde el nodo hoja hasta la raíz, actualizando tanto las estadísticas tradicionales (visitas y victorias) como las estadísticas RAVE en cada nodo.
  - Esta actualización conjunta refuerza la toma de decisiones basadas en información agregada de múltiples simulaciones.

- **Control por Tiempo:**  
  El uso de un límite de tiempo para iterar las simulaciones asegura que el algoritmo se ajuste a las restricciones del juego en tiempo real, ejecutando tantas iteraciones como sea posible dentro del plazo disponible.

---

## Conclusión

La integración de MCTS y RAVE permite construir un agente para Hex que es robusto y eficiente:

- **Balance entre exploración y explotación:**  
  La fórmula UCT+RAVE combina datos locales (de nodos específicos) y globales (de simulaciones generales) para guiar la búsqueda.
- **Identificación temprana de jugadas fuertes:**  
  RAVE acelera la convergencia hacia las mejores decisiones aprovechando información compartida de las simulaciones.
- **Diseño modular y escalable:**  
  La clara separación entre las fases de MCTS (selección, expansión, simulación y backpropagation) facilita la comprensión, el mantenimiento y la extensión del algoritmo.

En resumen, el uso combinado de MCTS y RAVE en la solución del jugador de Hex resulta en un agente que toma decisiones informadas y eficientes, adaptándose a condiciones de tiempo real y maximizando el rendimiento en juegos complejos.
