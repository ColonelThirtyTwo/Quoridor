"""
Quoridor student player starter file
 
Author: Adam Oest
Date: July, 2012
"""

from Model.interface import PlayerMove, BOARD_DIM
from .playerData import PlayerData, Wall

def init(logger, playerId, numWalls, playerHomes):
    """
        Part 1 - 4
    
        The engine calls this function once at the beginning of the game.
        The student player module uses this function to initialize its data
        structures to the initial game state.

        Parameters
            logger: a reference to the logger object. The player model uses
                logger.write(msg) and logger.error(msg) to log diagnostic
                information.
                
            playerId: this player's number, from 1 to 4
        
            numWalls: the number of walls each player is given initially
            
            playerHomes: An ordered tuple of player locations
                         A location is a 2-element tuple of (row,column).
                         If any player has already been eliminated from
                         the game (rare), there will be a bool False in
                         that player's spot in the tuple instead of a
                         location.
                    
        returns:
            a PlayerData object containing all of this player module's data
    """
    
    playerData = PlayerData(playerId-1, numWalls, playerHomes)
    return playerData

def last_move(playerData, move):
    """
        Parts 1 - 4
    
        The engine calls this function after any player module, including this one,
        makes a valid move in the game.
        
        The engine also calls this function repeatedly at the start of the game if
        there have been some moves specified in the configuration file's PRE_MOVE
        variable.

        The student player module updates its data structure with the information
        about the move.

        Parameters
            playerData: this player's data, originally built by this
                        module in init()
        
            move: the instance of PlayerMove that describes the move just made
        
        returns:
            this player module's updated (playerData) data structure
    """
    playerData.applyMove(move)
    return playerData

def move(playerData):
    """
        Part 3 - 4
    
        The engine calls this function at each moment when it is this
        player's turn to make a move. This function decides what kind of
        move, wall placement or piece move, to make.
        
        Parameters
            playerData: this player's data, originally built by this
                        module in init()
        
        returns:
            the move chosen, in the form of an instance of PlayerMove
    """
    return playerData.getMove_toGoal()

def player_invalidated(playerData, playerId):
    """
        Part 3 - 4
    
        The engine calls this function when another player has made
        an invalid move or has raised an exception ("crashed").
        
        Parameters
            playerData: this player's data, originally built by this
                        module in init()
            playerId: the ID of the player being invalidated
        
        returns:
            this player's updated playerData
    """
    playerData.invalidatePlayer(playerId-1)
    return playerData
