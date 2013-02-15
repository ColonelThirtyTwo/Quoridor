
import socket
#import threading
from .hashableplayermove import HashablePlayerMove
import atexit

PORT = 51894

class RemoteAI:
	class error(Exception):
		pass
	
	def __init__(self, host):
		self.host = host
		self.socket = None
	
	def _send(self, s):
		b = bytes(s,"ascii")
		totalsent = 0
		while totalsent < len(b):
			sent = self.socket.send(b[totalsent:])
			if sent == 0:
				raise RemoteAI.error("Disconnected from server")
			totalsent = totalsent + sent
	
	def _recv(self):
		buf = bytearray()
		while True:
			c = self.socket.recv(1)
			if c == b'':
				raise RemoteAI.error("Disconnected from server")
			if c == b'\n':
				s = str(buf, "ascii")
				return s
			if c != b'\r':
				buf.append(c[0])
	
	def _recvAck(self):
		r = self._recv()
		if r != "ack":
			raise RemoteAI.error("Received a bad ACK: "+r)
	
	def connect(self, me, walls, locations):
		try:
			self.socket = socket.create_connection((self.host,PORT), timeout=9.5)
			#self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
			atexit.register(self.close)
			self.me = me
			
			self._send("{} {} ".format(me, walls))
			for i in locations:
				if i:
					self._send("{},{} ".format(i[0], i[1]))
				else:
					self._send("inv ")
			self._send("\n")
			self._recvAck()
			return True
		except OSError:
			return False
	
	def sendMove(self, move):
		if move.move:
			self._send("m {} {},{}\n".format(move.playerId, move.r2, move.c2))
		else:
			self._send("w {} {},{} {},{}\n".format(move.playerId, move.r1, move.c1, move.r2, move.c2))
		self._recvAck()
	
	def sendInvalidate(self, plyid):
		self._send("i {}\n".format(plyid))
		self._recvAck()
	
	def getMove(self):
		self._send("g\n")
		
		typ, loc1, loc2 = self._recv().split()
		r1,c1 = loc1.split(",")
		r2,c2 = loc2.split(",")
		if typ == "m":
			return HashablePlayerMove(self.me, True, int(r1), int(c1), int(r2), int(c2))
		elif typ == "w":
			return HashablePlayerMove(self.me, False, int(r1), int(c1), int(r2), int(c2))
		else:
			raise RemoteAI.error("Invalid data returned from getMove: "+str(strresult))
	
	def getAdjacent(self, r,c):
		self._send("adj {},{}\n".format(r,c))
		
		strresult = self._recv().split()
		result = []
		for i in strresult:
			r,c = i.split(",")
			result.append((int(r), int(c)))
		return result
	
	def getPath(self, r1,c1, r2,c2):
		self._send("path {},{} {},{}\n".format(r1,c1, r2,c2))
		
		strresult = self._recv().split()
		result = []
		for i in strresult:
			r,c = i.split(",")
			result.append((int(r), int(c)))
		return result
	
	def close(self):
		if self.socket:
			self.socket.shutdown(socket.SHUT_RDWR)
			self.socket.close()
			self.socket = None
