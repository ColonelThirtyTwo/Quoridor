"""
Representation of a quoridor board
Author: Alex Parrill (amp9612@rit.edu)
Author: Joseph Moreyn (jbm6331@rit.edu)
"""

from Model.interface import BOARD_DIM, PlayerMove
from .board import Board, Player
from .wall import Wall
from collections import deque
import random

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
		
		plys = [None]*len(playerLocations)
		for i, loc in enumerate(playerLocations):
			if loc:
				plys[i] = Player(i, loc, numWalls)
		self.currentboard = Board(plys)
		self.me = playerId
		self.placewall = False
	
	def applyMove(self, move):
		self.currentboard.applyMove(move)
		if move.playerId-1 == self.me:
			self.placewall = move.move
	
	def getMove(self):
		if self.placewall and self.currentboard.players[self.me].walls > 0:
			while True:
				w = randomWall(self.me)
				if self.currentboard.checkWall(w):
					return w.toMove()
		else:
			mypos = self.currentboard.players[self.me].location
			path = self.currentboard.findPathToGoal(mypos, self.me)
			assert path, "No path to goal"
			assert len(path) > 1, "Shouldn't I have won?"
			return PlayerMove(self.me+1, True, mypos[0], mypos[1], path[1][0], path[1][1])
	
	def invalidate(self, plyid):
		self.currentboard.invalidate(plyid)
