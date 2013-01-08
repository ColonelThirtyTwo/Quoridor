"""
Quoridor II: Student Computer Player

A sample class you may use to hold your state data
Author: Adam Oest (amo9149@rit.edu)
Author: Alex Parrill (amp9612@rit.edu)
"""

from Model.interface import BOARD_DIM, PlayerMove
import random

class Directions:
    """
    Bitwise enumerations for representing directions
    """
    UP = 0x1
    RIGHT = 0x2
    DOWN = 0x4
    LEFT = 0x8
    
    LIST = (DOWN, RIGHT, UP, LEFT)
    TO_ADJ = {LEFT : (0,-1), RIGHT : (0,1), UP : (-1,0), DOWN : (1,0)}

class Wall:
    """
    A reprensentation of a wall.
    """
    def __init__(self, ownerid, r1, c1, r2, c2):
        self.owner = ownerid
        self.r1 = r1
        self.c1 = c1
        self.r2 = r2
        self.c2 = c2

    def loc1(self):
        """
        Returns the tuple (r1, c1)
        """
        return (self.r1, self.c1)
    
    def loc2(self):
        """
        Returns the tuple (r2, c2)
        """
        return (self.r2, self.c2)
    
    def isHoriz(self):
        """
        Returns true if wall is horizontal
        """
        return self.c1 == self.c1
    
    def isVert(self):
        """
        Returns true if wall is vertical
        """
        return self.r1 == self.r2
    
    def isValid(self):
        """
        Checks if the wall is valid, that is:
        1. Wall is axis aligned
        2. Wall coordinates are in the correct order
        3. Wall has a length of 2
        4. Wall is inside the board
        """
        return (self.r1 == self.r2 or self.c1 == self.c2) and \
            (self.r2 >= self.r1 and self.c2 >= self.c1) and \
            (self.r2-self.r1 + self.c2-self.c1 == 2) and \
            self.isInBoard()
    def isInBoard(self):
        """
        Helper function to isValid. Checks to see if the wall is inside the board.
        """
        if self.r1 < 0 or self.r1 > BOARD_DIM or self.c1 < 0 or self.c1 > BOARD_DIM or \
            self.r2 < 0 or self.r2 > BOARD_DIM or self.c2 < 0 or self.c2 > BOARD_DIM:
            # There is a coordinate outside the board
            return False

        bordercoords = 0
        # Check to see if we have no more than one coordinate on a border
        if self.r1 == 0 or self.r1 == BOARD_DIM:
            bordercoords += 1
        if self.c1 == 0 or self.c1 == BOARD_DIM:
            bordercoords += 1
        if self.r2 == 0 or self.r2 == BOARD_DIM:
            bordercoords += 1
        if self.c2 == 0 or self.c2 == BOARD_DIM:
            bordercoords += 1
        return bordercoords <= 1
    
    def intersects(self, other):
        """
        Checks if self instersects with wall other
        """
        mp1 = ((self.r1+self.r2)/2, (self.c1+self.c2)/2)
        mp2 = ((other.r1+other.r2)/2, (other.c1+other.c2)/2)
        if mp1 == mp2:
            return True
        if (self.isHoriz() == other.isHoriz()) and ( \
            mp1 == other.loc1() or mp1 == other.loc2() or \
            mp2 == self.loc1() or mp2 == self.loc2()):
            return True
        return False

    def toMove(self):
        """
        Converts the wall to a PlayerMove object
        """
        return PlayerMove(self.owner, False, self.r1, self.c1, self.r2, self.c2)

    def __str__(self):
        return "Wall@<%d,%d - %d,%d>" % (self.r1, self.c1, self.r2, self.c2)
    def __eq__(self, other):
        return self.r1 == other.r1 and self.r2 == self.r2 and \
            self.c1 == other.c1 and self.c2 == other.c2
    def __hash__(self):
        return hash(self.r1) + hash(self.c1) + hash(self.r2) + hash(self.c2)

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
    """A sample class for your player data"""
    
    def __init__(self, logger, playerId, numWalls, playerLocations):
        """
        __init__: 
        Constructs and returns an instance of PlayerData.
            self - new instance
            logger - the engine logger
            playerId - my player ID (0-3)
            numWalls: Number of walls we have
            playerLocations - list of player coordinates
        """
        
        self.logger = logger
        self.playerId = playerId
        self.numWalls = numWalls
        self.playerLocations = playerLocations
        
        self.board = bytearray(BOARD_DIM*BOARD_DIM)
        self.walls = []
        self.placewall = False

    ############################################################################################
    # Helper functions

    def log(self, msg):
        """
        Equivalent to self.logger.write
        """
        self.logger.write(msg)

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
        Returns the location aFjacent to the specified location in the direction of the passed Direction, or
        None if it is not possible to move in that direction
        """
        if self[loc] & d != 0: return None # Blocked
        r,c = loc[0]+Directions.TO_ADJ[d][0], loc[1]+Directions.TO_ADJ[d][1]
        if r < 0 or r >= BOARD_DIM or c < 0 or c >= BOARD_DIM:
            return None # Out of bounds
        return (r,c)

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
        new.logger = self.logger
        new.playerId = self.playerId
        new.numWalls = self.numWalls
        new.playerLocations = self.playerLocations.copy()
        new.board = self.board.copy()
        new.walls = self.walls.copy()
        new.placewall = self.placewall

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
        """
        __str__: PlayerData -> string
        Returns a string representation of the PlayerData object.
            self - the PlayerData object
        """

        b = "LDRU "*BOARD_DIM + "\n"
        for r in range(BOARD_DIM):
            for c in range(BOARD_DIM):
                b += "{:04b} ".format(self[r,c])
            b += "\n"

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

    def addWall(self, wall):
        """
        addWall: Wall -> Boolean
        Adds a wall to the internal board representation.
        Returns true if successful, false if the wall is invalid or collides with other walls.
        """
        if not wall.isValid():
            return False
        for i in self.walls:
            if wall.intersects(i):
                return False

        if wall.isHoriz():
            # Horizontal wall
            for i in range(wall.c1, wall.c2):
                self[wall.r1  ,i] |= Directions.UP
                self[wall.r2-1,i] |= Directions.DOWN
        else:
            # Vertical wall
            for i in range(wall.r1, wall.r2):
                self[i,wall.c1  ] |= Directions.LEFT
                self[i,wall.c1-1] |= Directions.RIGHT
        self.walls.append(wall)
        
        if wall.owner == self.playerId + 1:
            self.numWalls -= 1
        return True

    def getMove(self):
        """
        Returns the PlayerMove object representing the move that the player should make
        """
        testpd = self.copy()

        if self.placewall and self.numWalls > 0:
            self.placewall = False
            # Generate a wall
            while True:
                w = randomWall(testpd.playerId + 1)
                self.log("Generated wall: " + str(w))
                if testpd.addWall(w):
                    break
            return w.toMove()
        else:
            self.placewall = True
            # Move along the shortest path
            mypos = self.getMyPos()
            path = self.findPathToGoal(mypos)
            if not path:
                raise RuntimeError("No path to goal!")
            elif len(path) >= 2:
                return PlayerMove(self.playerId + 1, True, mypos[0], mypos[1], path[1][0], path[1][1])
            else:
                return None


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
        closed = set()
        open_set = {start}
        open_sorted = [start]
        came_from = {start : None}
        g_score = {start : 0}
        def evalScore(loc):
            return g_score[loc] + heuristic(loc)
        
        while len(open_set) != 0:
            current = open_sorted.pop()
            open_set.remove(current)
            if atgoal(current):
                l = []
                while current != None:
                    l.append(current)
                    current = came_from[current]
                l.reverse()
                return l
            closed.add(current)
            for i in self.getAdjacent(current):
                if i in closed: continue
                i_gscore = g_score[current] + 1
                if i not in open_set or g_score[i] > i_gscore:
                    came_from[i] = current
                    g_score[i] = i_gscore
                    if i not in open_set:
                        open_set.add(i)
                        open_sorted.append(i)
                    open_sorted.sort(key=evalScore, reverse=True)
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
    
    def findPathToGoal(self, start):
        """
        findPathToGoal: (r,c) -> list
        Finds the shortest valid path to the goal
        TODO: Support for other goals than the top
        """
        def heuristic(loc):
            return abs(loc[0])
        def atgoal(loc):
            return loc[0] == 0
        return self._astar(start, heuristic, atgoal)
