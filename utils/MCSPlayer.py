import math
from dataclasses import dataclass
from typing import Optional, Tuple, List
import time
from basic_classes import Player
import random


@dataclass
class Node:
    move: Optional[Tuple[int, int]]  # The move that led to this state
    parent: Optional["Node"]
    player_id: int  # Player who will make the next move
    visits: int = 0
    wins: int = 0
    children: List["Node"] = None

    def add_children(self, moves: List[Tuple[int, int]], player_id: int):
        self.children = [Node(move=m, parent=self, player_id=player_id) for m in moves]

    def uct_value(self, exploration_constant: float = 1.41) -> float:
        if self.visits == 0:
            return float("inf")
        exploitation = self.wins / self.visits
        exploration = exploration_constant * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )
        return exploitation + exploration


class MCSPlayer(Player):
    def __init__(self, player_id, num_simulations=100, time_limit=2.0):
        super().__init__(player_id)
        self.num_simulations = num_simulations  # Number of random games to simulate
        self.time_limit = time_limit  # Time limit in seconds

    def play(self, board):
        start_time = time.time()
        possible_moves = board.get_possible_moves()
        best_move = None
        best_wins = -1

        # Try each possible move
        for move in possible_moves:
            wins = 0
            sims_for_move = 0

            # Run simulations for this move until time limit
            while (
                time.time() - start_time < self.time_limit
                and sims_for_move < self.num_simulations
            ):
                # Create a copy of the board and make the move
                sim_board = board.clone()
                sim_board.place_piece(move[0], move[1], self.player_id)

                # Simulate a random game from this position
                if self._simulate_game(sim_board):
                    wins += 1
                sims_for_move += 1

            # Update best move if this one has more wins
            win_rate = wins / sims_for_move if sims_for_move > 0 else 0
            if win_rate > best_wins:
                best_wins = win_rate
                best_move = move

        return best_move if best_move else random.choice(possible_moves)

    def _simulate_game(self, board):
        """Simulates a random game from the current position and returns True if we win"""
        sim_board = board.clone()
        current_player = 3 - self.player_id  # Start with opponent's turn

        # Play until someone wins
        while True:
            # Get possible moves
            moves = sim_board.get_possible_moves()
            if not moves:
                return False  # Draw (shouldn't happen in Hex)

            # Make a random move
            move = random.choice(moves)
            sim_board.place_piece(move[0], move[1], current_player)

            # Check for winner
            if sim_board.check_connection(current_player):
                return current_player == self.player_id

            # Switch players
            current_player = 3 - current_player


class MCS_UCT_Player(Player):
    def __init__(self, player_id, simulation_time=2.0):
        super().__init__(player_id)
        self.simulation_time = simulation_time

    def play(self, board):
        root = Node(move=None, parent=None, player_id=self.player_id)
        end_time = time.time() + self.simulation_time

        # Main MCTS loop
        while time.time() < end_time:
            # 1. Selection
            node = self._select(root, board.clone())
            sim_board = board.clone()
            # Reconstruct the board state for this node
            self._reconstruct_board(node, sim_board)

            # 2. Expansion
            if node.visits > 0 and not sim_board.check_connection(3 - node.player_id):
                moves = sim_board.get_possible_moves()
                if moves:
                    node.add_children(moves, 3 - node.player_id)
                    node = random.choice(node.children)
                    sim_board.place_piece(
                        node.move[0], node.move[1], node.parent.player_id
                    )

            # 3. Simulation
            result = self._simulate_game(sim_board, node.player_id)

            # 4. Backpropagation
            self._backpropagate(node, result)

        # Choose the best move
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    def _select(self, node: Node, board) -> Node:
        while node.children is not None and node.children:
            if not all(child.visits > 0 for child in node.children):
                # Select first unvisited child
                unvisited = [c for c in node.children if c.visits == 0]
                return random.choice(unvisited)
            # Select child with highest UCT value
            node = max(node.children, key=lambda c: c.uct_value())
        return node

    def _reconstruct_board(self, node: Node, board) -> None:
        moves = []
        current = node
        while current.parent is not None:
            moves.append((current.move, current.parent.player_id))
            current = current.parent
        for move, player in reversed(moves):
            board.place_piece(move[0], move[1], player)

    def _simulate_game(self, board, player_id: int) -> bool:
        sim_board = board.clone()
        current_player = player_id

        while True:
            moves = sim_board.get_possible_moves()
            if not moves:
                return False

            move = random.choice(moves)
            sim_board.place_piece(move[0], move[1], current_player)

            if sim_board.check_connection(current_player):
                return current_player == self.player_id

            current_player = 3 - current_player

    def _backpropagate(self, node: Node, won: bool) -> None:
        while node is not None:
            node.visits += 1
            if won:
                node.wins += 1
            node = node.parent


