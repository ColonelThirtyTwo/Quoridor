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
from profilehooks import profile

inf = float("inf")

def alphabeta(board, depth, plyid, a=-inf, b=inf, curplyid=None):
	"""
	Generates and runs through a decision tree using minimax and alpha-beta pruning
	http://en.wikipedia.org/wiki/Minimax and http://en.wikipedia.org/wiki/Alpha-beta_pruning
		board: Starting configuration
		depth: Number of piles to search
		plyid: Maxing player's id
		a: Recursive parameter, don't use
		b: Recursive parameter, don't use
		curplyid: Recursive parameter, don't use
	Returns:
		The best PlayerMove object found
		The score of that move
	"""
	curplyid = curplyid or plyid
	
	if depth <= 0:
		return board, board.evaluate(plyid)
	
	p = board.isTerminal()
	if p:
		if p.id == plyid:
			return None, inf
		else:
			return None, -inf
	
	# Compute next ID
	nextid = (curplyid+1) % len(board.players)
	while not board.players[nextid]:
		nextid = (nextid+1) % len(board.players)
	
	if curplyid == plyid:
		# Max
		bestmove = None
		for move in board.generateNext(curplyid):
			#print("max: examining "+str(move))
			_, score = alphabeta(board.copy().applyMove(move), depth-1, plyid, a, b, nextid)
			if score > a:
				bestmove = move
				a = score
			if b <= a:
				break
		return bestmove, a
	else:
		# Min
		bestmove = None
		for move in board.generateNext(curplyid):
			#print("min: examining "+str(move))
			_, score = alphabeta(board.copy().applyMove(move), depth-1, plyid, a, b, nextid)
			if score < b:
				bestmove = move
				b = score
			if b <= a:
				break
		return bestmove, b

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
	Stores the AI state.
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
	
	def applyMove(self, move):
		"""
		Notifies the AI of a move
		"""
		self.currentboard.applyMove(move)
	
	#@profile(immediate=True, sort="time", filename="profile.out")
	def getMove(self):
		"""
		Computes and returns the move the AI thinks it should make
		"""
		bestmove, _ = alphabeta(self.currentboard, 2, self.me)
		return bestmove
	
	def invalidate(self, plyid):
		"""
		Notifies the AI of an invalidated player.
		"""
		self.currentboard.invalidate(plyid)
