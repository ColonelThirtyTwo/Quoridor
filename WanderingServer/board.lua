
local ffi = require "ffi"
local bit = require "bit"

local Board = {}
package.loaded[...] = Board
Board.__index = Board
Board.SIZE = 9

--local Coord = require "coord"
local Utils = require "utils"
local Queue = require "queue"
local Coord, unCoord = Utils.Coord, Utils.unCoord
local Wall = require "wall"
local Move = require "move"

local grid = ffi.typeof("short[9][9]")
local LEFT  = bit.lshift(1,0)
local RIGHT = bit.lshift(1,1)
local UP    = bit.lshift(1,2)
local DOWN  = bit.lshift(1,3)
Board.LEFT, Board.RIGHT, Board.UP, Board.DOWN = LEFT, RIGHT, UP, DOWN
local directions = {LEFT, RIGHT, UP, DOWN}
local bits2adj = {}
do
	for i=0,bit.bor(LEFT, RIGHT, UP, DOWN) do
		local t = {}
		if bit.band(i, LEFT) ~= 0 then
			table.insert(t, {0,-1})
		end
		if bit.band(i, RIGHT) ~= 0 then
			table.insert(t, {0,1})
		end
		if bit.band(i, UP) ~= 0 then
			table.insert(t, {-1,0})
		end
		if bit.band(i, DOWN) ~= 0 then
			table.insert(t, {1,0})
		end
		bits2adj[i] = t
	end
end

local goal_atgoals = {
	[1] = function(d)
		local r,c = unCoord(d)
		return r == 0
	end,
	[2] = function(d)
		local r,c = unCoord(d)
		return r == Board.SIZE-1
	end,
	[3] = function(d)
		local r,c = unCoord(d)
		return c == Board.SIZE-1
	end,
	[4] = function(d)
		local r,c = unCoord(d)
		return c == 0
	end,
}

-- ------------------------------------------------------------------------------------

function Board:new(players)
	local b = setmetatable({},self)
	b.players = players
	b.walls = {}
	b.grid = grid()
	for r=0,self.SIZE-1 do
		for c=0,self.SIZE-1 do
			b.grid[r][c] = bit.bor(
				r ~= 0           and UP    or 0,
				r ~= self.SIZE-1 and DOWN  or 0,
				c ~= 0           and LEFT  or 0,
				c ~= self.SIZE-1 and RIGHT or 0
			)
		end
	end
	
	return b
end

function Board:__index(key)
	if type(key) == "number" then
		local r,c = unCoord(key)
		assert(r >= 0 and r < self.SIZE and c >= 0 and c < self.SIZE)
		return self.grid[r][c]
	else
		return Board[key]
	end
end

function Board:__newindex(key, value)
	if type(key) == "number" then
		local r,c = unCoord(key)
		assert(r >= 0 and r < self.SIZE and c >= 0 and c < self.SIZE)
		self.grid[r][c] = value
	else
		rawset(self, key, value)
	end
end

function Board:get(r,c)
	assert(r >= 0 and r < self.SIZE and c >= 0 and c < self.SIZE)
	return self.grid[r][c]
end
function Board:set(r,c,v)
	assert(r >= 0 and r < self.SIZE and c >= 0 and c < self.SIZE)
	self.grid[r][c] = v
end

function Board:getNeighbor(coord, i)
	local r,c = unCoord(coord)
	local adj = bits2adj[self:get(r,c)]
	if adj[i] then
		return Coord(r+adj[i][1], c+adj[i][2])
	end
end

function Board:getPlayerAt(r,c)
	if not c then r,c = unCoord(r) end
	for i=1,#self.players do
		local p = self.players[i]
		if p.valid and p.r == r and p.c == c then
			return p
		end
	end
end

function Board:moveInDir(r,c,dir)
	if not dir then
		dir = c
		r,c = unCoord(r)
	end
	assert(self:validCoord(r,c))
	local b = self.grid[r][c]
	if bit.band(b, dir) ~= 0 then
		return r+bits2adj[dir][1][1], c+bits2adj[dir][1][2]
	end
end

