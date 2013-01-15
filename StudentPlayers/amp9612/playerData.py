"""
Player data to store the AI's state.
Author: Alex Parrill (amp9612@rit.edu)
"""

from Model.interface import BOARD_DIM, PlayerMove
from .wall import Wall
from .directions import Directions
from .board import Board, Player
import random

inf = float("inf")

def randomWall(plyid):
    """
    Generates a random wall, owned by plyid.
    May not be valid.
    """
    start_r = random.randint(0, BOARD_DIM)
    start_c = random.randint(0, BOARD_DIM)
    if random.getrandbits(1) == 0:
        end_r = start_r + 2
        end_c = start_c
    else:
        end_r = start_r
        end_c = start_c + 2
    return Wall(plyid, start_r, start_c, end_r, end_c)

def alphabeta(board, depth, plyid, a=-inf, b=inf, curplyid=None):
    """
    Generates and runs through a decision tree using minimax and alpha-beta pruning
    http://en.wikipedia.org/wiki/Minimax and http://en.wikipedia.org/wiki/Alpha-beta_pruning
        board: Starting configuration
        depth: Pile depth to search
        plyid: Starting player's id
        a: Recursive parameter, don't use
        b: Recursive parameter, don't use
        curplyid: Recursive parameter, don't use
    Returns: A dictionary tree with move : (node, score) entries of all the branches visited
    """
    curplyid = curplyid or plyid
    
    if depth <= 0 or board.isTerminal():
        return board, board.evaluate(plyid)
    
    # Compute next ID
    nextid = (curplyid+1) % len(board.players)
    while not board.getPlayer(nextid):
        nextid = (nextid+1) % len(board.players)
    
    treenode = {}
    
    if curplyid == plyid:
        # Max
        for move in board.generateNext(curplyid):
            #print("max: examining "+str(move))
            tree, score = alphabeta(board.copy().applyMove(move), depth-1, plyid, a, b, nextid)
            treenode[move] = (tree, score)
            a = max(a, score)
            if b < a:
                break
        return treenode, a
    else:
        # Min
        for move in board.generateNext(curplyid):
            #print("min: examining "+str(move))
            tree, score = alphabeta(board.copy().applyMove(move), depth-1, plyid, a, b, nextid)
            treenode[move] = (tree, score)
            b = min(b, score)
            if b < b:
                break
        return treenode, b

import cProfile
global temp
def alphabeta_wrapper(*args, **kwargs):
    global temp
    temp = alphabeta(*args, **kwargs)

class PlayerData:
    """
    State for the quoridor game
    """
    
    def __init__(self, plyid, numwalls, plylocs):
        """
        plyid: Base-zero player id
        numwalls: Starting number of walls for each player
        plylocs: Iterable of player locations
        """
        plys = []
        for id, pos in enumerate(plylocs):
            if pos:
                p = Player(id, pos, numwalls)
                plys.append(p)
            else:
                plys.append(None)
        self.myid = plyid
        self.currentboard = Board(bytearray(BOARD_DIM*BOARD_DIM), [], plys)
        self.placewall = False
    
    def applyMove(self, move):
        """
        Updates the internal board representation with a PlayerMove object
        """
        self.currentboard.applyMove(move)
    
    def getMove(self):
        """
        Returns the move the player should make
        """
        #tree, _ = alphabeta(self.currentboard, 3, self.myid)
        cProfile.runctx("alphabeta_wrapper(self.currentboard, 1, self.myid)", globals(), locals(), "profile.out")
        tree, _ = temp
        move, _ = min(tree.items(), key=lambda n: n[1][1])
        return move
    
    def invalidatePlayer(self, plyid):
        """
        Removes the player from the board
        """
        self.currentboard.removePlayer(plyid)
    
        
