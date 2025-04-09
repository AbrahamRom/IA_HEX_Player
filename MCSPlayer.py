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
