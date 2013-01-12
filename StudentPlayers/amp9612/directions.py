"""
Bitwise enumerations for representing directions
Author: Alex Parrill (amp9612@rit.edu)
"""

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
    PERPENDICULAR = {LEFT : (UP, DOWN), RIGHT : (UP, DOWN), UP : (LEFT, RIGHT), DOWN : (LEFT, RIGHT)}
