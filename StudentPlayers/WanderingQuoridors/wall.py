"""
Wall class
Author: Alex Parrill (amp9612@rit.edu)
Author: Joseph Moreyn (jbm6331@rit.edu)
"""

from Model.interface import BOARD_DIM
from .hashableplayermove import HashablePlayerMove as PlayerMove

class Wall:
    """
    A reprensentation of a wall.
    """
    def __init__(self, ownerid, r1, c1, r2, c2):
        self.owner = ownerid
        self._r1 = r1
        self._c1 = c1
        self._r2 = r2
        self._c2 = c2
        
    # Make them 'read only'
    @property
    def r1(self): return self._r1
    @property
    def c1(self): return self._c1
    @property
    def r2(self): return self._r2
    @property
    def c2(self): return self._c2

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
        return self.r1 == self.r2
    
    def isVert(self):
        """
        Returns true if wall is vertical
        """
        return self.c1 == self.c2
    
    def isValid(self):
        """
        Checks if the wall is valid, that is:
        1. Wall is axis aligned
        2. Wall coordinates are in the correct order
        3. Wall has a length of 2
        4. Wall is inside the board
        """
        
        if self.r1 != self.r2 and self.c1 != self.c2:
            # Not axis aligned
            return False
        if self.r2 < self.r1 or self.c2 < self.c1:
            # Coordinates in wrong order
            return False
        if self.r2-self.r1 + self.c2-self.c1 != 2:
            # Length != 2
            return False
            
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
        
        if self.isHoriz() == other.isHoriz():
            if mp1 == other.loc1():
                return True
            elif mp1 == other.loc2():
                return True
        return False

    def toMove(self):
        """
        Converts the wall to a PlayerMove object
        """
        return PlayerMove(self.owner+1, False, self.r1, self.c1, self.r2, self.c2)

    def __str__(self):
        return "Wall@<%d,%d - %d,%d>" % (self.r1, self.c1, self.r2, self.c2)
    def __eq__(self, other):
        return self.r1 == other.r1 and self.r2 == self.r2 and \
            self.c1 == other.c1 and self.c2 == other.c2
    def __hash__(self):
        return hash(self.r1) + hash(self.c1) + hash(self.r2) + hash(self.c2)
