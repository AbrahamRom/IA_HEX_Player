from hexboard import MyBoard

from best_players import MonteCarloHexPlayer as RavePlayer
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
    Play a tournament of multiple Hex games and track the results.
    Half of the games will be started by player1 and half by player2.
    """
    p1_wins = 0
    p2_wins = 0
    p1_total_time = 0
    p2_total_time = 0

    # Calculate number of games for each starting position
    games_per_player = num_games // 2
    remaining_games = num_games % 2  # In case of odd number of games

    for game in range(num_games):
        print(f"\nGame {game + 1} of {num_games}")

        # Determine starting player based on game number
        if game < games_per_player:
            first_player = player1
            second_player = player2
            print("Player 1 starts")
        else:
            first_player = player2
            second_player = player1
            print("Player 2 starts")

        winner, p1_time, p2_time = play_match(first_player, second_player, board_size)
        p1_total_time += p1_time
        p2_total_time += p2_time

        if winner == 1:
            p1_wins += 1
            print(f"Winner: Player 1 (Time: {p1_time:.2f}s)")
        else:
            p2_wins += 1
            print(f"Winner: Player 2 (Time: {p2_time:.2f}s)")

    # Prepare data for the table
    headers = ["Metric", "Player 1", "Player 2"]
    data = [
        ["Wins", p1_wins, p2_wins],
        ["Games starting first", games_per_player + remaining_games, games_per_player],
        ["Total time (s)", f"{p1_total_time:.2f}", f"{p2_total_time:.2f}"],
        [
            "Avg time/game (s)",
            f"{p1_total_time/num_games:.2f}",
            f"{p2_total_time/num_games:.2f}",
        ],
    ]

    print("\nTournament Results:")
    print(tabulate(data, headers=headers, tablefmt="grid"))


def play_game(board_size: int = 7) -> int:
    """
    Play a game of Hex between two AI players
    Returns the winner's ID (1 or 2)
    """
    # Initialize board and players
    board = MyBoard(board_size)
    # player1 = MCAEP(1, simulation_time=2.0)
    # player1 = MCSPlayer(1, simulation_time=2.0)
    # player1 = MCTHP(1, simulation_time=2.0)
    # player1 = MCTFAP(1, simulation_time=2.0)
    # player1 = MCTAsSP(1, simulation_time=2.0)
    player1 = RavePlayer(1, time_limit=2.0)

    player2 = RavePlayer(2, time_limit=2.0)

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
