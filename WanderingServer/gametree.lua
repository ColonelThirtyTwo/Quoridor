
local GameTree = {}
GameTree.__index = GameTree

local Move = require "move"
local Wall = require "wall"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

local tinsert = table.insert

function GameTree:new(board, move)
	return setmetatable({
		board = board,
		move = move,
		score = -math.huge,
		generated = false,
		sorted = false,
	}, self)
end

function GameTree:generate(plyid, depth)
	if self.generated then return end
	
	local p = self.board.players[plyid]
	local t = self.board:getAdjHop(Coord(p.r, p.c))
	for i=1,#t do
		local move = Move(plyid, p.r, p.c, unCoord(t[i]))
		tinsert(self, GameTree:new(self.board:copy():applyMove(move), move))
	end
	
	if p.walls > 0 then
		for c=1,self.board.SIZE-1 do
			for r=0,self.board.SIZE-2 do
				local w = Wall(plyid, r, c, r+2, c)
				if self.board:checkWall(w) then
					tinsert(self, GameTree:new(self.board:copy():applyMove(w), w))
				end
			end
		end
		for r=1,self.board.SIZE-1 do
			for c=0,self.board.SIZE-2 do
				local w = Wall(plyid, r, c, r, c+2)
				if self.board:checkWall(w) then
					tinsert(self, GameTree:new(self.board:copy():applyMove(w), w))
				end
			end
		end
	end
	
	if #self == 0 then
		local move = Move(plyid, p.r, p.c, p.r, p.c)
		tinsert(self, GameTree:new(self.board:copy():applyMove(move), move))
	end
	
	self.generated = true
end

function GameTree:setScore(s)
	if self.sorted then return end
	self.score = s
end

local compare = function(a,b) return a.score > b.score end -- Greater than for descending sorted
function GameTree:sort()
	if self.sorted then return end
	
	--table.sort(self, compare)
	Utils.arraySort(self,nil,nil,compare)
	self.sorted = true
end

return GameTree
