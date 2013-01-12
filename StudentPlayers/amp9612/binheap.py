"""
Binary heap implementation

Author: Alex Parrill (amp9612@rit.edu)
"""

from math import floor

class BinaryHeapMap:
	"""
	A binary min-heap implementation with an update method.

	The heap stores an arbitrary hashable, non-None object (the 'key') as well as
	a numerical value to be used during the heap ordering (the 'value')
	"""

	def __init__(self, mapping=None):
		if mapping:
			self._heap = [k for k in mapping]
			self._values = mapping.copy()
			for i in range(floor((len(self._heap)-1)/2), -1, -1):
				self._downheap(i)
		else:
			self._heap = []
			self._values = {}

	def _get(self, i):
		return self._values[self._heap[i]]

	def _upheap(self, i):
		p = floor((i-1)/2)
		while self._get(p) > self._get(i) and i != 0:
			self._heap[p], self._heap[i] = self._heap[i], self._heap[p]
			i = p
			p = floor((i-1)/2)

	def _downheap(self, i):
		l = len(self)
		while True:
			c1 = i*2+1
			c2 = i*2+2
			smallest = i
			if c1 < l and self._get(c1) < self._get(smallest):
				smallest = c1
			if c2 < l and self._get(c2) < self._get(smallest):
				smallest = c2

			if smallest != i:
				self._heap[i], self._heap[smallest] = self._heap[smallest], self._heap[i]
			else:
				break

	def add(self, key, value):
		"""
		Adds an item to the heap.
			key: Data to store
			value: Value to store. This must be a numeric value and is used when sorting the heap
		Returns true if the item was added or false if the item was already in the heap
		"""
		if key in self:
			return False
		if key is None:
			raise ValueError("Key may not be None")

		# Add item
		self._heap.append(key)
		self._values[key] = value
		self._upheap(len(self._heap)-1)
	
	def peek(self):
		"""
		Returns but does not remove the head of the heap's key and value.

		Raises IndexError if the heap is empty
		"""
		if len(self._heap) > 0:
			return self._heap[0], self._values[self._heap[0]]
		else:
			raise IndexError("heap is empty")
	
	def pop(self):
		"""
		Removes the head of the heap and returns both the key and the value

		Raises IndexError if the heap is empty
		"""
		if len(self) == 0:
			raise IndexError("heap is empty")

		# Get values and remove them
		rkey, rval = self._heap[0], self._values[self._heap[0]]
		del self._values[rkey]
		if len(self) == 1:
			self._heap.pop()
		else:
			self._heap[0] = self._heap.pop()
			self._downheap(0)
		return rkey, rval
	
	def _find(self, key, i=0):
		if i >= len(self):
			# Out of bounds
			return None
		elif self._heap[i] == key:
			# Found it
			return i
		elif self._get(i) <= self._values[key]:
			# Search more
			return self._find(key, i*2+1) or self._find(key, i*2+2)
		return None

	def update(self, key, value):
		"""
		Updates a key's value and resorts it in the heap.
		"""
		if key not in self:
			raise KeyError(key)
		
		i = self._find(key)
		assert(i is not None)
		
		oldval = self._values[key]
		self._values[key] = value
		if value > oldval:
			self._downheap(i)
		else:
			self._upheap(i)
	
	def copy(self):
		"""
		Creates a shallow copy of the heap.
		"""
		c = BinaryHeapMap.__new__(BinaryHeapMap)
		c._heap = self._heap.copy()
		c._values = self._values.copy()
		return c

	def __len__(self):
		return len(self._heap)
	def __contains__(self, key):
		return key in self._values
	def __str__(self):
		return "BinaryHeapMap("+repr(self._values)+")"
	def __repr__(self):
		return "BinaryHeapMap("+repr(self._values)+")"
	def __bool__(self):
		return bool(self._heap)

if __name__ == "__main__":
	# Tests
	import random
	random.seed()
	
	h1 = BinaryHeapMap()
	letters = [x for x in "abcde"]
	values = [x+1 for x in range(len(letters))]
	random.shuffle(values)
	for k,v in zip(letters, values):
		h1.add(k,v)
	print(h1)
	h2 = h1.copy()
	
	while h1:
		print("Pop:", h1.pop())
		
	toupdate, updateval = random.choice(letters), random.randrange(len(letters))
	print("Updating", toupdate, "to", updateval)
	h2.update(toupdate, updateval)
	while h2:
		print("Pop:", h2.pop())
	
	print("Creating from dictionary")
	d = {}
	for k,v in zip(letters, values):
		d[k] = v
	h3 = BinaryHeapMap(d)
	while h3:
		print("Pop:", h3.pop())
