from hexboard import MyBoard
from player import BadPlayer, ManhattanPlayer, AsPlayer
from UCSPlayer import UCSPlayer
from A_star_player import AStarPlayer
import time
from tabulate import tabulate


def play_match(player1, player2, board_size):
    board = MyBoard(board_size)
    current_player = player1
    turn = 1
    p1_time = 0
    p2_time = 0

    while True:
        start_time = time.time()
        move = current_player.play(board)
        end_time = time.time()

        # Track time for the current player
        if current_player == player1:
            p1_time += end_time - start_time
        else:
            p2_time += end_time - start_time

        board.place_piece(move[0], move[1], current_player.player_id)

        if board.check_connection(current_player.player_id):
            return current_player.player_id, p1_time, p2_time

        current_player = player2 if current_player == player1 else player1
        turn += 1


def play_tournament(player1, player2, board_size, num_games: int = 10) -> None:
    """
    Play a tournament of multiple Hex games and track the results
    """
    p1_wins = 0
    p2_wins = 0
    p1_total_time = 0
    p2_total_time = 0

    for game in range(num_games):
        print(f"\nGame {game + 1} of {num_games}")
        winner, p1_time, p2_time = play_match(player1, player2, board_size)
        p1_total_time += p1_time
        p2_total_time += p2_time

        if winner == 1:
            p1_wins += 1
        else:
            p2_wins += 1

    # Prepare data for the table
    headers = ["Metric", "Player 1", "Player 2"]
    data = [
        ["Wins", p1_wins, p2_wins],
        ["Total time (s)", f"{p1_total_time:.2f}", f"{p2_total_time:.2f}"],
        [
            "Avg time/game (s)",
            f"{p1_total_time/num_games:.2f}",
            f"{p2_total_time/num_games:.2f}",
        ],
    ]

    print("\nTournament Results:")
    print(tabulate(data, headers=headers, tablefmt="grid"))


def play_game(board_size: int = 19) -> int:
    """
    Play a game of Hex between two AI players
    Returns the winner's ID (1 or 2)
    """
    # Initialize board and players
    board = MyBoard(board_size)
    player1 = AStarPlayer(1)
    player2 = UCSPlayer(2)

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
            # return current_player.player_id
            break

        # Switch players
        current_player = player2 if current_player == player1 else player1
        turn += 1

    play_tournament(player1, player2, board_size, num_games=10)


if __name__ == "__main__":
    print("Starting Hex match...")
    winner = play_game()
    # print(f"Game finished! Player {winner} is the winner!")
