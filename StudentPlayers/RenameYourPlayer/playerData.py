"""
Quoridor II: Student Computer Player

A sample class you may use to hold your state data
Author: Adam Oest (amo9149@rit.edu)
Author: YOUR NAME HERE (your email address)
Author: YOUR NAME HERE (your email address)
Author: YOUR NAME HERE (your email address)
"""

class PlayerData(object):
    """A sample class for your player data"""
    
    # Add other slots as needed
    __slots__ = ('logger', 'playerId', 'playerLocations', 'numPlayers')
    
    def __init__(self, logger, playerId, playerLocations):
        """
        __init__: 
        Constructs and returns an instance of PlayerData.
            self - new instance
            logger - the engine logger
            playerId - my player ID (1-4)
            playerLocations - list of player start coordinates
        """
        
        self.logger = logger
        self.playerId = playerId
        self.playerLocations = playerLocations
        self.numPlayers = len(playerLocations)
        
        # initialize any other slots you require here
        
    def __str__(self):
        """
        __str__: PlayerData -> string
        Returns a string representation of the PlayerData object.
            self - the PlayerData object
        """
        result = "PlayerData= " \
                    + "playerId: " + str(self.playerId) \
                    + ", playerLocations: " + str(self.playerLocations) \
                    + ", numPlayers:" + str(self.numPlayers)
                
        # add any more string concatenation for your other slots here
                
        return result