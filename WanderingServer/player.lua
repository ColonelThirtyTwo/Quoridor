
local ffi = require "ffi"

local Player = {}
Player.__index = Player

function Player:new(id, r, c, walls, valid)
	return setmetatable({
		id = id,
		r = r, c = c,
		walls = walls,
		valid = valid,
	}, self)
end

function Player:copy()
	return setmetatable({
		id = self.id,
		pos = self.pos,
		walls = self.walls,
		valid = self.valid,
	}, getmetatable(self))
end

return Player
