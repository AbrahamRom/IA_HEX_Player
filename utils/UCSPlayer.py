from heapq import heappop, heappush
from basic_classes import Player, HexBoard


class UCSPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)

    def _pos_to_node(self, pos: tuple) -> str:
        """Convert position tuple to node string"""
        return f"pos_{pos[0]}_{pos[1]}"

    def _node_to_pos(self, node: str) -> tuple:
        """Convert node string back to position tuple"""
        if node in ["start", "end"]:
            return None
        _, row, col = node.split("_")
        return (int(row), int(col))

    def play(self, board: HexBoard) -> tuple:
        """
        Decide the next move using Uniform Cost Search (UCS).
        """
        graph = self._initialize_graph(board)
        path = self._ucs(graph, "start", "end")

        # Find first empty position in path
        for node in path:
            pos = self._node_to_pos(node)
            if pos is not None and board.board[pos[0]][pos[1]] == 0:
                return pos

        return board.get_possible_moves()[0]

    def _initialize_graph(self, board: HexBoard) -> dict:
        """
        Initializes the graph representation of the Hex board.
        """
        size = board.size
        graph = {"start": {}, "end": {}}

        # Add edges from 'start' to first row/column
        if self.player_id == 1:  # Red player (top to bottom)
            for col in range(size):
                node = self._pos_to_node((0, col))
                if board.board[0][col] == 0:  # Casilla vacía
                    graph["start"][node] = 1
                elif board.board[0][col] == self.player_id:  # Nuestra ficha
                    graph["start"][node] = 0
        else:  # Blue player (left to right)
            for row in range(size):
                node = self._pos_to_node((row, 0))
                if board.board[row][0] == 0:  # Casilla vacía
                    graph["start"][node] = 1
                elif board.board[row][0] == self.player_id:  # Nuestra ficha
                    graph["start"][node] = 0

        # Add edges to 'end' from last row/column
        if self.player_id == 1:
            for col in range(size):
                node = self._pos_to_node((size - 1, col))
                if board.board[size - 1][col] == self.player_id:  # Nuestra ficha
                    graph[node] = {"end": 0}
                elif board.board[size - 1][col] == 0:  # Casilla vacía
                    graph[node] = {"end": 1}
        else:
            for row in range(size):
                node = self._pos_to_node((row, size - 1))
                if board.board[row][size - 1] == self.player_id:  # Nuestra ficha
                    graph[node] = {"end": 0}
                elif board.board[row][size - 1] == 0:  # Casilla vacía
                    graph[node] = {"end": 1}

        # Add edges between board positions
        for row in range(size):
            for col in range(size):
                curr_node = self._pos_to_node((row, col))
                if curr_node not in graph:
                    graph[curr_node] = {}

                # Solo procesar si la casilla está vacía o es nuestra
                if (
                    board.board[row][col] != 3 - self.player_id
                ):  # No procesar casillas del oponente
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < size and 0 <= nc < size:
                            next_node = self._pos_to_node((nr, nc))
                            curr_state = board.board[nr][nc]

                            # Diferentes costos según el estado de la casilla
                            if curr_state == 0:  # Casilla vacía
                                graph[curr_node][next_node] = 1
                            elif curr_state == self.player_id:  # Nuestra ficha
                                graph[curr_node][next_node] = 0

        return graph

    def _ucs(self, graph: dict, start: str, end: str) -> list:
        """
        Finds the shortest path from start to end using Uniform Cost Search (UCS).
        """
        frontier = [(0, start, [start])]  # (cost, current_node, path)
        visited = set()

        while frontier:
            cost, current, path = heappop(frontier)

            if current in visited:
                continue
            visited.add(current)

            if current == end:
                return path

            for neighbor, step_cost in graph[current].items():
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    heappush(frontier, (cost + step_cost, neighbor, new_path))

        return []
