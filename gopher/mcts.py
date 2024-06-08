import math
import random
from typing import List, Optional
from utils import *

class Node:
    def __init__(self, game, parent: Optional['Node'] = None, action: Optional[Action] = None) -> None:
        self.game = game
        self.parent: Node = parent
        self.action: Action = action
        self.children: List['Node'] = []
        self.visits: int = 0
        self.wins: int = 0

    def add_child(self, child: 'Node') -> None:
        self.children.append(child)

    def update(self, result: float):
        self.visits += 1
        self.wins += result

    def ucb1(self) -> float:
        coeff_value: float = 2
        if self.visits == 0:
            return float('inf')
        return self.wins / self.visits + coeff_value * (math.sqrt(2 * math.log(self.parent.visits) / self.visits))

class MCTS:
    def __init__(self, root_game) -> None:
        self.root = Node(root_game)

    def selection(self, node: Node) -> Node:
        while node.children:
            node = max(node.children, key=lambda child: child.ucb1())
        return node

    def expansion(self, node: Node) -> None:
        game = node.game
        legal_moves = game.get_legits()
        for move in legal_moves:
            tmp : dict = game.save_state()
            game.move(move)
            game.set_player(3 - game.get_player())
            child = Node(game, parent=node, action=move)
            node.add_child(child)
            game.restore_state(tmp)

    def simulation(self, game) -> float:
        state = game.save_state()
        while game.final():
            legal_moves = game.get_legits()
            move = random.choice(legal_moves)
            game.move(move)
            game.set_player(3 - game.get_player())
        result = game.score()
        game.restore_state(state)
        return result

    def backpropagation(self, node: Node, result: float) -> None:
        while node:
            node.update(result)
            node = node.parent

    def search(self, iterations: int) -> Action:
        for _ in range(iterations):
            node = self.selection(self.root)
            if node.game.final():
                self.expansion(node)
            result = self.simulation(node.game)
            self.backpropagation(node, result)

        if self.root.children:
            best_child = max(self.root.children, key=lambda child: child.wins / child.visits if child.visits != 0 else float('-inf'))
            return best_child.action
        else:
            raise ValueError("No children found after MCTS iterations. The game might be already won/lost or no legal moves are available.")

def mcts(game) -> Action:
    mcts_search = MCTS(game)
    return mcts_search.search(1000)
