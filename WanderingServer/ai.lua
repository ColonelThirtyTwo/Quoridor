
local AI = {}
AI.__index = AI

local Board = require "board"
local Player = require "player"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

function AI:new(myid, numwalls, playerlocations)
	local ai = setmetatable({
		me = myid,
	},self)
	
	local players = {}
	for i=1,#playerlocations do
		if playerlocations[i] == false then
			players[i] = Player(i,0,0,numwalls,false)
		else
			local r,c = unCoord(playerlocations[i])
			players[i] = Player:new(i,r,c,numwalls,true)
		end
	end
	
	ai.currentboard = Board:new(players)
	return ai
end

function AI:notifyMove(plyid, r,c)
	self.currentboard:updatePlayerLocation(plyid, r, c)
end

function AI:notifyWall(wall)
	assert(self.currentboard:checkWall(wall))
	self.currentboard:addWall(wall)
end

function AI:notifyInvalidate(plyid)
	self.currentboard:invalidate(plyid)
end

function AI:getBoard()
	return self.currentboard
end

-- ------------------------------------------------------------------------------------

function AI:getNeighbors(r,c)
	local t = {}
	for i=1,4 do
		local d = self.currentboard:getNeighbor(Coord(r,c),i)
		if not d then break end
		table.insert(t, {unCoord(d)})
	end
	return t
end

function AI:getPath(r1,c1,r2,c2)
	return self.currentboard:findPathToLoc(Coord(r1,c1), Coord(r2,c2))
end

return AI
