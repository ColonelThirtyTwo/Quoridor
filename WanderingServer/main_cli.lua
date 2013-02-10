
local AI = require "ai"
local Wall = require "wall"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

local colorgrid = require("ffi").typeof("int[9][9]")

local function parseCoord(str)
	local r, c = str:match("^(%d+),(%d+)$")
	return tonumber(r), tonumber(c)
end

local ai
do
	io.write("Number of Players: ")
	local numplys = assert(tonumber(io.read()), "not a number")
	assert(({[1]=true, [2]=true, [4]=true})[numplys], "invalid number of players")
	
	io.write("Our player: ")
	local me = assert(tonumber(io.read()), "not a number")
	
	io.write("Number of Walls: ")
	local numwalls = assert(tonumber(io.read()), "not a number")
	
	local playerlocs = {}
	for i=1,numplys do
		io.write("Player ",i," location: ")
		local locstr = io.read()
		if locstr == "invalid" then
			playerlocs[i] = false
		else
			local r, c = parseCoord(locstr)
			assert(r and c, "invalid coordinates")
			playerlocs[i] = Coord(r,c)
		end
	end
	
	ai = AI:new(me, numwalls, playerlocs)
end

local playercolors = {
	[1] = bit.bor(Utils.textColors.red, Utils.textColors.intensity),
	[2] = bit.bor(Utils.textColors.blue, Utils.textColors.intensity),
	[3] = bit.bor(Utils.textColors.green, Utils.textColors.intensity),
	[4] = bit.bor(Utils.textColors.red, Utils.textColors.green, Utils.textColors.intensity),
}

local function processCmd(cmd, args)
	if cmd == "q" or cmd == "quit" then
		return true
	elseif cmd == "p" or cmd == "print" then
		local r,c
		if tonumber(args) then
			local p = ai:getBoard().players[tonumber(args)]
			if p and p.valid then
				r,c = p.r, p.c
			end
		else
			r,c = parseCoord(args)
		end
		
		local b = ai:getBoard()
		local cgr = colorgrid()
		if r and c then
			if r >= 0 and r < b.SIZE and c >= 0 and c < b.SIZE then
				cgr[r][c] = Utils.textColors.red
			else
				print("Invalid Coordinates")
				return
			end
		else
			for i=1,#b.players do
				local p = b.players[i]
				if p.valid then
					cgr[p.r][p.c] = playercolors[i]
				end
			end
		end
		b:print(cgr)
	elseif cmd == "w" or cmd == "wall" then
		local owner, loc1, loc2 = args:match("^(%d+) +([^ ]+) +([^ ]+)$")
		owner = tonumber(owner)
		if not owner then
			print("Invalid arguments")
			return
		end
		local r1,c1 = parseCoord(loc1)
		local r2,c2 = parseCoord(loc2)
		if not (r1 and r2) then
			print("Invalid arguments")
			return
		end
		local w = Wall(owner, r1, c1, r2, c2)
		if ai:getBoard():checkWall(w) then
			ai:notifyWall(w)
		else
			print("Invalid wall")
		end
	elseif cmd == "adj" then
		local r,c = parseCoord(args)
		if not (r and c) then
			print("Invalid coordinates")
			return
		end
		local cgr = colorgrid()
		local adj = ai:getNeighbors(r,c)
		for i=1,#adj do
			print(adj[i][1], adj[i][2])
			cgr[adj[i][1]][adj[i][2]] = Utils.textColors.red
		end
		ai:getBoard():print(cgr, true)
	elseif cmd == "path" then
		local loc1, loc2 = args:match("^([^ ]+) +([^ ]+)$")
		if not loc1 then
			print("Invalid coordinates")
			return
		end
		
		local r1,c1 = parseCoord(loc1)
		local r2,c2 = parseCoord(loc2)
		if not r1 or not r2 then
			print("Invalid coordinates")
			return
		end
		
		local b = ai:getBoard()
		local path = b:findPathToLoc(Coord(r1,c1), Coord(r2,c2))
		if not path then
			print("No path")
		else
			local cgr = colorgrid()
			for i=1,#path do
				local r,c = unCoord(path[i])
				print(i, r,c)
				assert(b:validCoord(r,c))
				cgr[r][c] = Utils.textColors.red
			end
			b:print(cgr)
		end	
	else
		print("Unknown command")
	end
end

while true do
	io.write("> ")
	local cmdstr = io.read()
	
	local cmd, args = cmdstr:match("^([^ ]+) ?(.-)$")
	if processCmd(cmd, args) then break end
end
