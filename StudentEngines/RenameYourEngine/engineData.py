"""
Quoridor II: Student Computer Engine

A sample class you may use to hold your state data
Author: Adam Oest (amo9149@rit.edu)

Author: YOUR NAME HERE (your email address)
Author: YOUR NAME HERE (your email address)
Author: YOUR NAME HERE (your email address)
"""

class EngineData(object):
    """A sample class for your engine data"""
    
    # Add other slots as needed
    __slots__ = ('logger', 'config', 'model')
    
    def __init__(self, logger, config, model):
        """
            Constructs and returns an instance of EngineData
            
            You decide what parameters and slots to use.  This is just a 
            minimal example.
        """
        
        self.logger = logger
        self.config = config
        self.model = model
        
        # initialize any other slots you require here
        
    def __str__(self):
        """
        __str__: EngineData -> string
        Returns a string representation of the EngineData object.
            self - the EngineData object
        """
        result = "EngineData= " \
                    + "logger: " + str(self.logger) \
                    + ", config: " + str(self.config) \
                    + ", model: " + str(self.model)
                
        # add any more string concatenation for your other slots here
                
        return result