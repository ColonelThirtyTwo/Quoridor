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

inf = float("inf")

def alphabeta(board, depth, plyid, a=-inf, b=inf, curplyid=None):
	"""
	Generates and runs through a decision tree using minimax and alpha-beta pruning
	http://en.wikipedia.org/wiki/Minimax and http://en.wikipedia.org/wiki/Alpha-beta_pruning
		board: Starting configuration
		depth: Pile depth to search
		plyid: Starting player's id
		a: Recursive parameter, don't use
		b: Recursive parameter, don't use
		curplyid: Recursive parameter, don't use
	Returns: A dictionary tree with move : (node, score) entries of all the branches visited
	"""
	curplyid = curplyid or plyid
	
	if depth <= 0 or board.isTerminal():
		return board, board.evaluate(plyid)
	
	# Compute next ID
	nextid = (curplyid+1) % len(board.players)
	while not board.players[nextid]:
		nextid = (nextid+1) % len(board.players)
	#print(board.players, curplyid, nextid)
	
	treenode = {}
	
	if curplyid == plyid:
		# Max
		for move in board.generateNext(curplyid):
			#print("max: examining "+str(move))
			tree, score = alphabeta(board.copy().applyMove(move), depth-1, plyid, a, b, nextid)
			treenode[move] = (tree, score)
			a = max(a, score)
			if b < a:
				break
		return treenode, a
	else:
		# Min
		for move in board.generateNext(curplyid):
			#print("min: examining "+str(move))
			tree, score = alphabeta(board.copy().applyMove(move), depth-1, plyid, a, b, nextid)
			treenode[move] = (tree, score)
			b = min(b, score)
			if a < b:
				break
		return treenode, b

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
	
	def applyMove(self, move):
		self.currentboard.applyMove(move)
	
	def getMove(self):
		tree, _ = alphabeta(self.currentboard, 1, self.me)
		move, _ = min(tree.items(), key=lambda n: n[1][1])
		return move
	
	def invalidate(self, plyid):
		self.currentboard.invalidate(plyid)
