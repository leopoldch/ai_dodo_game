import copy
import math
import random
import time
import numpy as np
from typing import Union


from dodo import create_board, init_board, legit_moves, move, final, score, print_board

Environment = dict
Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]  # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int  # 1 ou 2
State = list[tuple[Cell, Player]]  # État du jeu pour la boucle de jeu
Score = int
Time = int
Grid = dict[Cell:Player]

# Cache for possible actions
possible_actions_cache = {}

# Tree node class definition
class TreeNode:
    def __init__(self, state, player, parent=None):
        self.state = state
        self.parent = parent
        self.visits = 0
        self.score = 0
        self.children = {}
        self.player = player
        self.possibles_actions = self.get_possible_actions(state, player)

    def get_possible_actions(self, state, player):
        state_hash = hash(tuple(state))
        if (state_hash, player) in possible_actions_cache:
            return possible_actions_cache[(state_hash, player)]
        else:
            actions = legit_moves(state, player)
            possible_actions_cache[(state_hash, player)] = actions
            return actions

    def is_expanded(self):
        return len(self.possibles_actions) == 0

    def expand(self):
        action = self.possibles_actions.pop()
        possible_state = move(self.state, action, self.player)
        child = TreeNode(possible_state, 3 - self.player, self)
        self.children[action] = child
        return child

    def best_child(self, exploration_param=1.4):
        best_score = -float('inf')
        best_children = []

        for action, child in self.children.items():
            if child.visits == 0:
                score = float('inf')  # handle unvisited child nodes
            else:
                score = (child.score / child.visits) + exploration_param * np.sqrt(np.log(self.visits) / child.visits)
            if score > best_score:
                best_score = score
                best_children = [child]
            elif score == best_score:
                best_children.append(child)

        return random.choice(best_children)

    def backpropagation(self, score):
        self.visits += 1
        self.score += score
        if self.parent:
            self.parent.backpropagation(-score)

    def rollout(self, current_player):
        state = self.state
        while not final(state):
            actions = self.get_possible_actions(state, current_player)
            play = random.choice(actions)
            state = move(state, play, current_player)
            current_player = 3 - current_player
        return score(state, self.player)

    def select(self):
        current_node = self
        while not final(current_node.state):
            if current_node.is_expanded():
                current_node = current_node.best_child()
            else:
                return current_node.expand()
        return current_node

# MCTS class definition
class MCTS:
    def __init__(self, root):
        self.root = root

    def search(self, iterations):
        for _ in range(iterations):
            node = self.root.select()
            rollout_score = node.rollout(node.player)
            node.backpropagation(rollout_score)

        return self.root.best_child(0)  # only best, no exploration

def mcts(state, iterations, player):
    root = TreeNode(state, player)
    mcts = MCTS(root)
    best_child_node = mcts.search(iterations)
    for action, child in root.children.items():
        if child == best_child_node:
            return action

import time

def test(iterations: int, size: int):
    tps1 = time.time()
    stats1 = 0
    stats2 = 0
    for _ in range(iterations):
        current_player = 1
        board = create_board(size)
        state = init_board(board)
        while not final(state):
            if current_player == 1:
                play = mcts(state, 10, current_player)
                print("action:",play)
            else:
                play = random_strat(state, current_player)
            state = move(state, play, current_player)
            current_player = 3 - current_player

        if score(state, 1) == 1:
            stats1 += 1
        elif score(state, 2) == 1:
            stats2 += 1

    print(f"Execution time for {iterations} iterations: {time.time() - tps1:.4f} seconds")
    print(f"Games won by player 1: {(stats1/iterations)*100:.2f}%")
    print(f"Games won by player 2: {(stats2/iterations)*100:.2f}%")

def random_strat(state, current_player):
    actions = legit_moves(state, current_player)
    return random.choice(actions)

# Running the test
test(20, 7)