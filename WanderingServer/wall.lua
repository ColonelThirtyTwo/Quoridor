
local ffi = require "ffi"
local Board = require "board"

local Wall = {}
Wall.__index = Wall
local Wall_typ = ffi.typeof[[struct {
	int owner;
	int r1, c1, r2, c2;
}]]

function Wall:__new(owner, r1, c1, r2, c2)
	return ffi.new(self, owner, r1,c1, r2,c2)
end

function Wall:horizontal()
	return self.r1 == self.r2
end

function Wall:valid()
	if self.r1 ~= self.r2 and self.c1 ~= self.c2 then
		-- Not axis aligned
		return false
	end
	if self.r2 < self.r1 or self.c2 < self.c1 then
		-- Coordinates in wrong order
		return false
	end
	if self.r2-self.r1 + self.c2-self.c1 ~= 2 then
		-- Length ~= 2
		return false
	end
		
	if self.r1 < 0 or self.r1 > Board.SIZE or self.c1 < 0 or self.c1 > Board.SIZE or
		self.r2 < 0 or self.r2 > Board.SIZE or self.c2 < 0 or self.c2 > Board.SIZE then
		-- There is a coordinate outside the board
		return false
	end

	bordercoords = 0
	-- Check to see if we have no more than one coordinate on a border
	if self.r1 == 0 or self.r1 == Board.SIZE then
		bordercoords = bordercoords + 1
	end
	if self.c1 == 0 or self.c1 == Board.SIZE then
		bordercoords = bordercoords + 1
	end
	if self.r2 == 0 or self.r2 == Board.SIZE then
		bordercoords = bordercoords + 1
	end
	if self.c2 == 0 or self.c2 == Board.SIZE then
		bordercoords = bordercoords + 1
	end
	return bordercoords <= 1
end

function Wall:intersects(other)
	assert(ffi.istype(Wall_typ, other))
	mp1r, mp1c = (self.r1+self.r2)/2, (self.c1+self.c2)/2
	mp2r, mp2c = (other.r1+other.r2)/2, (other.c1+other.c2)/2
	if mp1r == mp2r and mp1c == mp2c then
		return true
	end
	
	if self:horizontal() == other:horizontal() then
		if mp1r == other.r1 and mp1c == other.c1 then
			return true
		elseif mp1r == other.r2 and mp1c == other.c2 then
			return true
		end
	end
	return false
end

function Wall:copy()
	return ffi.new(Wall_typ, self)
end

function Wall:__tostring()
	return string.format("Wall@(%d,%d)-(%d,%d)", self.r1,self.c1, self.r2,self.c2)
end

return ffi.metatype(Wall_typ, Wall)