class MCT_A_star_Sim_Player(MCS_UCT_Player):
    def __init__(self, player_id, simulation_time=2.0):
        super().__init__(player_id, simulation_time)

    def _heuristic(self, pos, goal_cells, board):
        """Manhattan distance heuristic adjusted for hex board"""
        min_dist = float("inf")
        row, col = pos
        for goal_row, goal_col in goal_cells:
            # Adjusted distance calculation for hex grid
            dist = abs(row - goal_row) + abs(col - goal_col)
            min_dist = min(min_dist, dist)
        return min_dist

    def _get_neighbors(self, pos, board):
        """Get valid neighboring cells"""
        row, col = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        neighbors = []

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (
                0 <= new_row < board.size
                and 0 <= new_col < board.size
                and board.board[new_row][new_col] == 0
            ):
                neighbors.append((new_row, new_col))
        return neighbors

    def _get_goal_cells(self, player_id, board):
        """Get the goal cells based on player_id"""
        if player_id == 1:  # Vertical connection (top to bottom)
            return [(board.size - 1, col) for col in range(board.size)]
        else:  # Horizontal connection (left to right)
            return [(row, board.size - 1) for row in range(board.size)]

    def _get_start_cells(self, player_id, board):
        """Get the starting cells based on player_id"""
        if player_id == 1:  # Vertical connection (top to bottom)
            return [(0, col) for col in range(board.size)]
        else:  # Horizontal connection (left to right)
            return [(row, 0) for row in range(board.size)]

    def _a_star_simulation(self, board, player_id):
        """Simulate game using A* pathfinding"""
        from heapq import heappush, heappop

        sim_board = board.clone()
        current_player = player_id

        while True:
            # Get start and goal positions for current player
            start_cells = self._get_start_cells(current_player, sim_board)
            goal_cells = self._get_goal_cells(current_player, sim_board)

            # Initialize A* algorithm
            open_set = []
            closed_set = set()
            g_score = {}
            f_score = {}

            # Add all start cells to open set
            for start in start_cells:
                if sim_board.board[start[0]][start[1]] == 0:
                    heappush(
                        open_set, (self._heuristic(start, goal_cells, sim_board), start)
                    )
                    g_score[start] = 0
                    f_score[start] = self._heuristic(start, goal_cells, sim_board)

            # A* search
            selected_move = None
            while open_set and not selected_move:
                current = heappop(open_set)[1]

                if current in goal_cells:
                    selected_move = current
                    break

                closed_set.add(current)

                for neighbor in self._get_neighbors(current, sim_board):
                    if neighbor in closed_set:
                        continue

                    tentative_g = g_score[current] + 1

                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self._heuristic(
                            neighbor, goal_cells, sim_board
                        )
                        heappush(open_set, (f_score[neighbor], neighbor))

            # If no path found, make a random move
            if not selected_move:
                moves = sim_board.get_possible_moves()
                if not moves:
                    return False
                selected_move = random.choice(moves)

            # Make the move
            sim_board.place_piece(selected_move[0], selected_move[1], current_player)

            # Check for winner
            if sim_board.check_connection(current_player):
                return current_player == self.player_id

            # Switch players
            current_player = 3 - current_player

    def _simulate_game(self, board, player_id: int) -> bool:
        """Override the random simulation with A* guided simulation"""
        return self._a_star_simulation(board, player_id)


