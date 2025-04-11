from basic_classes import Player
import math
import time
import random
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List


@dataclass
class RAVENode:
    move: Optional[Tuple[int, int]]  # The move that led to this state
    parent: Optional["RAVENode"]
    player_id: int  # Player who will make the next move
    visits: int = 0
    wins: int = 0
    children: List["RAVENode"] = None
    amaf_visits: Dict[Tuple[int, int], int] = None  # RAVE statistics
    amaf_wins: Dict[Tuple[int, int], int] = None

    def __post_init__(self):
        if self.amaf_visits is None:
            self.amaf_visits = {}
        if self.amaf_wins is None:
            self.amaf_wins = {}

    def add_children(self, moves: List[Tuple[int, int]], player_id: int):
        self.children = [
            RAVENode(move=m, parent=self, player_id=player_id) for m in moves
        ]

    def get_rave_value(self, move: Tuple[int, int], exploration: float = 1.4) -> float:
        """Calculate RAVE value for a move with improved evaluation"""
        beta = math.sqrt(exploration / (3 * self.visits + exploration))

        # Regular UCT value
        if self.visits == 0:
            exploitation = float("inf")
            exploration_term = 0
        else:
            exploitation = self.wins / self.visits
            exploration_term = math.sqrt(2 * math.log(self.parent.visits) / self.visits)

        # AMAF value
        if move in self.amaf_visits and self.amaf_visits[move] > 0:
            amaf = self.amaf_wins[move] / self.amaf_visits[move]
        else:
            amaf = 0

        # Add a penalty for moves that have been explored too much without success
        penalty = 0
        if self.visits > 0 and self.wins / self.visits < 0.1:  # Example threshold
            penalty = -0.1 * (1 - self.wins / self.visits)

        # Combine UCT and AMAF using beta weights and apply penalty
        return (1 - beta) * exploitation + beta * amaf + exploration_term + penalty


class RavePlayer(Player):
    def __init__(self, player_id: int, simulation_time: float = 2.0):
        super().__init__(player_id)
        self.simulation_time = simulation_time
        self.opponent_id = 3 - player_id

    def play(self, board) -> tuple:
        """Execute a move using Monte Carlo Tree Search with RAVE"""
        root = RAVENode(move=None, parent=None, player_id=self.player_id)
        end_time = time.time() + self.simulation_time

        while time.time() < end_time:
            # Phase 1: Selection and Expansion
            node = self._select_and_expand(root, board.clone())

            # Phase 2: Simulation
            sim_board = board.clone()
            self._reconstruct_board(node, sim_board)
            moves_played = self._simulate(sim_board, node.player_id)

            # Phase 3: Backpropagation with RAVE updates
            self._backpropagate(node, moves_played)

        # Select best child based on visit count
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    def _select_and_expand(self, node: RAVENode, board) -> RAVENode:
        """Select a node to expand using RAVE statistics"""
        while not self._is_terminal(board):
            if not node.children:
                # Expand node if it hasn't been expanded yet
                moves = board.get_possible_moves()
                if moves:
                    node.add_children(moves, 3 - node.player_id)
                    return random.choice(node.children)
                return node

            # Select best child using RAVE values
            best_value = float("-inf")
            best_child = None

            for child in node.children:
                value = child.get_rave_value(child.move)
                if value > best_value:
                    best_value = value
                    best_child = child

            if best_child is None:
                return node

            node = best_child
            if node.move:
                board.place_piece(node.move[0], node.move[1], node.parent.player_id)

        return node

    def _simulate(self, board, current_player_id) -> List[Tuple[Tuple[int, int], int]]:
        """Simulate a random game and return the moves played"""
        moves_played = []
        while not self._is_terminal(board):
            moves = board.get_possible_moves()
            if not moves:
                break

            move = random.choice(moves)
            moves_played.append((move, current_player_id))
            board.place_piece(move[0], move[1], current_player_id)

            if board.check_connection(current_player_id):
                break

            current_player_id = 3 - current_player_id

        return moves_played

    def _backpropagate(
        self, node: RAVENode, moves_played: List[Tuple[Tuple[int, int], int]]
    ):
        """Update node statistics including RAVE values"""
        won = any(
            player_id == self.player_id and self._is_winning_move(move, player_id)
            for move, player_id in moves_played
        )

        while node is not None:
            node.visits += 1
            if won:
                node.wins += 1

            # Update AMAF statistics
            for move, player_id in moves_played:
                if player_id == node.player_id:
                    if move not in node.amaf_visits:
                        node.amaf_visits[move] = 0
                        node.amaf_wins[move] = 0
                    node.amaf_visits[move] += 1
                    if won:
                        node.amaf_wins[move] += 1

            node = node.parent

    def _is_terminal(self, board) -> bool:
        """Check if the game state is terminal"""
        return (
            board.check_connection(self.player_id)
            or board.check_connection(self.opponent_id)
            or not board.get_possible_moves()
        )

    def _is_winning_move(self, move: Tuple[int, int], player_id: int) -> bool:
        """Check if a move is a winning move for the given player"""
        return True if player_id == self.player_id else False

    def _reconstruct_board(self, node: RAVENode, board) -> None:
        """Reconstruct the board state up to the given node"""
        moves = []
        current = node
        while current.parent is not None:
            moves.append((current.move, current.parent.player_id))
            current = current.parent

        for move, player_id in reversed(moves):
            board.place_piece(move[0], move[1], player_id)
