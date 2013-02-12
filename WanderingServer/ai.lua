
local AI = {}
AI.__index = AI

local Board = require "board"
local Player = require "player"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

local DEPTH_LIMIT = 25

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

function AI:notifyMove(plyid, r,c)
	self.currentboard:updatePlayerLocation(plyid, r, c)
	self.currentply = self.currentboard:nextPly(plyid)
end

function AI:notifyWall(wall)
	assert(self.currentboard:checkWall(wall))
	self.currentboard:addWall(wall)
	self.currentply = self.currentboard:nextPly(wall.owner)
end

function AI:notifyInvalidate(plyid)
	self.currentboard:invalidate(plyid)
	if plyid == self.currentply then
		self.currentply = self.currentboard:nextPly(self.currentply)
	end
end

function AI:getBoard()
	return self.currentboard
end

-- ------------------------------------------------------------------------------------

local getTime = Utils.getTime
local OUT_OF_TIME = {}

local function xpcall_hook(err)
	if err ~= OUT_OF_TIME then
		return debug.traceback(err,2)
	else
		return err
	end
end

local function alphabeta(board, depth, maxid, a, b, plyid, finishby)
	if getTime() > finishby then
		error(OUT_OF_TIME, 0)
	end
	
	local p = board:isTerminal()
	if p then
		if p.id == maxid then
			return nil, 5000+depth
		else
			return nil, -5000-depth
		end
	end
	
	if depth <= 0 then
		return nil, board:evaluate(maxid), depth
	end
	
	local nextid = board:nextPly(plyid)
	
	if plyid == maxid then
		local bestmove = nil
		for move in board:nextMoves(plyid) do
			local _, score = alphabeta(board:copy():applyMove(move), depth-1, maxid, a, b, nextid, finishby)
			if score > a then
				bestmove = move
				a = score
			end
			if b <= a then
				break
			end
		end
		return bestmove, a
	else
		local bestmove = nil
		for move in board:nextMoves(plyid) do
			local _, score = alphabeta(board:copy():applyMove(move), depth-1, maxid, a, b, nextid, finishby)
			if score < b then
				bestmove = move
				b = score
			end
			if b <= a then
				break
			end
		end
		return bestmove, b
	end
end

function AI:getMove()
	if self.currentboard:numActivePlayers() == 1 then
		-- Nothing that complicated for a 1P game
		local move, _ = alphabeta(self.currentboard, 1, self.me, -math.huge, math.huge, self.me, math.huge)
		return move
	end
	
	local start = getTime()
	local finishby = start+9
	local depth = 1
	local bestmove = nil
	while depth < DEPTH_LIMIT do
		local ok, move = xpcall(alphabeta, xpcall_hook, self.currentboard, depth, self.me, -math.huge, math.huge, self.me, finishby)
		-- alphabeta(board, depth, maxid, a, b, plyid, finishby)
		if not ok then
			if move == OUT_OF_TIME then
				io.write("\tMax time elapsed\n")
				break
			else
				error(move,0)
			end
		end
		bestmove = move
		io.write("\tAlphabeta d=", depth, " finished in ", (getTime()-start), " seconds\n")
		depth = depth + 1
	end
	return bestmove
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
