"""
Board class to store the board's state
Author: Alex Parrill (amp9612@rit.edu)
"""

from Model.interface import PlayerMove, BOARD_DIM
from .directions import Directions
from .wall import Wall
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
    
    def copy(self):
        """
        Creates a copy of self
        """
        return Player(self.id, self.location, self.walls)
    
    def __str__(self):
        return "Player({0},{1},{2})".format(self.id, self.location, self.walls)
    __repr__ = __str__

class Board:
    """
    A representation of the quoridor board.
    """
    
    def __init__(self, board, walls, players):
        """
        board: bytearray representation of the board
        walls: list of Wall objects
        players: list of Player objects, in the order of their turns
        """
        self.board = board
        self.walls = walls
        self.players = players

    ############################################################################################
    # Misc functions
    
    def getPlayer(self, plyid):
        """
        Returns the player object with the given playerid
        """
        return self.players[plyid]
    
    def removePlayer(self, plyid):
        """
        Removes the player from the board.
        """
        self.players[plyid] = None

    def getAdjacent(self, loc):
        """
        Returns a generator of all adjacent spaces that can be accessed from this space.
        This will go through players without hopping over them.
        """
        mask = self[loc]
        if mask & Directions.UP    == 0 and loc[0] > 0:
            yield loc[0]-1, loc[1]
        if mask & Directions.DOWN  == 0 and loc[0] < BOARD_DIM-1:
            yield loc[0]+1, loc[1]
        if mask & Directions.LEFT  == 0 and loc[1] > 0:
            yield loc[0], loc[1]-1
        if mask & Directions.RIGHT == 0 and loc[1] < BOARD_DIM-1:
            yield loc[0], loc[1]+1

    def getAdjacentHop(self, loc):
        """
        Returns a generator of all adjacent spaces that can be accessed from this space.
            loc: (r,c) location
        """
        for d in Directions.LIST:
            if self[loc] & d != 0:
                continue
            newloc = loc[0]+Directions.TO_ADJ[d][0], loc[1]+Directions.TO_ADJ[d][1]
            if newloc[0] < 0 or newloc[0] >= BOARD_DIM or newloc[1] < 0 or newloc[1] >= BOARD_DIM:
                continue
            
            # Weird moves when a player is blocking
            ply = None
            for p in self.players:
                if p and p.location == newloc and p.location != loc:
                    ply = p
                    break
            if ply:
                if self[newloc] & d == 0:
                    # Can 'jump over' the player
                    newloc = loc[0]+Directions.TO_ADJ[d][0], loc[1]+Directions.TO_ADJ[d][1]
                    if newloc[0] < 0 or newloc[0] >= BOARD_DIM or newloc[1] < 0 or newloc[1] >= BOARD_DIM:
                        continue
                    yield newloc
                else:
                    d1, d2 = Directions.PERPENDICULAR[d]
                    if self[newloc] & d1 == 0:
                        newloc2 = loc[0]+Directions.TO_ADJ[d1][0], loc[1]+Directions.TO_ADJ[d1][1]
                        if newloc2[0] >= 0 and newloc2[0] < BOARD_DIM and newloc2[1] >= 0 and newloc2[1] < BOARD_DIM:
                            yield newloc2
                    if self[newloc] & d2 == 0:
                        newloc2 = loc[0]+Directions.TO_ADJ[d2][0], loc[1]+Directions.TO_ADJ[d2][1]
                        if newloc2[0] >= 0 and newloc2[0] < BOARD_DIM and newloc2[1] >= 0 and newloc2[1] < BOARD_DIM:
                            yield newloc2
            else:
                yield newloc
    
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
            self.board = self.board.copy()
            self.addWall(wall, True)
            for ply in self.players:
                if ply and self.findPathToGoal(ply.location, ply.id) == None:
                    return False
        finally:
            # Make sure we put it back
            self.board = board
        
        return True

    def copy(self):
        """
        Creates a copy of the player data.
        """
        new = Board.__new__(Board) # Create a new object without calling __init__

        # Copy over attributes
        new.board = self.board.copy()
        new.walls = self.walls.copy() # Wall are immutable, so they don't need to be deep copied
        new.players = [p and p.copy() or p for p in self.players]

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
    
    def applyMove(self, move):
        """
        Calls either updatePlayerLocation or addWall with values from the passed PlayerMove object.
        """
        if move.move:
            self.updatePlayerLocation(move.playerId-1, (move.r2, move.c2))
        else:
            w = Wall(move.playerId-1, move.r1, move.c1, move.r2, move.c2)
            assert(self.checkWall(w))
            self.addWall(w)
        return self
        
    def updatePlayerLocation(self, plyid, loc):
        """
        updatePlayerLocation: int, (r,c)
        Updates a player's location.
        """
        self.getPlayer(plyid).location = loc

    def addWall(self, wall, byteonly=False):
        """
        addWall: Wall -> Boolean
        Adds a wall to the internal board representation.
        Assumes the wall is valid.
            wall: Wall to add
            byteonly: Internal use only
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

        if not byteonly:
            self.walls.append(wall)
            self.getPlayer(wall.owner).walls -= 1
        
    ############################################################################################
    # AI functions
    
    def isTerminal(self):
        """
        If a player is on one of the goal spaces, returns that player.
        Otherwise, returns None
        """
        for p in self.players:
            if _goal_settings[p.id][1](p.location):
                return p
        return None
    
    def evaluate(self, plyid):
        """
        Estimates how well off plyid is in the current situation.
        """
        # TODO: This can probably be tweaked
        score = 0
        for p in self.players:
            s = len(self.findPathToGoal(p.location, p.id))
            if p.id == plyid:
                score -= s
            else:
                score += s
        return s
    
    def generateNext(self, plyid):
        """
        Returns a generator that yields every possible PlayerMove from this configuration by
        player plyid
        """
        ply = self.getPlayer(plyid)
        
        # Movement
        for loc in self.getAdjacent(ply.location):
            yield PlayerMove(ply.id+1, True, ply.location[0], ply.location[1], loc[0], loc[1])
        
        if ply.walls != 0:
            # Vertical walls
            for c in range(1, BOARD_DIM):
                for r in range(0, BOARD_DIM-1):
                    w = Wall(ply.id+1, r, c, r+2, c)
                    if self.checkWall(w):
                        yield w.toMove()
            # Horizontal walls
            for r in range(1, BOARD_DIM):
                for c in range(0, BOARD_DIM-1):
                    w = Wall(ply.id+1, r, c, r, c+2)
                    if self.checkWall(w):
                        yield w.toMove()
    
    ############################################################################################
    # Pathfinding

    def _astar(self, start, heuristic, atgoal):
        """
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
        Finds the shortest valid path to the goal
        """
        heuristic, atgoal = _goal_settings[goalnum]
        return self._astar(start, heuristic, atgoal)