class MCT_A_star_Exp_Player(MCS_UCT_Player):
    def __init__(self, player_id, simulation_time=2.0):
        super().__init__(player_id, simulation_time)

    def _heuristic(self, pos, goal_cells, board):
        """Manhattan distance heuristic adjusted for hex board"""
        min_dist = float("inf")
        row, col = pos
        for goal_row, goal_col in goal_cells:
            dist = abs(row - goal_row) + abs(col - goal_col)
            min_dist = min(min_dist, dist)
        return min_dist

    def _get_neighbors(self, pos, board):
        """Get valid neighboring cells"""
        row, col = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        neighbors = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (
                0 <= new_row < board.size
                and 0 <= new_col < board.size
                and board.board[new_row][new_col] == 0
            ):
                neighbors.append((new_row, new_col))
        return neighbors

    def _get_goal_cells(self, player_id, board):
        """Get goal cells based on player_id"""
        if player_id == 1:  # Vertical connection
            return [(board.size - 1, col) for col in range(board.size)]
        else:  # Horizontal connection
            return [(row, board.size - 1) for row in range(board.size)]

    def _get_start_cells(self, player_id, board):
        """Get starting cells based on player_id"""
        if player_id == 1:  # Vertical connection
            return [(0, col) for col in range(board.size)]
        else:  # Horizontal connection
            return [(row, 0) for row in range(board.size)]

    def _evaluate_move_a_star(self, move, board, player_id):
        """Evaluate a move using A* pathfinding"""
        from heapq import heappush, heappop

        # Make the move on a temporary board
        sim_board = board.clone()
        sim_board.place_piece(move[0], move[1], player_id)

        start_cells = self._get_start_cells(player_id, sim_board)
        goal_cells = self._get_goal_cells(player_id, sim_board)

        # Initialize A* algorithm
        open_set = []
        closed_set = set()
        g_score = {}

        # Add all start cells to open set
        min_f_score = float("inf")
        for start in start_cells:
            if sim_board.board[start[0]][start[1]] in [0, player_id]:
                h_score = self._heuristic(start, goal_cells, sim_board)
                heappush(open_set, (h_score, start))
                g_score[start] = 0
                min_f_score = min(min_f_score, h_score)

        # If no valid path exists, return a high score
        if min_f_score == float("inf"):
            return float("inf")

        return min_f_score

    def _select(self, node: Node, board) -> Node:
        """Modified selection using A* evaluation for unvisited nodes"""
        while node.children is not None and node.children:
            if not all(child.visits > 0 for child in node.children):
                # Evaluate unvisited children using A*
                unvisited = [c for c in node.children if c.visits == 0]
                scores = [
                    (self._evaluate_move_a_star(c.move, board, node.player_id), c)
                    for c in unvisited
                ]
                return min(scores, key=lambda x: x[0])[1]
            # Use standard UCT for visited nodes
            node = max(node.children, key=lambda c: c.uct_value())
        return node


