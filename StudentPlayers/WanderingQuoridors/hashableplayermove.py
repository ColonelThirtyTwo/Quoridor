"""
Subclass of PlayerMove that is hashable
Author: Alex Parrill (amp9612@rit.edu)
Author: Joseph Moreyn (jbm6331@rit.edu)
"""


from Model.interface import PlayerMove

class HashablePlayerMove(PlayerMove):
	"""
	Subclass of PlayerMove that is hashable
	"""
	__slots__ = tuple()
	
	def __eq__(self, other):
		return self.playerId == other.playerId and \
			self.move == other.move and \
			self.r1 == other.r1 and self.r2 == other.r2 and \
			self.c1 == other.c1 and self.c2 == other.c2
	def __hash__(self):
		return hash(self.playerId) ^ hash(self.move) ^ hash(self.r1) ^ hash(self.c1) ^ hash(self.r2) ^ hash(self.c2)
