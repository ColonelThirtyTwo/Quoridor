"""
Quoridor II: Student Computer Player

A sample class you may use to hold your state data
Author: Adam Oest (amo9149@rit.edu)
Author: Alex Parrill (amp9612@rit.edu)
"""

from Model.interface import BOARD_DIM

# Enumerations for representing directions
DIR_UP = 0x1
DIR_RIGHT = 0x2
DIR_DOWN = 0x4
DIR_LEFT = 0x8
DIR_LIST = (DIR_DOWN, DIR_RIGHT, DIR_UP, DIR_LEFT)
DIR_2_ADJ = {DIR_LEFT : (0,-1), DIR_RIGHT : (0,1), DIR_UP : (-1,0), DIR_DOWN : (1,0)}

class PlayerData(object):
    """A sample class for your player data"""
    
    def __init__(self, logger, playerId, playerLocations):
        """
        __init__: 
        Constructs and returns an instance of PlayerData.
            self - new instance
            logger - the engine logger
            playerId - my player ID (0-3)
            playerLocations - list of player coordinates
        """
        
        self.logger = logger
        self.playerId = playerId
        self.playerLocations = playerLocations
        self.numPlayers = len(playerLocations)
        
        self.board = bytearray(BOARD_DIM*BOARD_DIM)
        self.debug = False

    def getAdjacent(self, loc):
        """
        getAdjacent: (r,c) -> (r,c)
        Returns a list of all adjacent spaces that can be accessed from this space.
            loc - locationm tuple
        """
        adj = []
        for d in DIR_LIST:
            newloc = self.getMoveTo(loc, d)
            if newloc: adj.append(newloc)
        return adj

    def getMoveTo(self, loc, d):
        """
        getMoveTo: (r,c), DIR_ENUM -> (r,c)
        Returns the location adjacent to the specified location in the direction of the passed DIR_ENUM, or
        None if it is not possible to move in that direction
        """
        if self[loc] & d != 0: return None # Blocked
        r,c = loc[0]+DIR_2_ADJ[d][0], loc[1]+DIR_2_ADJ[d][1]
        if r < 0 or r >= BOARD_DIM or c < 0 or c >= BOARD_DIM:
            return None # Out of bounds
        return (r,c)

    def addWall(self, start, end):
        """
        addWall: int, int, int, int
        Adds a wall to the internal board representation.
        """
        if start[0] == end[0]:
            # Horizontal wall
            for i in range(start[1], end[1]):
                self[start[0]  ,i] |= DIR_UP
                self[start[0]-1,i] |= DIR_DOWN
        elif start[1] == end[1]:
            # Vertical wall
            for i in range(start[0], end[0]):
                self[i,start[1]  ] |= DIR_LEFT
                self[i,start[1]-1] |= DIR_RIGHT
        else:
            raise ValueError("Invalid wall: %d,%d to %d,%d" % (start[0], start[1], end[0], end[1]))

        self.log("Added wall from %d,%d to %d,%d. New representation:\n%s" % (start[0],start[1],end[0],end[1],str(self)))

    def log(self, msg):
        """
        log:
        Equivalent to self.logger.write
        """
        self.logger.write(msg)

    def findPath(self, start, dest):
        """
        findPath: (r,c), (r,c) -> list
        Finds the shortest valid path from start to dest, inclusive.
        Returns:
            a list of (r,c) tuples representing the path.
        """
        closed = set()
        open = {start}
        came_from = {start : None}
        g_score = {start : 0}
        def estScore(loc):
            return g_score[loc] + abs(dest[0]-loc[0]) + abs(dest[1]-loc[1])

        while len(open) != 0:
            current = min(open, key=estScore) # TODO: optimize this into O(1)
            open.remove(current)
            if current == dest:
                # At goal, reconstruct path
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
                if i not in open or g_score[i] > i_gscore:
                    came_from[i] = current
                    g_score[i] = i_gscore
                    open.add(i)
        # Explored all reachable nodes, path doesn't exist.
        return []


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
                b += "{:04b} ".format(self[r,c]) #hex(self[(r,c)]) + " "
            b += "\n"

        result = "PlayerData= " \
                    + "playerId: " + str(self.playerId) \
                    + ", playerLocations: " + str(self.playerLocations) \
                    + ", numPlayers:" + str(self.numPlayers) + ", board:\n" \
                    + b
                
        return result
