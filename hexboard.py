from basic_classes import HexBoard
import os


class MyBoard(HexBoard):
    def __init__(self, size: int):
        super().__init__(size)

    def clone(self) -> "HexBoard":
        """Devuelve una copia del tablero actual"""
        new_board = HexBoard(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.player_positions = {
            1: self.player_positions[1].copy(),
            2: self.player_positions[2].copy(),
        }
        return new_board

    def place_piece(self, row: int, col: int, player_id: int) -> bool:
        """Coloca una ficha si la casilla está vacía."""
        # Verificar si la posición está dentro del tablero
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False

        # Verificar si la casilla está vacía
        if self.board[row][col] != 0:
            return False

        # Colocar la ficha
        self.board[row][col] = player_id
        # Registrar la posición para el jugador
        self.player_positions[player_id].add((row, col))

        return True

    def get_possible_moves(self) -> list:
        """Devuelve todas las casillas vacías como tuplas (fila, columna)."""
        possible_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0:  # Si la casilla está vacía
                    possible_moves.append((row, col))
        return possible_moves

    def print_board(self):
        """Imprime el tablero actual en formato hexagonal"""
        # Clear console before printing
        os.system("cls" if os.name == "nt" else "clear")

        for i in range(self.size):
            # Print leading spaces for the hex layout
            print(" " * i, end="")

            # Print the row
            for j in range(self.size):
                cell = self.board[i][j]
                if cell == 0:
                    print(". ", end="")
                elif cell == 1:
                    print("B ", end="")  # Blue player (North-South)
                else:
                    print("R ", end="")  # Red player (East-West)
            print()  # New line after each row

    def check_connection(self, player_id: int) -> bool:
        """Verifica si el jugador ha conectado sus dos lados"""
        if player_id == 1:  # Jugador 1 conecta norte-sur
            # Encontrar todas las piezas en la primera fila
            start_positions = [
                (0, col) for col in range(self.size) if self.board[0][col] == 1
            ]
            target_row = self.size - 1

            # BFS desde cada pieza inicial
            for start in start_positions:
                visited = set()
                queue = [start]

                while queue:
                    row, col = queue.pop(0)
                    if row == target_row:  # Llegó al otro lado
                        return True

                    # Revisar las 6 casillas adyacentes
                    for dr, dc in [(0, 1), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, 1)]:
                        new_row, new_col = row + dr, col + dc

                        if (
                            0 <= new_row < self.size
                            and 0 <= new_col < self.size
                            and self.board[new_row][new_col] == 1
                            and (new_row, new_col) not in visited
                        ):

                            visited.add((new_row, new_col))
                            queue.append((new_row, new_col))

        else:  # Jugador 2 conecta este-oeste
            # Encontrar todas las piezas en la primera columna
            start_positions = [
                (row, 0) for row in range(self.size) if self.board[row][0] == 2
            ]
            target_col = self.size - 1

            # BFS desde cada pieza inicial
            for start in start_positions:
                visited = set()
                queue = [start]

                while queue:
                    row, col = queue.pop(0)
                    if col == target_col:  # Llegó al otro lado
                        return True

                    # Revisar las 6 casillas adyacentes
                    for dr, dc in [(0, 1), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, 1)]:
                        new_row, new_col = row + dr, col + dc

                        if (
                            0 <= new_row < self.size
                            and 0 <= new_col < self.size
                            and self.board[new_row][new_col] == 2
                            and (new_row, new_col) not in visited
                        ):

                            visited.add((new_row, new_col))
                            queue.append((new_row, new_col))

        return False
