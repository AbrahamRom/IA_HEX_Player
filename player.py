from copy import deepcopy
import random
from basic_classes import Player


class MyPlayer(Player):
    def __init__(self, player_id):
        super().__init__(player_id)

    def play(self, board) -> tuple:
        """
        Método principal para seleccionar la jugada.
        :param board: Instancia de HexBoard con el estado actual del juego.
        :return: Tupla (fila, columna) de la jugada seleccionada.
        """
        possible_moves = board.get_possible_moves()
        best_move = None
        best_score = -float("inf")

        # Evaluamos cada movimiento posible
        for move in possible_moves:
            # Clonar el tablero para simular la jugada
            board_copy = self.clone_board(board)
            board_copy.place_piece(move[0], move[1], self.player_id)
            score = self.evaluate_board(board_copy)
            if score > best_score:
                best_score = score
                best_move = move

        # En caso de que no se haya definido un movimiento óptimo, se elige uno al azar
        return best_move if best_move is not None else random.choice(possible_moves)

    def evaluate_board(self, board) -> int:
        """
        Función heurística para evaluar el tablero.
        Se calcula la diferencia entre la cantidad de fichas propias y las del oponente.
        :param board: Instancia de HexBoard después de aplicar un movimiento.
        :return: Puntuación del tablero.
        """
        my_pieces = len(board.player_positions[self.player_id])
        opponent_pieces = len(board.player_positions[3 - self.player_id])
        return my_pieces - opponent_pieces

    def clone_board(self, board):
        """
        Método para clonar el tablero. Se asume que la clase HexBoard implementa un método clone.
        :param board: Instancia actual de HexBoard.
        :return: Copia del tablero.
        """
        return board.clone()
