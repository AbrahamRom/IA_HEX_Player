from copy import deepcopy
import random
from basic_classes import Player


class BadPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)

    def play(self, board) -> tuple:
        """
        Select a move by trying to place pieces adjacent to existing ones
        and moving towards the goal side.
        :param board: Current HexBoard instance.
        :return: Tuple (row, col) of selected move.
        """
        possible_moves = board.get_possible_moves()
        my_positions = board.player_positions[self.player_id]

        # If no pieces placed yet, start near the starting edge
        if not my_positions:
            if self.player_id == 1:  # Red player (top to bottom)
                return (0, board.size // 2)  # Start at top middle
            else:  # Blue player (left to right)
                return (board.size // 2, 0)  # Start at left middle

        best_move = None
        best_score = float("inf")

        for move in possible_moves:
            row, col = move
            # Check if move is adjacent to any of our pieces
            is_adjacent = any(
                abs(row - pos[0]) <= 1 and abs(col - pos[1]) <= 1
                for pos in my_positions
            )

            if is_adjacent:
                if self.player_id == 1:  # Red player
                    # Score based on distance to bottom
                    score = board.size - row
                else:  # Blue player
                    # Score based on distance to right side
                    score = board.size - col

                if score < best_score:
                    best_score = score
                    best_move = move
                elif score == best_score and random.random() < 0.5:
                    best_move = move

        # If no adjacent moves found, choose randomly
        return best_move if best_move is not None else random.choice(possible_moves)


class ManhattanPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)

    def play(self, board) -> tuple:
        """
        Select a move based on Manhattan distance heuristic.
        For player 1 (Red): Tries to minimize distance between top and bottom
        For player 2 (Blue): Tries to minimize distance between left and right

        :param board: Current HexBoard instance
        :return: Tuple (row, col) of the selected move
        """
        possible_moves = board.get_possible_moves()
        best_move = None
        best_score = float("inf")  # We want to minimize distance

        board_size = board.size

        for move in possible_moves:
            row, col = move
            current_score = float("inf")

            # Player 1 (Red) - Connects top to bottom
            if self.player_id == 1:
                # Manhattan distance from current position to bottom row
                distance_to_bottom = board_size - 1 - row
                # Add penalty for moves far from center column
                center_penalty = abs(col - board_size // 2)
                current_score = distance_to_bottom + 0.3 * center_penalty

            # Player 2 (Blue) - Connects left to right
            else:
                # Manhattan distance from current position to right edge
                distance_to_right = board_size - 1 - col
                # Add penalty for moves far from center row
                center_penalty = abs(row - board_size // 2)
                current_score = distance_to_right + 0.3 * center_penalty

            # Update best move if current score is better
            if current_score < best_score:
                best_score = current_score
                best_move = move

            # # Break ties randomly
            elif current_score == best_score and random.random() < 0.5:
                best_move = move

        return best_move


class AsPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)

    def play(self, board) -> tuple:
        """
        Select a move using A* search algorithm.
        For player 1 (Red): Finds path from top to bottom
        For player 2 (Blue): Finds path from left to right
        """
        possible_moves = board.get_possible_moves()
        if not possible_moves:
            return None

        def heuristic(pos):
            row, col = pos
            if self.player_id == 1:  # Red player (top to bottom)
                return board.size - row  # Distance to bottom
            else:  # Blue player (left to right)
                return board.size - col  # Distance to right

        def get_neighbors(pos):
            row, col = pos
            directions = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, 1)]
            neighbors = []
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if (new_row, new_col) in possible_moves:
                    neighbors.append((new_row, new_col))
            return neighbors

        best_move = None
        best_score = float("inf")

        # Evaluate each possible move
        for move in possible_moves:
            # Calculate f_score = g_score + h_score
            g_score = len(board.player_positions[self.player_id])  # Current path length
            h_score = heuristic(move)
            f_score = g_score + h_score

            # Check if this move blocks opponent
            opponent_id = 3 - self.player_id
            opponent_positions = board.player_positions[opponent_id]
            if opponent_positions:
                # Bonus for blocking opponent's path
                for opp_pos in opponent_positions:
                    if (
                        abs(move[0] - opp_pos[0]) <= 1
                        and abs(move[1] - opp_pos[1]) <= 1
                    ):
                        f_score -= 2

            if f_score < best_score:
                best_score = f_score
                best_move = move
            elif f_score == best_score and random.random() < 0.5:
                best_move = move

        return best_move if best_move else random.choice(possible_moves)


import heapq
import time


