
-- Represents a pawn move

local ffi = require "ffi"

local Move = {}
Move.__index = Move
local Move_typ = ffi.typeof[[struct {
	int plyid;
	int prevr, prevc;
	int r, c;
}]]

function Move:__tostring()
	return string.format("Move@(Ply:%d)(%d,%d -> %d,%d)", self.plyid, self.prevr, self.prevc, self.r, self.c)
end

return ffi.metatype(Move_typ, Move)
