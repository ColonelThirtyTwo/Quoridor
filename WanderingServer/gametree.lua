
-- A tree class where each edge represents a move a player can make.
-- The tree dynamically expands as it is used.

local GameTree = {}
GameTree.__index = GameTree

local Board = require "board"
local Move = require "move"
local Wall = require "wall"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

local tinsert = table.insert
local ccreate = coroutine.create
local cyield = coroutine.yield
local cresume = coroutine.resume

-- Table of all of the walls that can possibly be put into the board
local possible_walls = {}
do
	for c=1,Board.SIZE-1 do
		for r=0,Board.SIZE-2 do
			local w = Wall(-1, r, c, r+2, c)
			if w:valid() then
				tinsert(possible_walls, w)
			end
		end
	end
	for r=1,Board.SIZE-1 do
		for c=0,Board.SIZE-2 do
			local w = Wall(-1, r, c, r, c+2)
			if w:valid() then
				tinsert(possible_walls, w)
			end
		end
	end
end

-- Coroutine function for generating moves
local function move_gen(self, plyid)
	local p = self.board.players[plyid]
	cyield() -- Yield once after getting our arguments
	
	-- Compute player pawn movements
	do
		local t = self.board:getAdjHop(Coord(p.r, p.c))
		for i=1,#t do
			local move = Move(plyid, p.r, p.c, unCoord(t[i]))
			move = GameTree:new(self.board:copy():applyMove(move), move)
			cyield(move)
		end
	end
	
	-- Compute wall moves
	if p.walls > 0 then
		for i=1,#possible_walls do
			if self.board:checkWall(possible_walls[i]) then
				local w = possible_walls[i]:copy()
				w.owner = plyid
				w = GameTree:new(self.board:copy():applyMove(w), w)
				cyield(w)
			end
		end
	end
	
	-- If we don't have any moves, create a pass move
	if #self == 0 then
		local move = Move(plyid, p.r, p.c, p.r, p.c)
		cyield(move)
	end
	
	-- Generate nils for infinity
	while true do
		cyield(nil)
	end
end

-- Initializer
function GameTree:new(board, move)
	local t = setmetatable({
		board = board,
		move = move,
		score = -math.huge,
		sorted = false,
	}, self)
	return t
end

-- Handles gtree[index], generating moves dynamically.
-- This isn't called if gtree[index] exists, so we
-- don't have to check for already-generated moves.
function GameTree:__index(k)
	if type(k) == "number" then
		assert(k >= 1)
		assert(k == 1 or self[k-1])
		local ok, node = cresume(self.generator)
		if not ok then
			error(debug.traceback(self.generator,node,0))
		end
		self[k] = node
		if node then self.sorted = false end
		return node
	else
		return GameTree[k]
	end
end

-- Initializes the move generator coroutine.
-- This should be called before indexing the tree is done.
function GameTree:initGenerator(plyid)
	if self.generator then return end
	self.generator = ccreate(move_gen)
	local ok, err = cresume(self.generator, self, plyid)
	if not ok then
		error(debug.traceback(self.generator,err,0))
	end
end

-- Sets this node's score. Used during sorting.
function GameTree:setScore(s)
	self.score = s
end

local compare = function(a,b) return a.score > b.score end -- Greater than for descending sorted

-- Sorts the generated moves based on their score, so that Alpha-beta can cut off earlier.
function GameTree:sort()
	if self.sorted then return end
	
	--table.sort(self, compare)
	Utils.arraySort(self,nil,nil,compare)
	self.sorted = true
end

return GameTree
