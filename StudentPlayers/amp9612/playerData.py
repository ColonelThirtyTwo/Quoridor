"""
Player data to store the AI's state.
Author: Alex Parrill (amp9612@rit.edu)
"""

from Model.interface import BOARD_DIM, PlayerMove
from .wall import Wall
from .directions import Directions
from .board import Board, Player
import random

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
        self.myid = plyid
        self.currentboard = Board(bytearray(BOARD_DIM*BOARD_DIM), [], plys, 0)
        self.placewall = False
    
    def applyMove(self, move):
        """
        Updates the internal board representation with a PlayerMove object
        """
        if move.move:
            self.currentboard.updatePlayerLocation(move.playerId-1, (move.r2, move.c2))
        else:
            w = Wall(move.playerId-1, move.r1, move.c1, move.r2, move.c2)
            assert(self.currentboard.checkWall(w))
            self.currentboard.addWall(w)
    
    def getMove(self):
        """
        Returns the move the player should make
        """
        p = self.currentboard.getPlayer(self.myid)
        if self.placewall and p.walls > 0:
            self.placewall = False
            while True:
                w = randomWall(self.myid + 1)
                if self.currentboard.checkWall(w):
                    break
            return w.toMove()
        else:
            self.placewall = True
            mypos = p.location
            path = self.currentboard.findPathToGoal(mypos, self.myid)
            if not path:
                raise RuntimeError("No path to goal!")
            elif len(path) >= 2:
                return PlayerMove(self.myid + 1, True, mypos[0], mypos[1], path[1][0], path[1][1])
            else:
                return None
    
    def invalidatePlayer(self, plyid):
        """
        Removes the player from the board
        """
        self.currentboard.removePlayer(plyid)
