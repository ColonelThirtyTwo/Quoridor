"""
Board class to store the board's state
Author: Alex Parrill (amp9612@rit.edu)
"""

from Model.interface import BOARD_DIM
from .directions import Directions
from .binheap import BinaryHeapMap

# Heuristic and isgoal functions for each of the four goal rows
_goal_settings = [
    (lambda loc: abs(loc[0]), lambda loc: loc[0] == 0),
    (lambda loc: BOARD_DIM-1-abs(loc[0]), lambda loc: loc[0] == BOARD_DIM-1),
    # TODO: Verify that player 3 goes to the right and player 4 goes to the left
    (lambda loc: BOARD_DIM-1-abs(loc[1]), lambda loc: loc[1] == BOARD_DIM-1),
    (lambda loc: abs(loc[1]), lambda loc: loc[1] == 0)
]

class Player:
    """
    Player object.
    """
    def __init__(self, id, location, walls):
        """
        id: Base-zero Player id
        location: Current location of player
        walls: Number of walls the player has left
        """
        self.id = id
        self.location = location
        self.walls = walls

class TempWallView:
    """
    A view object for temporairly setting a wall in a board without modifying the underlying
    board bytearr or creating a clone of it. Used during wall validity checking to be able
    to pathfind with the wall without actually adding it.
    """
    def __init__(self, board, wall):
        self.board = board
        self.wall = wall
    
    def __getitem__(self, i):
        r = i // BOARD_DIM
        c = i % BOARD_DIM
        w = self.wall
        if w.isHoriz() and c >= w.c1 and c < w.c2:
            if r == w.r1:
                return self.board[i] | Directions.UP
            elif r == w.r1 - 1:
                return self.board[i] | Directions.DOWN
        elif w.isVert() and r >= w.r1 and r < w.r2:
            if c == w.c1:
                return self.board[i] | Directions.LEFT
            elif c == w.c1 - 1:
                return self.board[i] | Directions.RIGHT
        return self.board[i]

