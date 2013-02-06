"""
Board class to store the board's state
Author: Alex Parrill (amp9612@rit.edu)
Author: Joseph Moreyn (jbm6331@rit.edu)
"""

from .wall import Wall
from .hashableplayermove import HashablePlayerMove
from Model.interface import BOARD_DIM
from collections import deque

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
	Representation of a quoridor board
	"""
	
	def __init__(self, players, board=None, walls=None):
		self.players = players
		self.walls = walls or []
		
		if board:
			self.board = board
		else:
			self.board = {}
			tmplist = []
			for r in range(BOARD_DIM):
				for c in range(BOARD_DIM):
					if r != 0:           tmplist.append((r-1,c))
					if r != BOARD_DIM-1: tmplist.append((r+1,c))
					if c != 0:           tmplist.append((r,c-1))
					if c != BOARD_DIM-1: tmplist.append((r,c+1))
					self.board[r,c] = frozenset(tmplist)
					tmplist.clear()
	
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
		new.board = self.board.copy() # The individual elements in the adjacency list are immutable, so they dont need to be deep copied
		new.walls = self.walls.copy() # Wall are immutable, so they don't need to be deep copied
		new.players = [p and p.copy() or p for p in self.players]
		
		return new
	
	#################################################################################################################
	
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
		self.players[plyid].location = loc
	
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
			ply = self.players[wall.owner]
			if ply:
				ply.walls -= 1
	
	def invalidate(self, plyid):
		self.players[plyid] = None
	
	#################################################################################################################
	
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
		Returns a generator that yields every possible (Hashable)PlayerMove from this configuration by
		player plyid
		"""
		ply = self.players[plyid]
		
		# Movement
		canmove = False
		for loc in self.getAdjacent(ply.location):
			canmove = True
			yield HashablePlayerMove(ply.id+1, True, ply.location[0], ply.location[1], loc[0], loc[1])
		
		if ply.walls != 0:
			# Vertical walls
			for c in range(1, BOARD_DIM):
				for r in range(0, BOARD_DIM-1):
					w = Wall(ply.id+1, r, c, r+2, c)
					if self.checkWall(w):
						canmove = True
						yield w.toMove()
			# Horizontal walls
			for r in range(1, BOARD_DIM):
				for c in range(0, BOARD_DIM-1):
					w = Wall(ply.id+1, r, c, r, c+2)
					if self.checkWall(w):
						canmove = True
						yield w.toMove()

		if not canmove:
			yield HashablePlayerMove(ply.id+1, True, ply.location[0], ply.location[1], ply.location[0], ply.location[1])
	
	#################################################################################################################
	
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
		Finds the shortest valid path from start to dest, inclusive.
		Returns:
			a list of (r,c) tuples representing the path.
		"""
		#def heuristic(loc):
		#	return abs(dest[0]-loc[0]) + abs(dest[1]-loc[1])
		def atgoal(loc):
			return loc == dest
		return self._bfs(start, atgoal)
	
	def findPathToGoal(self, start, goalnum):
		"""
		Finds the shortest valid path to the goal
		"""
		heuristic, atgoal = _goal_settings[goalnum]
		return self._bfs(start, atgoal)
