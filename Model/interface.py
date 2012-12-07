"""
This is the interface the player uses to specify its moves and communicate
with the engine. NOTE: Nothing in this file should be modified by students.

Author: Adam Oest (amo9149@rit.edu)
"""

BOARD_DIM = 9

class PlayerMove():
	"""
		This class communicates information about a new move being made.
		The engine uses these objects internally to verify the player's
		move and update the board display.
		
		Note that this class is used for both wall placements, which need
		two pairs of coordinates for the wall endpoints, and piece moves,
		which use the first coordinate pair for a verification of the
		current position and the second coordinate pair for the new position.
		
		The Coordinate System
		
		A Quoridor board is a 9-by-9 grid of cells.
		"Cells" are the spots where player pieces can be placed.
		Our numbering conventions for cell positions are as follows.
		The top row is row 0; the bottom row is row 8.
		The left column is column 0; the rightmost column is column 8.
		Examples
			The top right corner cell is row 0, column 8.
			The starting position of the player at the bottom of the board
			  is row 8, column 4.

		For wall placement, you must identify locations _between_
		the cells. These locations are numbered 0 through 9.
		The board position for identifying the end point of a wall
		is therefore the same as that of the cell below it to its right,
		if a cell exists there.
		Looking at it the opposite way, the coordinates of a cell are
		the same as the coordinates of its upper left-hand corner.
		
		Player identification
		
		Player IDs start with 1 (not 0).
		For example, in a four-player game the player IDs are 1,2,3,4.
		In part 1, all PlayerMove instances should have playerId = 1.
    """
	__slots__ = ('playerId','move','start','end','r1','c1','r2','c2')
	
	def __init__(self, playerId, move, r1, c1, r2, c2):
		"""
		Initialize the object.
			playerId: your player id
			move: True for move, False for wall
			IF move IS True:
				r1: piece's current row coordinate
				c1: piece's current column coordinate
				r2: piece's new row coordinate
				c2: piece's new column coordinate
			IF move IS False:
				r1: wall starting (top) row coordinate
				c1: wall starting (left) column coordinate
				r2: wall ending (bottom) row coordinate
				c2: wall ending (right) column coordinate
		Precondition: If the move is a wall placement, the first coordinate pair
		              must be the top or left end of the wall.
		"""
		
		self.playerId = playerId
		self.move = move
		
		self.start = (r1, c1)
		self.end = (r2, c2)
		self.r1, self.c1, self.r2, self.c2 = r1, c1, r2, c2
		
	def getCopy(self):
		"""Copy constructor"""
		return PlayerMove(self.playerId,self.move, self.r1, self.c1, self.r2, self.c2);

	def __str__(self):
		"""Return a string representation of this object"""
	
		return "Player %s %s: [%s,%s] -> [%s,%s]" % \
			(self.playerId, 'Move' if self.move else 'Wall', self.start[0],
			self.start[1], self.end[0], self.end[1])
	
	def __repr__(self):
		"""Return a string representation of this object"""
		return self.__str__();
	

# FOR STUDENT ENGINES ONLY

class StudentEngineModel():
	"""
	    Model class wrapper for student engine
	"""
	
	# All the slots are callable functions
	__slots__ = ('makeMove','getPlayerData','setPlayerData',
		'getPlayerModule', 'playerHomes')
	
	
	def __init__(self, makeMove, getPlayerData, setPlayerData, getPlayerModule, \
			playerHomes):
		"""
		    Save method references
		"""
		self.makeMove = makeMove
		self.getPlayerData = getPlayerData
		self.setPlayerData = setPlayerData
		self.getPlayerModule = getPlayerModule
		self.playerHomes = playerHomes
		
		""" 
		METHOD SIGNATURES AND OVERVIEW
		
		    makeMove(playerMove)
		        
		        tells the web engine to execute and display the passed move
		        the move must be valid
		    
		    getPlayerData(playerId)
		
		        gets the player data for the given player (id's start at 1)
		    
		        returns: player's data object
		    
		    setPlayerData(playerId, playerData)
		
		        saves the passed data as the player's new data
		        retrieved using getPlayerData
		        
		    getPlayerModule(playerId)
		    
		        retrieves the requested player module object
		        so you can call its functions
		    
		        returns: player module
		"""