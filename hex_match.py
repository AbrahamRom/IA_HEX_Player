from hexboard import MyBoard
from player import MyPlayer
import time


def play_game(board_size: int = 11) -> int:
    """
    Play a game of Hex between two AI players
    Returns the winner's ID (1 or 2)
    """
    # Initialize board and players
    board = MyBoard(board_size)
    player1 = MyPlayer(1)
    player2 = MyPlayer(2)

    current_player = player1
    turn = 1

    while True:
        # Get and execute the current player's move
        move = current_player.play(board)
        board.place_piece(move[0], move[1], current_player.player_id)

        # Print the current state and board
        board.print_board()
        print(f"Turn {turn}: Player {current_player.player_id} placed at {move}")
        time.sleep(1)

        # Check for victory
        if board.check_connection(current_player.player_id):
            print(f"Player {current_player.player_id} wins!")
            return current_player.player_id

        # Switch players
        current_player = player2 if current_player == player1 else player1
        turn += 1


if __name__ == "__main__":
    print("Starting Hex match...")
    winner = play_game()
    print(f"Game finished! Player {winner} is the winner!")
