from heapq import heappop, heappush
from basic_classes import Player, HexBoard
import random


class AStarPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)

    def _pos_to_node(self, pos: tuple) -> str:
        """Convierte una posición (fila, columna) a un identificador de nodo."""
        return f"pos_{pos[0]}_{pos[1]}"

    def _node_to_pos(self, node: str) -> tuple:
        """Convierte el identificador del nodo a una posición (fila, columna)."""
        if node in ["start", "end"]:
            return None
        _, row, col = node.split("_")
        return (int(row), int(col))

    def play(self, board: HexBoard) -> tuple:
        """
        Decide el siguiente movimiento usando A*.
        """
        graph = self._initialize_graph(board)
        path = self._astar(graph, "start", "end", board.size, board)

        # # Buscar la primera posición vacía en el camino (excluyendo nodos especiales)
        # for node in path:
        #     pos = self._node_to_pos(node)
        #     if pos is not None and board.board[pos[0]][pos[1]] == 0:
        #         return pos

        # Escoger aleatoriamente una posición vacía en el camino (excluyendo nodos especiales)
        valid_positions = [
            self._node_to_pos(node)
            for node in path
            if self._node_to_pos(node) is not None
            and board.board[self._node_to_pos(node)[0]][self._node_to_pos(node)[1]] == 0
        ]
        if valid_positions:
            return random.choice(valid_positions)

        # Si no se encontró, devolver algún movimiento válido
        return board.get_possible_moves()[0]

    def _heuristic(self, node: str, size: int, board: HexBoard) -> int:
        """
        Heurística mejorada:
         - Para el jugador 1 (conecta arriba a abajo): la distancia restante es (size - 1 - fila)
         - Para el jugador 2 (conecta izquierda a derecha): la distancia restante es (size - 1 - columna)
         - Penalidad adicional por alejarse del centro del tablero.
         - Penalidad adicional por estar junto a fichas del otro jugador.
         - Bonificación por estar junto a fichas propias conectadas.
        """
        if node in ["start", "end"]:
            return 0
        pos = self._node_to_pos(node)
        center = size // 2
        distance_from_center = abs(pos[0] - center) + abs(pos[1] - center)

        # Penalidad por estar junto a fichas del otro jugador
        penalty = 0
        bonus = 0
        opponent_id = 3 - self.player_id
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
            nr, nc = pos[0] + dr, pos[1] + dc
            if 0 <= nr < size and 0 <= nc < size:
                if board.board[nr][nc] == opponent_id:
                    penalty += 2  # Penalización por cada ficha del oponente adyacente
                elif board.board[nr][nc] == self.player_id:
                    bonus -= 1  # Bonificación por cada ficha propia adyacente

        if self.player_id == 1:
            # Conexión de arriba a abajo
            return max(0, size - 1 - pos[0]) + distance_from_center + penalty + bonus
        else:
            # Conexión de izquierda a derecha
            return max(0, size - 1 - pos[1]) + distance_from_center + penalty + bonus

    def _initialize_graph(self, board: HexBoard) -> dict:
        """
        Inicializa la representación en grafo del tablero Hex.
        """
        size = board.size
        graph = {"start": {}, "end": {}}

        # Agregar aristas desde 'start' a las celdas del borde de inicio
        if self.player_id == 1:  # Jugador 1 (arriba a abajo)
            for col in range(size):
                node = self._pos_to_node((0, col))
                if board.board[0][col] == 0:  # Casilla vacía
                    graph["start"][node] = 1
                elif board.board[0][col] == self.player_id:  # Nuestra ficha
                    graph["start"][node] = 0
        else:  # Jugador 2 (izquierda a derecha)
            for row in range(size):
                node = self._pos_to_node((row, 0))
                if board.board[row][0] == 0:
                    graph["start"][node] = 1
                elif board.board[row][0] == self.player_id:
                    graph["start"][node] = 0

        # Agregar aristas desde las celdas del borde de meta a 'end'
        if self.player_id == 1:
            for col in range(size):
                node = self._pos_to_node((size - 1, col))
                if board.board[size - 1][col] == self.player_id:
                    graph[node] = {"end": 0}
                elif board.board[size - 1][col] == 0:
                    graph[node] = {"end": 1}
        else:
            for row in range(size):
                node = self._pos_to_node((row, size - 1))
                if board.board[row][size - 1] == self.player_id:
                    graph[node] = {"end": 0}
                elif board.board[row][size - 1] == 0:
                    graph[node] = {"end": 1}

        # Agregar aristas entre posiciones internas del tablero
        for row in range(size):
            for col in range(size):
                curr_node = self._pos_to_node((row, col))
                if curr_node not in graph:
                    graph[curr_node] = {}

                # Solo considerar casillas vacías o con nuestra ficha
                if board.board[row][col] != 3 - self.player_id:
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < size and 0 <= nc < size:
                            next_node = self._pos_to_node((nr, nc))
                            neighbor_state = board.board[nr][nc]

                            if neighbor_state == 0:
                                graph[curr_node][next_node] = 1
                            elif neighbor_state == self.player_id:
                                graph[curr_node][next_node] = 0

        return graph

    def _astar(
        self, graph: dict, start: str, end: str, size: int, board: HexBoard
    ) -> list:
        """
        Encuentra el camino más corto de start a end utilizando el algoritmo A*.
        """
        # Cada entrada en la cola es (f, g, nodo_actual, camino)
        # f = g + h, donde g es el costo acumulado y h es la heurística
        frontier = [(self._heuristic(start, size, board), 0, start, [start])]
        visited = set()

        while frontier:
            f, g, current, path = heappop(frontier)

            if current in visited:
                continue
            visited.add(current)

            if current == end:
                return path

            for neighbor, step_cost in graph.get(current, {}).items():
                if neighbor not in visited:
                    new_g = g + step_cost
                    new_f = new_g + self._heuristic(neighbor, size, board)
                    new_path = path + [neighbor]
                    heappush(frontier, (new_f, new_g, neighbor, new_path))

        return []