class MCT_Full_A_Star_Player(MCS_UCT_Player):
    def __init__(self, player_id, simulation_time=2.0):
        super().__init__(player_id, simulation_time)

    def _heuristic(self, pos, goal_cells):
        """Manhattan distance heuristic adjusted for hex board"""
        min_dist = float("inf")
        row, col = pos
        for goal_row, goal_col in goal_cells:
            dist = abs(row - goal_row) + abs(col - goal_col)
            min_dist = min(min_dist, dist)
        return min_dist

    def _get_neighbors(self, pos, board):
        """Get valid neighboring cells"""
        row, col = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        neighbors = []
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (
                0 <= new_row < board.size
                and 0 <= new_col < board.size
                and board.board[new_row][new_col] == 0
            ):
                neighbors.append((new_row, new_col))
        return neighbors

    def _get_goal_cells(self, player_id, board):
        """Get goal cells based on player_id"""
        if player_id == 1:  # Vertical connection
            return [(board.size - 1, col) for col in range(board.size)]
        else:  # Horizontal connection
            return [(row, board.size - 1) for row in range(board.size)]

    def _get_start_cells(self, player_id, board):
        """Get starting cells based on player_id"""
        if player_id == 1:  # Vertical connection
            return [(0, col) for col in range(board.size)]
        else:  # Horizontal connection
            return [(row, 0) for row in range(board.size)]

    def _evaluate_moves_with_a_star(self, board, player_id):
        """Evaluate all possible moves using A* and return them sorted by score"""
        from heapq import heappush, heappop

        moves = board.get_possible_moves()
        move_scores = []

        for move in moves:
            # Create a temporary board with the move
            sim_board = board.clone()
            sim_board.place_piece(move[0], move[1], player_id)

            # Initialize A* parameters
            start_cells = self._get_start_cells(player_id, sim_board)
            goal_cells = self._get_goal_cells(player_id, sim_board)

            # Find the minimum path length using A*
            min_path_length = float("inf")
            for start in start_cells:
                if sim_board.board[start[0]][start[1]] in [0, player_id]:
                    open_set = [(self._heuristic(start, goal_cells), 0, start)]
                    closed_set = set()
                    g_scores = {start: 0}

                    while open_set:
                        f, g, current = heappop(open_set)

                        if current in goal_cells:
                            min_path_length = min(min_path_length, g)
                            break

                        if current in closed_set:
                            continue

                        closed_set.add(current)

                        for neighbor in self._get_neighbors(current, sim_board):
                            if neighbor in closed_set:
                                continue

                            tentative_g = g_scores[current] + 1

                            if (
                                neighbor not in g_scores
                                or tentative_g < g_scores[neighbor]
                            ):
                                g_scores[neighbor] = tentative_g
                                f_score = tentative_g + self._heuristic(
                                    neighbor, goal_cells
                                )
                                heappush(open_set, (f_score, tentative_g, neighbor))

            move_scores.append((min_path_length, move))

        return [move for _, move in sorted(move_scores)]

    def play(self, board):
        root = Node(move=None, parent=None, player_id=self.player_id)
        end_time = time.time() + self.simulation_time

        # Main MCTS loop with A* guided expansion and simulation
        while time.time() < end_time:
            # Selection
            node = self._select(root, board.clone())
            sim_board = board.clone()
            self._reconstruct_board(node, sim_board)

            # Expansion with A* guidance
            if node.visits > 0 and not sim_board.check_connection(3 - node.player_id):
                sorted_moves = self._evaluate_moves_with_a_star(
                    sim_board, 3 - node.player_id
                )
                if sorted_moves:
                    node.add_children(sorted_moves, 3 - node.player_id)
                    # Choose the best move according to A*
                    node = node.children[0]
                    sim_board.place_piece(
                        node.move[0], node.move[1], node.parent.player_id
                    )

            # Simulation (using A* guided playouts)
            result = self._a_star_simulation(sim_board, node.player_id)

            # Backpropagation
            self._backpropagate(node, result)

        # Choose the best move based on visit count
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    def _a_star_simulation(self, board, player_id):
        """Simulate game using A* for move selection"""
        sim_board = board.clone()
        current_player = player_id

        while True:
            # Get moves sorted by A* evaluation
            moves = self._evaluate_moves_with_a_star(sim_board, current_player)
            if not moves:
                return False

            # Choose the best move according to A*
            best_move = moves[0]
            sim_board.place_piece(best_move[0], best_move[1], current_player)

            # Check for winner
            if sim_board.check_connection(current_player):
                return current_player == self.player_id

            # Switch players
            current_player = 3 - current_player


