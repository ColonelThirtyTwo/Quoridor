
class Vector(tuple):
	__slots__ = ()
	
	def __add__(self, other):
		return Vector(self[0]+other[0], self[1]+other[1])
	def __sub__(self, other):
		return Vector(self[0]-other[0], self[1]-other[1])
	def __mul__(self, other):
		return Vector(self[0]*other, self[1]*other)
	def __div__(self, other):
		return Vector(self[0]/other, self[1]/other)
