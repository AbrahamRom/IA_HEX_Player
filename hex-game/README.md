# Hex Game

## Overview
Hex is a two-player abstract strategy game played on a hexagonal grid. The objective is to connect opposite sides of the board with a continuous path of one's own pieces. This project implements a Hex player using Monte Carlo Tree Search (MCTS) with Upper Confidence bounds for Trees (UCT) and an A* algorithm for pathfinding.

## Project Structure
- `src/MCSPlayer.py`: Contains the implementation of the Hex player classes, including `MCSPlayer`, `MCS_UCT_Player`, and a new player class that uses the A* algorithm.
- `src/basic_classes.py`: Defines the base classes and methods necessary for the game, including the `Player` class.
- `src/astar_utils.py`: Contains utility functions and classes related to the A* algorithm.
- `tests/test_hex_player.py`: Includes unit tests for the Hex player classes.

## Setup
To set up the project, ensure you have Python installed. Clone the repository and install the required dependencies.

```bash
pip install -r requirements.txt
```

## Running Tests
To run the tests, use the following command:

```bash
pytest tests/test_hex_player.py
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.