class MCT_Heuristic_Player(MCS_UCT_Player):
    def __init__(self, player_id, simulation_time=2.0):
        super().__init__(player_id, simulation_time)

    def _evaluate_position(self, pos, board, player_id):
        """
        Evaluate position using multiple heuristics:
        1. Distance to goals
        2. Connectivity potential
        3. Center control
        """
        row, col = pos
        score = 0

        # Distance to goals
        if player_id == 1:  # Vertical connection (top-bottom)
            score -= abs(row - (board.size - 1))  # Distance to bottom
        else:  # Horizontal connection (left-right)
            score -= abs(col - (board.size - 1))  # Distance to right edge

        # Center control (positions closer to center are better)
        center = board.size // 2
        center_dist = abs(row - center) + abs(col - center)
        score += (board.size - center_dist) / 2

        # Connectivity potential (count empty neighbors)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1)]
        empty_neighbors = 0
        friendly_neighbors = 0

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < board.size and 0 <= new_col < board.size:
                if board.board[new_row][new_col] == 0:
                    empty_neighbors += 1
                elif board.board[new_row][new_col] == player_id:
                    friendly_neighbors += 1

        score += empty_neighbors * 0.5 + friendly_neighbors * 1.0
        return score

    def _get_best_moves(self, board, player_id, num_moves=1):
        """Get the top N moves based on heuristic evaluation"""
        possible_moves = board.get_possible_moves()
        move_scores = []

        for move in possible_moves:
            score = self._evaluate_position(move, board, player_id)
            move_scores.append((score, move))

        # Sort moves by score and return top N
        move_scores.sort(reverse=True)
        return [move for _, move in move_scores[:num_moves]]

    def _select(self, node: Node, board) -> Node:
        """Modified selection using heuristic evaluation for unvisited nodes"""
        while node.children is not None and node.children:
            if not all(child.visits > 0 for child in node.children):
                unvisited = [c for c in node.children if c.visits == 0]
                scores = [
                    (self._evaluate_position(c.move, board, node.player_id), c)
                    for c in unvisited
                ]
                return max(scores, key=lambda x: x[0])[1]
            node = max(node.children, key=lambda c: c.uct_value())
        return node

    def play(self, board):
        root = Node(move=None, parent=None, player_id=self.player_id)
        end_time = time.time() + self.simulation_time

        while time.time() < end_time:
            # Selection
            node = self._select(root, board.clone())
            sim_board = board.clone()
            self._reconstruct_board(node, sim_board)

            # Expansion with heuristic guidance
            if node.visits > 0 and not sim_board.check_connection(3 - node.player_id):
                best_moves = self._get_best_moves(sim_board, 3 - node.player_id)
                if best_moves:
                    node.add_children(best_moves, 3 - node.player_id)
                    node = random.choice(node.children)
                    sim_board.place_piece(
                        node.move[0], node.move[1], node.parent.player_id
                    )

            # Simulation with heuristic guidance
            result = self._heuristic_simulation(sim_board, node.player_id)

            # Backpropagation
            self._backpropagate(node, result)

        # Choose best child based on visits and wins
        best_child = max(
            root.children, key=lambda c: (c.wins / c.visits) + (c.visits / root.visits)
        )
        return best_child.move

    def _heuristic_simulation(self, board, player_id: int) -> bool:
        """Simulate game using heuristic-guided moves instead of random"""
        sim_board = board.clone()
        current_player = player_id

        while True:
            # Get top moves based on heuristic
            best_moves = self._get_best_moves(sim_board, current_player, num_moves=3)
            if not best_moves:
                return False

            # Choose one of the top moves (with some randomness)
            move = random.choice(best_moves)
            sim_board.place_piece(move[0], move[1], current_player)

            if sim_board.check_connection(current_player):
                return current_player == self.player_id

            current_player = 3 - current_player