class UCSPlayer(Player):
    def __init__(self, player_id: int):
        super().__init__(player_id)

    def play(self, board) -> tuple:
        best_move = None
        min_cost = float("inf")

        for move in board.get_possible_moves():
            # Clonamos el tablero para simular el movimiento
            new_board = board.clone()
            new_board.place_piece(*move, self.player_id)

            # Calculamos el costo mínimo para conectar los bordes
            cost = self._ucs_path_cost(new_board)

            if cost < min_cost:
                min_cost = cost
                best_move = move

        print(min_cost)
        print(best_move)

        time.sleep(1)

        return best_move

    def inicialize_graph(self, board):
        size = board.size
        graph = {}
        start_node = "start"
        end_node = "end"

        # Initialize graph with start and end nodes
        graph[start_node] = {}
        graph[end_node] = {}

        # Add edges from start node to initial positions
        if self.player_id == 1:  # Red player (top to bottom)
            for col in range(size):
                graph[start_node][(0, col)] = 0
        else:  # Blue player (left to right)
            for row in range(size):
                graph[start_node][(row, 0)] = 0

        # Add edges from final positions to end node
        if self.player_id == 1:  # Red player (top to bottom)
            for col in range(size):
                graph[(size - 1, col)] = {end_node: 0}
        else:  # Blue player (left to right)
            for row in range(size):
                graph[(row, size - 1)] = {end_node: 0}

        # Add edges for all board positions
        for row in range(size):
            for col in range(size):
                if board.board[row][col] != 3 - self.player_id:  # Ignore opponent cells
                    graph[(row, col)] = {}
                    if row % 2 == 0:  # Even rows
                        directions = [
                            (-1, 0),  # Up
                            (1, 0),  # Down
                            (0, -1),  # Left
                            (0, 1),  # Right
                            (-1, 1),  # Up-Right
                            (1, 1),  # Down-Right
                        ]
                    else:  # Odd rows
                        directions = [
                            (-1, 0),  # Up
                            (1, 0),  # Down
                            (0, -1),  # Left
                            (0, 1),  # Right
                            (-1, -1),  # Up-Left
                            (1, -1),  # Down-Left
                        ]
                    for dr, dc in directions:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < size and 0 <= nc < size:
                            if board.board[nr][nc] == 0:  # Empty cell
                                graph[(row, col)][(nr, nc)] = 1
                            elif board.board[nr][nc] == self.player_id:  # Own cell
                                graph[(row, col)][(nr, nc)] = 0
                            # Opponent's cell is ignored

        return graph

    def _ucs_path_cost(self, board) -> int:
        size = board.size

        graph = self.inicialize_graph(board)

        # Priority queue for UCS
        frontier = [(0, "start")]  # (cost, node)
        heapq.heapify(frontier)

        # Keep track of visited nodes and costs
        visited = set()
        cost_so_far = {"start": 0}

        while frontier:
            current_cost, current_node = heapq.heappop(frontier)

            if current_node == "end":
                return current_cost

            if current_node in visited:
                continue

            visited.add(current_node)

            # Explore neighbors
            for next_node, step_cost in graph[current_node].items():
                if next_node not in visited:
                    new_cost = current_cost + step_cost
                    if (
                        next_node not in cost_so_far
                        or new_cost < cost_so_far[next_node]
                    ):
                        cost_so_far[next_node] = new_cost
                        heapq.heappush(frontier, (new_cost, next_node))

        return float("inf")  # No path found

    #     size = board.size
    #     visited = set()
    #     heap = []

    #     def get_neighbors(i, j, size):
    #         neighbors = []
    #         if i % 2 == 0:  # Filas pares
    #             offsets = [
    #                 (0, -1),  # Izquierda
    #                 (0, 1),  # Derecha
    #                 (-1, 0),  # Arriba
    #                 (1, 0),  # Abajo
    #                 (-1, 1),  # Arriba-Derecha
    #                 (1, 1),  # Abajo-Derecha
    #             ]
    #         else:  # Filas impares
    #             offsets = [
    #                 (0, -1),  # Izquierda
    #                 (0, 1),  # Derecha
    #                 (-1, 0),  # Arriba
    #                 (1, 0),  # Abajo
    #                 (-1, -1),  # Arriba-Izquierda
    #                 (1, -1),  # Abajo-Izquierda
    #             ]

    #         for di, dj in offsets:
    #             ni, nj = i + di, j + dj
    #             if 0 <= ni < size and 0 <= nj < size:
    #                 neighbors.append((ni, nj))

    #         return neighbors

    #     start_edges = []
    #     target_check = lambda r, c: False

    #     if self.player_id == 1:
    #         # Norte-Sur
    #         start_edges = [(0, col) for col in range(size)]
    #         target_check = lambda r, c: r == size - 1
    #     else:
    #         # Oeste-Este
    #         start_edges = [(row, 0) for row in range(size)]
    #         target_check = lambda r, c: c == size - 1

    #     for r, c in start_edges:
    #         cell = board.board[r][c]
    #         if cell == self.player_id:
    #             heapq.heappush(heap, (0, (r, c)))
    #         elif cell == 0:
    #             heapq.heappush(heap, (1, (r, c)))

    #     while heap:
    #         cost, (r, c) = heapq.heappop(heap)
    #         if (r, c) in visited:
    #             continue
    #         visited.add((r, c))

    #         if target_check(r, c):
    #             return cost

    #         for nr, nc in get_neighbors(r, c, size):
    #             if (nr, nc) in visited:
    #                 continue

    #             cell = board.board[nr][nc]
    #             if cell == self.player_id:
    #                 heapq.heappush(heap, (cost, (nr, nc)))
    #             elif cell == 0:
    #                 heapq.heappush(heap, (cost + 1, (nr, nc)))
    #             # Las celdas del oponente no se agregan

    #     return float("inf")


class Gplayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)

    def play(self, board):
        pass