class Board:
    """
    A representation of the quoridor board.
    """
    
    def __init__(self, board, walls, players, turn):
        """
        board: bytearray representation of the board
        walls: list of Wall objects
        players: list of Player objects, in the order of their turns
        turn: index of players argument of the player whose turn it is
        """
        self.board = board
        self.walls = walls
        self.players = players
        self.turn = turn

    ############################################################################################
    # Helper functions
    
    def getPlayer(self, plyid):
        """
        Returns the player object with the given playerid
        """
        for i in self.players:
            if i.id == plyid:
                return i
    
    def removePlayer(self, plyid):
        """
        Removes the player from the board.
        """
        for i,p in enumerate(self.players):
            if p.id == plyid:
                self.players.pop(i)

    def getAdjacent(self, loc):
        """
        Returns a list of all adjacent spaces that can be accessed from this space.
            loc: (r,c) location
        """
        adj = []
        for d in Directions.LIST:
            newloc = self.getMoveTo(loc, d)
            if newloc: adj.append(newloc)
        return adj

    def getMoveTo(self, loc, d):
        """
        getMoveTo: (r,c), Direction -> (r,c)
        Returns the location ajacent to the specified location in the direction of the passed Direction, or
        None if it is not possible to move in that direction
        """
        if self[loc] & d != 0: return None # Blocked
        r,c = loc[0]+Directions.TO_ADJ[d][0], loc[1]+Directions.TO_ADJ[d][1]
        if r < 0 or r >= BOARD_DIM or c < 0 or c >= BOARD_DIM:
            return None # Out of bounds
        return (r,c)
    
    def checkWall(self, wall):
        """
        Checks if a wall is valid. This includes:
        1. All the checks done by wall.isValid
        2. It does not intersect with any other walls
        3. It does not cut off a player's path
        """
        if not wall.isValid():
            return False
        
        for i in self.walls:
            if wall.intersects(i):
                return False
        
        # Temporairly 'add' the wall and make sure players can still get to their goals
        board = self.board
        try:
            self.board = TempWallView(board, wall)
            for ply in self.players:
                if self.findPathToGoal(ply.location, ply.id) == None:
                    return False
        finally:
            # Make sure we put it back
            self.board = board
        
        return True

    def copy(self):
        """
        Creates a shallow copy of the player data.
        """
        new = Board.__new__(Board) # Create a new object without calling __init__

        # Copy over attributes
        new.board = self.board.copy()
        new.walls = self.walls.copy()
        new.players = self.players.copy()
        new.turn = self.turn

        return new

    def __getitem__(self, loc):
        """
        __getitem__: (r,c) -> int
        Returns the bitflags at the specified location
        """
        if loc[0] < 0 or loc[0] >= BOARD_DIM or loc[1] < 0 or loc[1] >= BOARD_DIM:
            raise IndexError("Invalid location: %d,%d" % (loc[0], loc[1]))
        return self.board[loc[0]*BOARD_DIM+loc[1]]

    def __setitem__(self, loc, v):
        """
        __setitem__: (r,c), int
        Sets the bitflags at the specified location
        """
        if loc[0] < 0 or loc[0] >= BOARD_DIM or loc[1] < 0 or loc[1] >= BOARD_DIM:
            raise IndexError("Invalid location: %d,%d" % (loc[0], loc[1]))
        self.board[loc[0]*BOARD_DIM+loc[1]] = v
        
    def __str__(self):
        b = "    "
        for i in range(BOARD_DIM):
            b += "{:2}   ".format(i)
        b += "\n    " + "LDRU "*BOARD_DIM + "\n"
        for r in range(BOARD_DIM):
            b += "{:2}  ".format(r)
            for c in range(BOARD_DIM):
                b += "{:04b} ".format(self[r,c])
            b += "\n"

        result = "Board="+b
        
        return result

    ############################################################################################
    # Update Functions

    def updatePlayerLocation(self, plyid, loc):
        """
        updatePlayerLocation: int, (r,c)
        Updates a player's location.
        """
        self.getPlayer(plyid).location = loc

    def addWall(self, wall):
        """
        addWall: Wall -> Boolean
        Adds a wall to the internal board representation.
        Assumes the wall is valid.
        """
        if wall.isHoriz():
            # Horizontal wall
            for i in range(wall.c1, wall.c2):
                self[wall.r1  ,i] |= Directions.UP
                self[wall.r1-1,i] |= Directions.DOWN
        else:
            # Vertical wall
            for i in range(wall.r1, wall.r2):
                self[i,wall.c1  ] |= Directions.LEFT
                self[i,wall.c1-1] |= Directions.RIGHT
        self.walls.append(wall)
        self.getPlayer(wall.owner).walls -= 1

    ############################################################################################
    # Pathfinding

    def _astar(self, start, heuristic, atgoal):
        """
        _astar: (r,c), int function(loc), bool function(loc) -> list
        Generic A* Algorithm.
            start: Starting point
            heuristic: function that takes a location and returns its heuristic score
            atgoal: function that takes a location and returns true if that location is a destination
        Returns a list of (r,c) tuples representing the path, or None if no path exists
        """
        nclosed = set()
        nopen = BinaryHeapMap()
        nopen.add(start, 0)
        came_from = {start : None}
        g_score = {start : 0}
        
        while nopen:
            current, _ = nopen.pop()
            if atgoal(current):
                l = []
                while current != None:
                    l.append(current)
                    current = came_from[current]
                l.reverse()
                return l
            nclosed.add(current)
            for i in self.getAdjacent(current):
                if i in nclosed:
                    continue
                i_gscore = g_score[current] + 1
                isopen = i in nopen
                if not isopen or g_score[i] > i_gscore:
                    came_from[i] = current
                    g_score[i] = i_gscore
                    if not isopen:
                        nopen.add(i, g_score[i]+heuristic(i))
                    else:
                        nopen.update(i, g_score[i]+heuristic(i))
        # Explored all reachable nodes, path doesn't exist.
        return None
        
    def findPathToLoc(self, start, dest):
        """
        findPathToLoc: (r,c), (r,c) -> list
        Finds the shortest valid path from start to dest, inclusive.
        Returns:
            a list of (r,c) tuples representing the path.
        """
        def heuristic(loc):
            return abs(dest[0]-loc[0]) + abs(dest[1]-loc[1])
        def atgoal(loc):
            return loc == dest
        return self._astar(start, heuristic, atgoal)
    
    def findPathToGoal(self, start, goalnum):
        """
        findPathToGoal: (r,c) -> list
        Finds the shortest valid path to the goal
        """
        heuristic, atgoal = _goal_settings[goalnum]
        return self._astar(start, heuristic, atgoal)