function Board:getAdjHop(loc1,c)
	if c then loc1 = Coord(loc1, c) end
	-- Hnng ugly
	local t = {}
	for i=1,#directions do
		local d = directions[i]
		local r2,c2 = self:moveInDir(loc1, d)
		if r2 then
			local loc2 = Coord(r2,c2)
			if self:getPlayerAt(loc2) then
				local r3,c3 = self:moveInDir(r2,c2, d)
				if r3 and not self:getPlayerAt(r3,c3) then
					table.insert(t, Coord(r3,c3))
				else
					print("+",r2,c2)
					local loc3 = Coord(r3,c3)
					for j=1,4 do
						local loc4 = self:getNeighbor(loc2, j)
						if not loc4 then break end
						print("-",unCoord(loc4))
						if loc4 ~= loc3 and loc4 ~= loc1 then
							table.insert(t, loc4)
						end
					end
				end
			else
				table.insert(t, loc2)
			end
		end
	end
	return t
end

function Board:validCoord(r,c)
	if not c then r,c = unCoord(r) end
	return r >= 0 and r < self.SIZE and c >= 0 and c < self.SIZE
end

function Board:copy()
	local b = setmetatable({},Board)
	b.players = {}
	for i=1,#self.players do b.players[i] = self.players[i]:copy() end
	b.walls = Utils.arrayCopy(self.walls)
	b.grid = ffi.new(grid, self.grid)
	return b
end

function Board:checkWall(wall)
	if not wall:valid() then return false end
	for i=1,#self.walls do
		if wall:intersects(self.walls[i]) then
			return false
		end
	end
	
	local oldgrid = self.grid
	self.grid = grid()
	ffi.copy(self.grid, oldgrid, ffi.sizeof(grid))
	self:addWall(wall, true)
	for i=1,#self.players do
		if self.players[i].valid and not self:canReachGoal(i) then
			self.grid = oldgrid
			return false
		end
	end
	self.grid = oldgrid
	return true
end

