
-- Represents a player

local ffi = require "ffi"

local Player = {}
Player.__index = Player
local Player_typ = ffi.typeof[[struct{
	int id;
	int r,c;
	int walls;
	bool valid;
}]]

function Player:copy()
	return Player_typ(self)
end

function Player:__tostring()
	if self.valid then
		return string.format("Player%d@(%d,%d)(walls:%d)", self.id, self.r, self.c, self.walls)
	else
		return string.format("Player%d(invalid)", self.id)
	end
end

return ffi.metatype(Player_typ, Player)
