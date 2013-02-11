
local AI = {}
AI.__index = AI

local Board = require "board"
local Player = require "player"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

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
	print(plyid, self.currentply)
end

function AI:notifyWall(wall)
	assert(self.currentboard:checkWall(wall))
	self.currentboard:addWall(wall)
	self.currentply = self.currentboard:nextPly(wall.owner)
	print(wall.owner, self.currentply)
end

function AI:notifyInvalidate(plyid)
	self.currentboard:invalidate(plyid)
	if plyid == self.currentply then
		self.currentply = self.currentboard:nextPly(self.currentply)
		print(plyid, self.currentply)
	end
end

function AI:getBoard()
	return self.currentboard
end

-- ------------------------------------------------------------------------------------

local function alphabeta(board, depth, maxid, a, b, plyid)
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
		local bestmove, bestdepth = nil, math.huge
		for move in board:nextMoves(plyid) do
			local _, score = alphabeta(board:copy():applyMove(move), depth-1, maxid, a, b, nextid)
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
			local _, score = alphabeta(board:copy():applyMove(move), depth-1, maxid, a, b, nextid)
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
	--local start = os.clock()
	local move, _ = alphabeta(self.currentboard, 2, self.me, -math.huge, math.huge, self.me)
	--local dt = os.clock()-start
	--print("Generated move in",dt,"seconds")
	return move
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
