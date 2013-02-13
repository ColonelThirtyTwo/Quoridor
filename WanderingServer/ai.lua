
--- AI main file

local AI = {}
AI.__index = AI

local Board = require "board"
local Player = require "player"
local GameTree = require "gametree"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

-- IDDFS depth limit
local DEPTH_LIMIT = 3

-- Initializer
function AI:new(myid, numwalls, playerlocations)
	local ai = setmetatable({
		me = myid,
		placewall = false,
	},self)
	
	local players = {}
	for i=1,#playerlocations do
		if playerlocations[i] == false then
			players[i] = Player(i,0,0,numwalls,false)
		else
			local r,c = unCoord(playerlocations[i])
			players[i] = Player(i,r,c,numwalls,true)
		end
	end
	
	ai.currentboard = Board:new(players)
	ai.currentply = 1
	return ai
end

-- Notifies the AI of a player's move
function AI:notifyMove(plyid, r,c)
	self.currentboard:updatePlayerLocation(plyid, r, c)
	self.currentply = self.currentboard:nextPly(plyid)
end

-- Notifies the AI of a wall place
function AI:notifyWall(wall)
	assert(self.currentboard:checkWall(wall))
	self.currentboard:addWall(wall)
	self.currentply = self.currentboard:nextPly(wall.owner)
end

-- Notifies the AI of a player invalidation
function AI:notifyInvalidate(plyid)
	self.currentboard:invalidate(plyid)
	if plyid == self.currentply then
		self.currentply = self.currentboard:nextPly(self.currentply)
	end
end

-- Gets the current board
function AI:getBoard()
	return self.currentboard
end

-- ------------------------------------------------------------------------------------

local getTime = Utils.getTime
local OUT_OF_TIME = {}

-- Hook for xpcall, to add a traceback if there is a real error.
local function xpcall_hook(err)
	if err ~= OUT_OF_TIME then
		return debug.traceback(err,2)
	else
		return err
	end
end

-- Recursive minimax function with alpha-beta pruning
-- Will throw a OUT_OF_TIME error if the current time exceeds the
-- time specified by the finishby argument.
local function alphabeta(node, depth, maxid, a, b, plyid, finishby)
	if getTime() > finishby then
		error(OUT_OF_TIME, 0)
	end
	
	local p = node.board:isTerminal()
	if p then
		local score = p.id == maxid and 5000+depth or -5000-depth
		node:setScore(score)
		return nil, score
	end
	
	if depth <= 0 then
		local score = node.board:evaluate(maxid)
		node:setScore(score)
		return nil, score
	end
	
	local nextid = node.board:nextPly(plyid)
	local bestmove, returnscore
	node:initGenerator(plyid)
	
	if plyid == maxid then
		local i = 1
		while node[i] do
			local nextnode = node[i]
			local move = nextnode.move
			local _, score = alphabeta(nextnode, depth-1, maxid, a, b, nextid, finishby)
			if score > a then
				bestmove = move
				a = score
			end
			if b <= a then
				break
			end
			i=i+1
		end
		returnscore = a
	else
		local i = 1
		while node[i] do
			local nextnode = node[i]
			local move = nextnode.move
			local _, score = alphabeta(nextnode, depth-1, maxid, a, b, nextid, finishby)
			if score < b then
				bestmove = move
				b = score
			end
			if b <= a then
				break
			end
			i=i+1
		end
		returnscore = b
	end
	
	node:sort()
	return bestmove, returnscore
end

-- Gets the move that the AI controlled player should make
function AI:getMove()
	local start = getTime()
	local finishby = start+8 -- 8 seconds to compute move + 2 seconds in case of network latency
	local tree = GameTree:new(self.currentboard)
	local depth = 1
	local bestmove = nil
	while depth <= DEPTH_LIMIT do
		local ok, move = xpcall(alphabeta, xpcall_hook, tree, depth, self.me, -math.huge, math.huge, self.me, finishby)
		if not ok then
			if move == OUT_OF_TIME then
				-- Ran out of time
				io.write("\tMax time elapsed\n")
				break
			else
				-- A real error
				error(move,0)
			end
		end
		bestmove = move
		io.write("\tAlphabeta d=", depth, " finished in ", (getTime()-start), " seconds\n")
		depth = depth + 1
	end
	return bestmove
end

-- Shuts down the AI
function AI:shutdown()
end

-- ------------------------------------------------------------------------------------

-- Part 1: Gets an array of neighbors
function AI:getNeighbors(r,c)
	local t = {}
	for i=1,4 do
		local d = self.currentboard:getNeighbor(Coord(r,c),i)
		if not d then break end
		table.insert(t, {unCoord(d)})
	end
	return t
end

-- Part 1: Gets a path from r1,c1 to r2,c2
function AI:getPath(r1,c1,r2,c2)
	return self.currentboard:findPathToLoc(Coord(r1,c1), Coord(r2,c2))
end

return AI
