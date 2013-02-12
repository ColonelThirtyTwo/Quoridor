
package.path = "./windows/?.lua;"..package.path

local AI = require "ai"
local Board = require "board"
local Wall = require "wall"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

local colorgrid = require("ffi").typeof("int[9][9]")

local function parseCoord(str)
	local r, c = str:match("^(%d+),(%d+)$")
	r,c = tonumber(r), tonumber(c)
	if r and c and r >= 0 and r < Board.SIZE and c >= 0 and c < Board.SIZE then
		return r,c
	end
end

local playercolors = {
	[1] = bit.bor(Utils.textColors.red, Utils.textColors.intensity),
	[2] = bit.bor(Utils.textColors.blue, Utils.textColors.intensity),
	[3] = bit.bor(Utils.textColors.green, Utils.textColors.intensity),
	[4] = bit.bor(Utils.textColors.red, Utils.textColors.green, Utils.textColors.intensity),
}

local function colorPlayers(board, cgr)
	for i=1,#board.players do
		local p = board.players[i]
		if p.valid then
			cgr[p.r][p.c] = playercolors[i]
		end
	end
end

local commands = {}
commands["q"] = function(args)
	return true
end
commands["quit"] = commands["q"]
commands["p"] = function(ai, args)
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
	colorPlayers(b,cgr)
	if r and c then
		if r >= 0 and r < b.SIZE and c >= 0 and c < b.SIZE then
			cgr[r][c] = Utils.textColors.bg_red
		else
			print("Invalid Coordinates")
			return
		end
	end
	b:print(cgr)
end
commands["print"] = commands["p"]

commands["w"] = function(ai, args)
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
end
commands["wall"] = commands["w"]

commands["m"] = function(ai, args)
	local id, loc = args:match("^(%d+) +([^ ]+)$")
	id = tonumber(id)
	if not id then
		print("Invalid arguments")
		return
	end
	local r,c = parseCoord(loc)
	if not r then
		print("Invalid location")
		return
	end
	
	ai:notifyMove(id, r, c)
end
commands["move"] = commands["m"]

commands["invalidate"] = function(ai, args)
	local id = tonumber(args)
	if not id then
		print("Invalid id")
		return
	end
	
	ai:notifyInvalidate(id)
end
commands["inv"] = commands["invalidate"]

commands["adj"] = function(ai, args)
	local r,c = parseCoord(args)
	if not (r and c) then
		print("Invalid coordinates")
		return
	end
	
	local cgr = colorgrid()
	colorPlayers(ai:getBoard(),cgr)
	cgr[r][c] = bit.bor(cgr[r][c], Utils.textColors.bg_blue)
	local adj = ai:getNeighbors(r,c)
	for i=1,#adj do
		print(adj[i][1], adj[i][2])
		cgr[adj[i][1]][adj[i][2]] = bit.bor(cgr[adj[i][1]][adj[i][2]], Utils.textColors.bg_red)
	end
	ai:getBoard():print(cgr, true)
end

commands["mdir"] = function(ai, args)
	local loc, dir = args:match("^([^ ]+) +([^ ]+)$")
	if not loc then
		print("Invalid arguments")
		return
	end
	local r,c = parseCoord(loc)
	if not r then
		print("Invalid coordinates")
		return
	end
	local bits = ({left=Board.LEFT, right=Board.RIGHT, up=Board.UP, down=Board.DOWN})[dir]
	if not bits then
		print("Invalid direction")
		return
	end
	
	local cgr = colorgrid()
	colorPlayers(ai:getBoard(),cgr)
	local r2,c2 = ai:getBoard():moveInDir(r,c,bits)
	if not r2 then
		print("Cannot move")
		return
	end
	
	assert(ai:getBoard():validCoord(r2,c2))
	print(r2, c2)
	cgr[r][c] = bit.bor(cgr[r][c], Utils.textColors.bg_blue)
	cgr[r2][c2] = bit.bor(cgr[r2][c2], Utils.textColors.bg_red)
	ai:getBoard():print(cgr)
end

commands["adjhop"] = function(ai, args)
	local r,c = parseCoord(args)
	if not (r and c) then
		print("Invalid coordinates")
		return
	end
	local cgr = colorgrid()
	colorPlayers(ai:getBoard(),cgr)
	cgr[r][c] = bit.bor(cgr[r][c], Utils.textColors.bg_blue)
	local adj = ai:getBoard():getAdjHop(r,c)
	for i=1,#adj do
		local r,c = unCoord(adj[i])
		assert(ai:getBoard():validCoord(r,c))
		print(r,c)
		cgr[r][c] = bit.bor(cgr[r][c], Utils.textColors.bg_red)
	end
	ai:getBoard():print(cgr, true)
end

commands["path"] = function(ai, args)
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
		colorPlayers(ai:getBoard(),cgr)
		for i=1,#path do
			local r,c = unCoord(path[i])
			print(i, r,c)
			assert(b:validCoord(r,c))
			cgr[r][c] = bit.bor(cgr[r][c], Utils.textColors.bg_red)
		end
		b:print(cgr)
	end
end

commands["help"] = function(ai, args)
	for k,_ in pairs(commands) do
		print(k)
	end
end

local function main(ai)
	while true do
		io.write("> ")
		local cmdstr = io.read()
		
		local cmd, args = cmdstr:match("^([^ ]+) ?(.-)$")
		--if processCmd(cmd, args) then break end
		local cmdfunc = commands[cmd]
		if cmdfunc then
			if cmdfunc(ai, args) then
				break
			end
		else
			print("Unknown command")
		end
	end
end

if not (...) then
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
	
	return main(AI:new(me, numwalls, playerlocs))
else
	return main
end

