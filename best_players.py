import random
import time
import math
from copy import deepcopy  # Para la clonación del tablero
from hexboard import (
    HexBoard,
)  # Asegúrate de que esta clase esté definida en hexboard.py
from basic_classes import (
    Player,
)  # Asegúrate de que esta clase esté definida en basic_classes.py


# Se asume que la clase HexBoard tiene los métodos:
# - clone(): copia profunda del tablero.
# - get_possible_moves(): retorna una lista de (fila, columna) de casillas vacías.
# - place_piece(row, col, player_id): coloca la ficha si la casilla está vacía.
# - check_connection(player_id): retorna True si el jugador logra la conexión ganadora.


# ------------------------------
# Clase para los nodos del árbol MCTS con RAVE
# ------------------------------
class TreeNode:
    def __init__(self, board: "HexBoard", move: tuple, parent: "TreeNode", player: int):
        """
        board: estado del tablero en este nodo.
        move: movimiento que se realizó para llegar a este nodo (None para la raíz).
        parent: nodo padre (None para la raíz).
        player: identificador del jugador que realizó el movimiento en este nodo.
                (NOTA: en la raíz se asigna el jugador que *jugó* el movimiento previo;
                de esta manera, el siguiente movimiento en la expansión lo hará self.player_id)
        """
        self.board = board  # Estado del tablero en este nodo
        self.move = move  # Movimiento (fila, col) aplicado para llegar a este nodo
        self.parent = parent
        self.player = player  # El jugador que realizó el movimiento en este nodo

        # Estadísticas para la MCTS tradicional:
        self.visits = 0
        self.wins = 0.0  # Número de simulaciones ganadoras (desde la perspectiva del jugador que movió en este nodo)

        # Diccionarios para almacenar estadísticas RAVE para movimientos:
        # Para cada movimiento (casilla) se almacenan:
        #   rave_visits[move]: cantidad de veces que dicho movimiento apareció en la simulación
        #   rave_wins[move]: cantidad de veces que dicho movimiento condujo a una victoria para el jugador de la simulación
        self.rave_visits = {}
        self.rave_wins = {}

        # Movimientos que aún no se han probado desde este nodo:
        self.untried_moves = board.get_possible_moves()

        # Los hijos se almacenarán en un diccionario: move -> TreeNode
        self.children = {}

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, exploration=math.sqrt(2), rave_constant=300):
        """Selecciona el mejor hijo usando una combinación UCT + RAVE.

        La fórmula es:
          UCT+RAVE = estimated_value + exploration_term
        donde:
          - estimated_value es una combinación (ponderada por beta) entre la tasa de victoria
            del nodo y la tasa RAVE para ese movimiento.
          - beta se calcula como: beta = sqrt(rave_constant / (3 * node_visits + rave_constant))
        """
        best_value = -float("inf")
        best_child = None
        # Nota: usamos las estadísticas RAVE que están almacenadas en este nodo (como padre)
        for move, child in self.children.items():
            # Si el hijo no ha sido visitado, le damos un valor muy alto para favorecer su exploración.
            if child.visits == 0:
                uct_rave_val = float("inf")
            else:
                # Tasa de victoria MCTS tradicional en el hijo.
                win_rate = child.wins / child.visits

                # Obtención de las estadísticas RAVE para el movimiento aplicado en el hijo.
                # Las estadísticas RAVE se almacenan en el nodo padre respecto a los movimientos
                # que se han visto en simulaciones posteriores.
                rave_visits = self.rave_visits.get(move, 0)
                rave_wins = self.rave_wins.get(move, 0)
                rave_win_rate = rave_wins / rave_visits if rave_visits > 0 else 0

                beta = math.sqrt(rave_constant / (3 * child.visits + rave_constant))
                # Combinamos la tasa MCTS y la tasa RAVE:
                estimated_value = (1 - beta) * win_rate + beta * rave_win_rate
                # Término de exploración (usamos logaritmo de visitas del padre)
                exploration_term = exploration * math.sqrt(
                    math.log(self.visits) / child.visits
                )
                uct_rave_val = estimated_value + exploration_term

            if uct_rave_val > best_value:
                best_value = uct_rave_val
                best_child = child
        return best_child


# ------------------------------
# Función de simulación (rollout) con registro de movimientos y quién los jugó.
# ------------------------------
def rollout(board: "HexBoard", current_player: int) -> tuple[int, list]:
    """
    Realiza una simulación (random playout) a partir del estado actual del tablero.

    Retorna:
      - winner: el identificador del jugador ganador.
      - sim_moves: una lista de tuplas (move, player) indicando el movimiento y el jugador que lo realizó.
    """
    sim_moves = []
    # Se trabaja con una copia del tablero para no alterar el estado real.
    sim_board = board.clone()
    while True:
        possible_moves = sim_board.get_possible_moves()
        if not possible_moves:
            # Sin movimientos posibles (caso excepcional)
            break
        move = random.choice(possible_moves)
        sim_board.place_piece(move[0], move[1], current_player)
        sim_moves.append((move, current_player))
        # Si el jugador actual ha ganado, se termina la simulación.
        if sim_board.check_connection(current_player):
            return current_player, sim_moves
        # Alternamos jugadores: si es 1 pasa a 2, y viceversa.
        current_player = 3 - current_player
    # En caso de empate (muy poco probable en HEX), se devuelve None
    return None, sim_moves


