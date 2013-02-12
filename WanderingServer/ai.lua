
local AI = {}
AI.__index = AI

local Board = require "board"
local Player = require "player"
local GameTree = require "gametree"
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
	node:generate(plyid)
	
	if plyid == maxid then
		for i=1,#node do
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
		end
		returnscore = a
	else
		for i=1,#node do
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
		end
		returnscore = b
	end
	
	node:sort()
	return bestmove, returnscore
end

--local profi = require "ProFi"
--profi:setGetTimeMethod(Utils.getTime)

function AI:getMove()
	
	--if self.currentboard:numActivePlayers() == 1 then
	--	-- Nothing that complicated for a 1P game
	--	local move, _ = alphabeta(self.currentboard, 1, self.me, -math.huge, math.huge, self.me, math.huge)
	--	return move
	--end
	
	--profi:start()
	
	local start = getTime()
	local finishby = start+8
	local tree = GameTree:new(self.currentboard)
	local depth = 1
	local bestmove = nil
	while true do
		local ok, move = xpcall(alphabeta, xpcall_hook, tree, depth, self.me, -math.huge, math.huge, self.me, finishby)
		-- alphabeta(board, depth, maxid, a, b, plyid, finishby)
		if not ok then
			if move == OUT_OF_TIME then
				break
			else
				error(move,0)
			end
		end
		bestmove = move
		io.write("\tAlphabeta d=", depth, " finished in ", (getTime()-start), " seconds\n")
		depth = depth + 1
	end
	io.write("\tMax time elapsed\n")
	
	--profi:stop()
	
	return bestmove
end

function AI:shutdown()
	--profi:writeReport("profile.txt")
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