function Board:nextPly(plyid)
	repeat
		plyid = (plyid % #self.players) + 1
	until self.players[plyid].valid
	return plyid
end

-- ------------------------------------------------------------------------------------

function Board:updatePlayerLocation(plyid, r, c)
	assert(r >= 0 and r < self.SIZE and c >= 0 and c < self.SIZE)
	self.players[plyid].r, self.players[plyid].c = r, c
end

function Board:addWall(wall, onlytoadjlist)
	if wall:horizontal() then
		self:set(wall.r1  , wall.c1  , bit.band(self:get(wall.r1  , wall.c1  ), bit.bnot(UP)) )
		self:set(wall.r1  , wall.c1+1, bit.band(self:get(wall.r1  , wall.c1+1), bit.bnot(UP)) )
		self:set(wall.r1-1, wall.c1  , bit.band(self:get(wall.r1-1, wall.c1  ), bit.bnot(DOWN)) )
		self:set(wall.r1-1, wall.c1+1, bit.band(self:get(wall.r1-1, wall.c1+1), bit.bnot(DOWN)) )
	else
		self:set(wall.r1  , wall.c1  , bit.band(self:get(wall.r1  , wall.c1  ), bit.bnot(LEFT)) )
		self:set(wall.r1+1, wall.c1  , bit.band(self:get(wall.r1+1, wall.c1  ), bit.bnot(LEFT)) )
		self:set(wall.r1  , wall.c1-1, bit.band(self:get(wall.r1  , wall.c1-1), bit.bnot(RIGHT)) )
		self:set(wall.r1+1, wall.c1-1, bit.band(self:get(wall.r1+1, wall.c1-1), bit.bnot(RIGHT)) )
	end
	
	if not onlytoadjlist then
		table.insert(self.walls, wall)
		self.players[wall.owner].walls = self.players[wall.owner].walls - 1
	end
end

function Board:invalidate(plyid)
	self.players[plyid].valid = false
end

function Board:applyMove(m)
	if ffi.istype(Move, m) then
		self:updatePlayerLocation(m.plyid, m.r, m.c)
	elseif ffi.istype(Wall, m) then
		self:addWall(m)
	else
		error("Unknown move: "..tostring(m),2)
	end
	return self
end

-- ------------------------------------------------------------------------------------

function Board:isTerminal()
	for i=1,#self.players do
		local p = self.players[i]
		if p.valid and goal_atgoals[i](Coord(p.r, p.c)) then
			return p
		end
	end
end

function Board:evaluate(plyid)
	local myscore = 0
	local enemyscore = 0
	local activeEnemies = 0
	
	for i=1,#self.players do
		local p = self.players[i]
		if p.valid then
			local s = #self:findPathToGoal(Coord(p.r,p.c), i)-1
			if i == plyid then
				myscore = -s
			else
				activeEnemies = activeEnemies + 1
				enemyscore = enemyscore - 20 / math.sqrt(s)
			end
		end
	end
		
	if activeEnemies == 0 then
		return myscore
	else
		return myscore + enemyscore / activeEnemies
	end
end

local function boardNextMoves(self, plyid)
	coroutine.yield()
	
	local canmove = false
	local p = self.players[plyid]
	local t = self:getAdjHop(Coord(p.r, p.c))
	for i=1,#t do
		canmove = true
		coroutine.yield(Move(plyid, p.r, p.c, unCoord(t[i])))
	end
	
	if p.walls > 0 then
		for c=1,self.SIZE-1 do
			for r=0,self.SIZE-2 do
				w = Wall(plyid, r, c, r+2, c)
				if self:checkWall(w) then
					canmove = true
					coroutine.yield(w)
				end
			end
		end
		for r=1,self.SIZE-1 do
			for c=0,self.SIZE-2 do
				w = Wall(plyid, r, c, r, c+2)
				if self:checkWall(w) then
					canmove = true
					coroutine.yield(w)
				end
			end
		end
	end
	
	if not canmove then
		coroutine.yield(Coord(p.r, p.c))
	end
end

function Board:nextMoves(plyid)
	assert(plyid >= 1 and plyid <= #self.players, plyid)
	--local c = coroutine.wrap(boardNextMoves)
	local c = Utils.coroutineWrapDebug(boardNextMoves)
	c(self, plyid)
	return c
end

-- ------------------------------------------------------------------------------------

function Board:_bfs(start, atgoal, canreach)
	local queue = Queue:new()
	queue:add(start)
	local closed = {[start] = false}
	
	while not queue:empty() do
		local current = queue:poll()
		if atgoal(current) then
			if canreach then
				return true
			else
				-- Reconstruct path
				local l = {}
				while current do
					l[#l+1] = current
					current = closed[current]
				end
				Utils.arrayReverse(l)
				return l
			end
		end
		for i=1,4 do
			local v = self:getNeighbor(current, i)
			if not v then break end
			if closed[v] == nil then
				closed[v] = current
				queue:add(v)
			end
		end
	end
	return nil
end

function Board:findPathToLoc(start, finish)
	local atgoal = function(l) return l == finish end
	return self:_bfs(start, atgoal)
end

function Board:findPathToGoal(start, plyid)
	return self:_bfs(start, goal_atgoals[plyid])
end

function Board:canReachGoal(plyid)
	local l = Coord(self.players[plyid].r, self.players[plyid].c)
	return self:_bfs(l, goal_atgoals[plyid], true)
end

-- ------------------------------------------------------------------------------------

local bits2chars = {
	[0] = " ",
	[LEFT] = string.char(181),
	[RIGHT] = string.char(198),
	[UP] = string.char(208),
	[DOWN] = string.char(210),
	[bit.bor(LEFT, RIGHT)] = string.char(205),
	[bit.bor(LEFT, UP)] = string.char(188),
	[bit.bor(LEFT, DOWN)] = string.char(187),
	[bit.bor(RIGHT,UP)] = string.char(200),
	[bit.bor(RIGHT, DOWN)] = string.char(201),
	[bit.bor(UP, DOWN)] = string.char(186),
	[bit.bor(LEFT,RIGHT,UP)] = string.char(202),
	[bit.bor(LEFT,RIGHT,DOWN)] = string.char(203),
	[bit.bor(LEFT,UP,DOWN)] = string.char(185),
	[bit.bor(RIGHT,UP,DOWN)] = string.char(204),
	[bit.bor(LEFT,RIGHT,UP,DOWN)] = string.char(206),
}

function Board:print(colors, noplayers)
	if not noplayers then
		for i=1,#self.players do
			io.write(i, ": ")
			local p = self.players[i]
			if p.valid then
				io.write("(",p.r,",",p.c,") Walls: ",p.walls)
			else
				io.write("invalidated")
			end
			
			if i ~= #self.players then
				io.write(", ")
			end
		end
		io.write("\n")
	end
	
	io.write(" ")
	for c=0,self.SIZE-1 do
		io.write("|")
	end
	io.write("\n")
	
	for r=0,self.SIZE-1 do
		io.write("-")
		for c=0,self.SIZE-1 do
			local chr = bits2chars[self:get(r,c)]
			assert(chr, self:get(r,c))
			
			if colors and colors[r][c] and colors[r][c] ~= 0 then
				Utils.writeColored(chr, colors[r][c])
			else
				io.write(chr)
			end
		end
		io.write("\n")
	end
end

return Board