# ------------------------------
# Función para actualizar las estadísticas RAVE en el camino de backpropagation.
# ------------------------------
def update_rave(node: TreeNode, sim_moves: list, winner: int):
    """
    Para cada nodo en el camino (cada nodo en el árbol que participó en esta simulación),
    se actualizan las estadísticas RAVE: para cada movimiento (jugado por cualquiera de los jugadores)
    que aparece en la simulación, se suma un conteo y se incrementan las victorias si el jugador que
    realizó dicho movimiento es el ganador.

    sim_moves: lista de tuplas (move, player) de la simulación.
    """
    for move, player in sim_moves:
        # Inicializa contadores si es la primera vez que se ve el movimiento.
        if move not in node.rave_visits:
            node.rave_visits[move] = 0
            node.rave_wins[move] = 0
        node.rave_visits[move] += 1
        if player == winner:
            node.rave_wins[move] += 1


# ------------------------------
# Implementación del jugador de HEX con MCTS + RAVE
# ------------------------------
class MonteCarloHexPlayer(Player):
    def __init__(self, player_id: int, time_limit: float = 1.0):
        """
        player_id: el identificador del jugador (1 o 2)
        time_limit: límite de tiempo (en segundos) para la búsqueda MCTS por jugada.
        """
        super().__init__(player_id)
        self.time_limit = time_limit

    def play(self, board: "HexBoard") -> tuple:
        """
        Se escoge el movimiento a partir de una búsqueda iterativa MCTS con RAVE.
        Debido a la naturaleza aleatoria y la posibilidad de tener un tiempo limitado,
        se realizan simulaciones (rollouts) hasta agotar el tiempo.
        """
        # Creamos la raíz del árbol a partir del estado actual.
        # NOTA: La raíz es un nodo "dummy" sin movimiento, y se asigna como jugador el opuesto
        # de self.player_id para que el próximo movimiento (al expandir) sea de self.player_id.
        root = TreeNode(
            board.clone(), move=None, parent=None, player=3 - self.player_id
        )

        # Tiempo inicial para controlar el límite.
        start_time = time.time()
        iterations = 0

        while time.time() - start_time < self.time_limit:
            iterations += 1
            # Selección: comenzamos en la raíz y descendemos por el árbol hasta alcanzar un nodo
            # con movimientos sin probar o un estado terminal.
            node = root
            board_copy = board.clone()
            # Registro de movimientos realizados en la simulación (con el jugador que los hizo)
            simulation_moves = []

            # Fase de selección: avanzar mientras el nodo esté completamente expandido
            while node.is_fully_expanded() and node.children:
                # Seleccionamos el mejor hijo usando la combinación UCT+RAVE.
                node = node.best_child()
                if node.move is not None:
                    board_copy.place_piece(node.move[0], node.move[1], node.player)
                    simulation_moves.append((node.move, node.player))

            # Fase de expansión: si el nodo actual posee movimientos sin intentar, se selecciona uno al azar.
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                # El siguiente jugador es el opuesto al que jugó en el nodo actual.
                current_player = 3 - node.player
                board_copy.place_piece(move[0], move[1], current_player)
                simulation_moves.append((move, current_player))
                # Se crea un nodo hijo para el movimiento expandido.
                child_board = board_copy.clone()
                child_node = TreeNode(child_board, move, node, player=current_player)
                node.children[move] = child_node
                # Se elimina el movimiento de los no probados.
                node.untried_moves.remove(move)
                # Continuamos la simulación desde el nuevo nodo.
                node = child_node

            # Fase de simulación: se realiza un rollout a partir del estado actual.
            current_player = 3 - node.player  # El siguiente turno
            winner, sim_moves = rollout(board_copy, current_player)
            simulation_moves.extend(sim_moves)

            # Fase de backpropagation: se actualizan las estadísticas (MCTS y RAVE) a lo largo del camino.
            backprop_node = node
            while backprop_node is not None:
                backprop_node.visits += 1
                # La recompensa se da si el jugador que realizó el movimiento en el nodo ganó.
                if winner is not None and backprop_node.player == winner:
                    backprop_node.wins += 1
                # Actualizamos las estadísticas RAVE en el nodo.
                update_rave(backprop_node, simulation_moves, winner)
                backprop_node = backprop_node.parent

        # Después de terminar las simulaciones, se selecciona el hijo de la raíz con mayor número de visitas.
        best_move = None
        best_visits = -1
        for move, child in root.children.items():
            if child.visits > best_visits:
                best_visits = child.visits
                best_move = move

        # (Opcional) Se puede mostrar información adicional de la búsqueda:
        # print(f"Iteraciones realizadas: {iterations}, Mejor movimiento {best_move} con {best_visits} visitas.")
        return best_move
