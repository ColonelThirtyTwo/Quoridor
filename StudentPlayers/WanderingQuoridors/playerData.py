"""
Representation of a quoridor board
Author: Alex Parrill (amp9612@rit.edu)
Author: Joseph Moreyn (jbm6331@rit.edu)
"""

from Model.interface import BOARD_DIM, PlayerMove
from .board import Board, Player
from .wall import Wall
from .remoteai import RemoteAI
import random

CHEAP_MIN_ON_4PLAYER = True

inf = float("inf")
def alphabeta(board, depth, plyid, a=-inf, b=inf, curplyid=None, cheapmin=False):
	"""
	Generates and runs through a decision tree using minimax and alpha-beta pruning
	http://en.wikipedia.org/wiki/Minimax and http://en.wikipedia.org/wiki/Alpha-beta_pruning
		board: Starting configuration
		depth: Number of piles to search
		plyid: Maxing player's id
		a: Recursive parameter, don't use
		b: Recursive parameter, don't use
		curplyid: Recursive parameter, don't use
		cheapmin: Only compute pawn movements for min player piles. Tremendously speeds up scan, but doesn't consider enemy wall placements.
	Returns:
		The best PlayerMove object found
		The score of that move
	"""
	if curplyid is None:
		curplyid = plyid
	
	p = board.isTerminal()
	if p:
		if p.id == plyid:
			return None, inf
		else:
			return None, -inf
	
	if depth <= 0:
		return board, board.evaluate(plyid)
	
	nextid = (curplyid+1) % len(board.players)
	while not board.players[nextid]:
		nextid = (nextid+1) % len(board.players)
	
	if curplyid == plyid:
		# Max
		bestmove = None
		for move in board.generateNext(curplyid):
			#print("max: examining "+str(move))
			_, score = alphabeta(board.copy().applyMove(move), depth-1, plyid, a, b, nextid, cheapmin)
			if score > a:
				bestmove = move
				a = score
			if b <= a:
				break
		return bestmove, a
	else:
		# Min
		bestmove = None
		if cheapmin:
			itr = board.generateNextMove(curplyid)
		else:
			itr = board.generateNext(curplyid)
		for move in itr:
			#print("min: examining "+str(move))
			_, score = alphabeta(board.copy().applyMove(move), depth-1, plyid, a, b, nextid, cheapmin)
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

def getMoveToGoal(board, plyid):
	"""
	Returns a PlayerMove object to move plyid along the shortest path to its goal.
	"""
	loc = board.players[plyid].location
	bestmove, bestlen = None, inf
	for i in board.getAdjacentHop(loc):
		path = board.findPathToGoal(i, plyid)
		if path and len(path) < bestlen:
			bestmove = i
			bestlen = len(path)
	if bestmove:
		return PlayerMove(plyid+1, True, loc[0], loc[1], bestmove[0], bestmove[1])
	
	if board.players[plyid].walls > 0:
		# Gotta place a wall
		while True:
			w = randomWall(plyid)
			if board.checkWall(w):
				return w.toMove()
	else:
		# Can pass
		PlayerMove(plyid+1, True, loc[0], loc[1], loc[0], loc[1])

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
		
		self.remoteai = RemoteAI("col32-desktop.student.rit.edu")
		self.remoteai.connect(playerId+1, numWalls, playerLocations)
	
	def applyMove(self, move):
		"""
		Notifies the AI of a move
		"""
		self.currentboard.applyMove(move)
		if self.remoteai:
			self.remoteai.sendMove(move)
	
	#from profilehooks import profile
	#@profile(immediate=True, sort="time", filename="profile.out")
	def getMove(self):
		"""
		Computes and returns the move the AI thinks it should make
		"""
		if self.currentboard.activeplayers == 1:
			return getMoveToGoal(self.currentboard, self.me)
		elif self.remoteai:
			try:
				return self.remoteai.getMove()
			except Exception as err:
				self.remoteai = None
				print(err)
				print("WanderingQuoridors: Falling back to backup move generator...")
				return getMoveToGoal(self.currentboard, self.me)
		else:
			if CHEAP_MIN_ON_4PLAYER and self.currentboard.activeplayers > 2:
				depth = 4
				cheapmin = True
			else:
				depth = 2
				cheapmin = False
			bestmove, _ = alphabeta(self.currentboard, depth, self.me, cheapmin=cheapmin)
			if bestmove:
				return bestmove
			else:
				print("WanderingQuoridors: Failure is probably imminent. Panic now.")
				return getMoveToGoal(self.currentboard, self.me)
	
	def invalidate(self, plyid):
		"""
		Notifies the AI of an invalidated player.
		"""
		self.currentboard.invalidate(plyid)
		if self.remoteai:
			self.remoteai.sendInvalidate(plyid+1)
