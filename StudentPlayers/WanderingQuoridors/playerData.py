"""
Representation of a quoridor board
Author: Alex Parrill (amp9612@rit.edu)
Author: Joseph Moreyn (jbm6331@rit.edu)
"""

from Model.interface import BOARD_DIM, PlayerMove
from .binheap import BinaryHeapMap
from .wall import Wall
from collections import deque
import random

# Heuristic and isgoal functions for each of the four goal rows
_goal_settings = [
    (lambda loc: abs(loc[0]), lambda loc: loc[0] == 0),
    (lambda loc: BOARD_DIM-1-abs(loc[0]), lambda loc: loc[0] == BOARD_DIM-1),
    # TODO: Verify that player 3 goes to the right and player 4 goes to the left
    (lambda loc: BOARD_DIM-1-abs(loc[1]), lambda loc: loc[1] == BOARD_DIM-1),
    (lambda loc: abs(loc[1]), lambda loc: loc[1] == 0)
]

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
    A representation of the quoridor board.
    """
    
    def __init__(self, playerId, numWalls, playerLocations):
        """
        playerId: my player ID (0-3)
        numWalls: Number of walls we have
        playerLocations: list of player coordinates
        """
        self.playerId = playerId
        self.numWalls = numWalls
        self.playerLocations = playerLocations
        
        self.board = {}
        self.walls = []
        self.placewall = False
        
        # Build board
        tmplist = []
        for r in range(BOARD_DIM):
            for c in range(BOARD_DIM):
                if r != 0:           tmplist.append((r-1,c))
                if r != BOARD_DIM-1: tmplist.append((r+1,c))
                if c != 0:           tmplist.append((r,c-1))
                if c != BOARD_DIM-1: tmplist.append((r,c+1))
                self.board[r,c] = frozenset(tmplist)
                tmplist.clear()

    ############################################################################################
    # Helper functions

    def getAdjacentHop(self, loc):
        """
        Iterates over all adjacent spaces that can be accessed from this space,
        also computing moves where players can hop over each other
            loc: (r,c) location
        """
        for loc2 in self.board[loc]:
            if self.playerAt(loc2):
                loc3 = loc2[0]*2-loc[0], loc2[1]*2-loc[1]
                if loc3 in self.board[loc2] and not self.playerAt(loc3):
                    yield loc3
                else:
                    for loc4 in self.board[loc2]:
                        if loc4 != loc:
                            yield loc4
            else:
                yield loc2

    def playerAt(self, loc):
        """
        Returns if a player is at a specified location
        """
        for p in self.playerLocations:
            if p == loc:
                return True

    def getMyPos(self):
        """
        Returns our position.
        """
        return self.playerLocations[self.playerId]

    def copy(self):
        """
        Creates a clone of the player data.
        """
        new = PlayerData.__new__(PlayerData) # Create a new player object without calling __init__

        # Copy over attributes
        new.playerId = self.playerId
        new.numWalls = self.numWalls
        new.playerLocations = self.playerLocations.copy()
        new.board = self.board.copy()
        new.walls = self.walls.copy()
        new.placewall = self.placewall

        return new
        
    def __str__(self):
        """
        __str__: PlayerData -> string
        Returns a string representation of the PlayerData object.
            self - the PlayerData object
        """
        
        b = str(self.board)

        result = "PlayerData= " \
                    + "playerId: " + str(self.playerId) \
                    + ", playerLocations: " + str(self.playerLocations) \
                    + ", numPlayers:" + str(len(self.playerLocations)) + ", board:\n" \
                    + b
                
        return result

    ############################################################################################
    # Update Functions

    def updatePlayerLocation(self, plyid, loc):
        """
        updatePlayerLocation: int, (r,c)
        Updates a player's location.
        """
        self.playerLocations[plyid-1] = loc
        if plyid-1 == self.playerId:
            self.placewall = True
    
    def checkWall(self, wall):
        """
        Returns True if wall can be successfully placed
        """
        if not wall.isValid():
            return False
        
        for i in self.walls:
            if wall.intersects(i):
                return False
        
        board = self.board
        try:
            self.board = board.copy()
            self.addWall(wall, True)
            for i, loc in enumerate(self.playerLocations):
                if loc and self.findPathToGoal(loc, i) == None:
                    return False
        finally:
            self.board = board
        
        return True
    
    def addWall(self, wall, onlytoboard=False):
        """
        Adds a wall to the internal board representation. Assumes the wall is valid and can be added
        
        onlytoboard is an internal parameter and should not be used.
        """

        if wall.isHoriz():
            # Horizontal wall
            self.board[wall.r1  ,wall.c1  ] = self.board[wall.r1  ,wall.c1  ].difference(((wall.r1-1,wall.c1  ),))
            self.board[wall.r1  ,wall.c1+1] = self.board[wall.r1  ,wall.c1+1].difference(((wall.r1-1,wall.c1+1),))
            self.board[wall.r1-1,wall.c1  ] = self.board[wall.r1-1,wall.c1  ].difference(((wall.r1  ,wall.c1  ),))
            self.board[wall.r1-1,wall.c1+1] = self.board[wall.r1-1,wall.c1+1].difference(((wall.r1  ,wall.c1+1),))
        else:
            # Vertical wall
            self.board[wall.r1  ,wall.c1  ] = self.board[wall.r1  ,wall.c1  ].difference(((wall.r1  ,wall.c1-1),))
            self.board[wall.r1+1,wall.c1  ] = self.board[wall.r1+1,wall.c1  ].difference(((wall.r1+1,wall.c1-1),))
            self.board[wall.r1  ,wall.c1-1] = self.board[wall.r1  ,wall.c1-1].difference(((wall.r1  ,wall.c1  ),))
            self.board[wall.r1+1,wall.c1-1] = self.board[wall.r1+1,wall.c1-1].difference(((wall.r1+1,wall.c1  ),))
                
        if not onlytoboard:
            self.walls.append(wall)
            if wall.owner == self.playerId + 1:
                self.numWalls -= 1
                self.placewall = False

    def getMove(self):
        """
        Returns the PlayerMove object representing the move that the player should make
        """

        if self.placewall and self.numWalls > 0:
            # Generate a wall
            while True:
                w = randomWall(self.playerId + 1)
                if self.checkWall(w):
                    break
            return w.toMove()
        else:
            # Move along the shortest path
            mypos = self.getMyPos()
            path = self.findPathToGoal(mypos, self.playerId)
            if not path:
                raise RuntimeError("No path to goal!")
            elif len(path) >= 2:
                return PlayerMove(self.playerId + 1, True, mypos[0], mypos[1], path[1][0], path[1][1])
            else:
                return None


    ############################################################################################
    # Pathfinding

    def _bfs(self, start, atgoal):
        """
        Generic BFS Algorithm
            start: Starting point
            atgoal: function that takes a location and returns true if that location is a destination
        Returns a list of (r,c) tuples representing the path, or None if no path exists
        """
        queue = deque()
        queue.append(start)
        closed = {start : None}
        while queue:
            current = queue.popleft()
            if atgoal(current):
                l = []
                while current != None:
                    l.append(current)
                    current = closed[current]
                l.reverse()
                return l
            for i in self.board[current]:
                if i not in closed:
                    closed[i] = current
                    queue.append(i)
        return None
        
    def findPathToLoc(self, start, dest):
        """
        findPathToLoc: (r,c), (r,c) -> list
        Finds the shortest valid path from start to dest, inclusive.
        Returns:
            a list of (r,c) tuples representing the path.
        """
        def atgoal(loc):
            return loc == dest
        return self._bfs(start, atgoal)
    
    def findPathToGoal(self, start, goalnum):
        """
        findPathToGoal: (r,c) -> list
        Finds the shortest valid path to the goal
        """
        heuristic, atgoal = _goal_settings[goalnum]
        return self._bfs(start, atgoal)
