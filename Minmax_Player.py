from basic_classes import Player, HexBoard
import copy


class MinMaxPlayer(Player):
    def __init__(self, player_id, depth=3):
        super().__init__(player_id)
        self.depth = depth
        self.opponent_id = (
            3 - player_id
        )  # If player_id is 1, opponent is 2 and vice versa

    def play(self, board):
        """Selects the best move using MinMax with alpha-beta pruning"""
        best_score = float("-inf")
        best_move = None
        alpha = float("-inf")
        beta = float("inf")

        # Try each possible move
        for move in board.get_possible_moves():
            # Create a copy of the board and make the move

            # print(f"\n {type(board)} \n")

            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id)

            # print(f"\n {type(new_board)} \n")

            # Get score for this move
            score = self.min_value(new_board, self.depth - 1, alpha, beta)

            # Update best move if necessary
            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        return best_move

    def min_value(self, board, depth, alpha, beta):
        """Minimizing player's turn (opponent)"""
        # Check terminal conditions
        if board.check_connection(self.player_id):
            return 1000  # Win for max player
        if board.check_connection(self.opponent_id):
            return -1000  # Win for min player
        if depth == 0:
            return self.evaluate_board(board)

        value = float("inf")

        # Try each possible move
        for move in board.get_possible_moves():
            # Create a copy and make the move
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.opponent_id)

            # Recursively get the value
            value = min(value, self.max_value(new_board, depth - 1, alpha, beta))

            # Alpha-beta pruning
            if value <= alpha:
                return value
            beta = min(beta, value)

        return value

    def max_value(self, board, depth, alpha, beta):
        """Maximizing player's turn (self)"""
        # Check terminal conditions
        if board.check_connection(self.player_id):
            return 1000  # Win for max player
        if board.check_connection(self.opponent_id):
            return -1000  # Win for min player
        if depth == 0:
            return self.evaluate_board(board)

        value = float("-inf")

        # Try each possible move
        for move in board.get_possible_moves():
            # Create a copy and make the move
            new_board = board.clone()
            new_board.place_piece(move[0], move[1], self.player_id)

            # Recursively get the value
            value = max(value, self.min_value(new_board, depth - 1, alpha, beta))

            # Alpha-beta pruning
            if value >= beta:
                return value
            alpha = max(alpha, value)

        return value

    def evaluate_board(self, board):
        """Evaluates the current board state"""
        score = 0
        size = board.size

        # Evaluate based on position control
        for row in range(size):
            for col in range(size):
                if board.board[row][col] == self.player_id:
                    # Add points for controlling center positions
                    center_control = (
                        1 - (abs(row - size // 2) + abs(col - size // 2)) / size
                    )
                    score += center_control

                    # Add points for pieces forming connections
                    connected_allies = self.count_connected_allies(board, row, col)
                    score += connected_allies

                elif board.board[row][col] == self.opponent_id:
                    # Subtract points for opponent's pieces
                    center_control = (
                        1 - (abs(row - size // 2) + abs(col - size // 2)) / size
                    )
                    score -= center_control

                    # Subtract points for opponent's connections
                    connected_allies = self.count_connected_allies(board, row, col)
                    score -= connected_allies

        # Add bonus for controlling key paths
        if self.player_id == 1:  # North-South player
            score += self.evaluate_vertical_paths(board)
        else:  # East-West player
            score += self.evaluate_horizontal_paths(board)

        return score

    def count_connected_allies(self, board, row, col):
        """Counts the number of allied pieces adjacent to the given position"""
        count = 0
        directions = [(0, 1), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, 1)]
        player = board.board[row][col]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (
                0 <= new_row < board.size
                and 0 <= new_col < board.size
                and board.board[new_row][new_col] == player
            ):
                count += 1

        return count

    def evaluate_vertical_paths(self, board):
        """Evaluates potential paths from north to south"""
        score = 0
        size = board.size

        # Check each column
        for col in range(size):
            consecutive = 0
            for row in range(size):
                if board.board[row][col] == self.player_id:
                    consecutive += 1
                elif board.board[row][col] == self.opponent_id:
                    consecutive = 0
            score += consecutive * 2

        return score * 3

    def evaluate_horizontal_paths(self, board):
        """Evaluates potential paths from east to west"""
        score = 0
        size = board.size

        # Check each row
        for row in range(size):
            consecutive = 0
            for col in range(size):
                if board.board[row][col] == self.player_id:
                    consecutive += 1
                elif board.board[row][col] == self.opponent_id:
                    consecutive = 0
            score += consecutive * 2

        return score * 3
