
package.path = "./windows/?.lua;"..package.path

local oldrequrie = require

local ffi = require "ffi"
local SocketUtils = require "SocketUtils"
local Board = require "board"
local AI = require "ai"
local Wall = require "wall"
local Move = require "move"
local Utils = require "utils"
local Coord, unCoord = Utils.Coord, Utils.unCoord

local PORT = 51894
local BUFFER_LEN = 4096

local function printf(...)
	print(string.format(...))
end

local buffer = ffi.new("char[?]", BUFFER_LEN)
local function readLine(socket)
	local nchars, err = SocketUtils.ReadLine(socket, buffer, BUFFER_LEN)
	if err then
		return nil, err
	else
		return ffi.string(buffer, nchars)
	end
end

local function write(socket, str)
	SocketUtils.WriteN(socket, str, #str)
end

local function writeAck(socket)
	write(socket, "ack\n")
end

local colorgrid = Utils.ColorGrid()
local function printBoard(board)
	ffi.fill(colorgrid, ffi.sizeof(Utils.ColorGrid))
	Utils.colorPlayers(board, colorgrid)
	board:print(colorgrid)
end

local function processCmd(socket, ai, cmd, args)
	
	-- ------------------------------------------------------------------------------------
	-- Updates
	
	if cmd == "m" then
		local id, r, c = args:match("^(%d+) (%d+),(%d)$")
		if not id then
			print("Invalid move line:", args)
			return true
		end
		id = tonumber(id)
		r,c = tonumber(r), tonumber(c)
		
		printf("Move: %d to %d,%d", id, r, c)
		ai:notifyMove(id, r, c)
		writeAck(socket)
		
		printBoard(ai:getBoard())
		
		if ai:getBoard():isTerminal() then
			print("--- Game Over ---")
			return true
		end
		
	elseif cmd == "w" then
		local id, r1,c1, r2,c2 = args:match("^(%d+) (%d+),(%d) (%d+),(%d)$")
		if not id then
			print("Invalid wall line:", args)
			return true
		end
		id = tonumber(id)
		r1,c1, r2,c2 = tonumber(r1), tonumber(c1), tonumber(r2), tonumber(c2)
		local w = Wall(id, r1,c1, r2,c2)
		
		printf("Wall: %s", w)
		ai:notifyWall(w)
		writeAck(socket)
		
		printBoard(ai:getBoard())
		
	elseif cmd == "i" then
		local id = tonumber(args)
		if not id then
			print("Invalid invalidate line:", args)
			return true
		end
		
		printf("Invalidate: %d", id)
		ai:notifyInvalidate(id)
		writeAck(socket)
		
		printBoard(ai:getBoard())
	
	-- ------------------------------------------------------------------------------------
	-- Get
	
	elseif cmd == "g" then
		print("Generating move...")
		local m = ai:getMove()
		if ffi.istype(Move, m) then
			print("\tGot move:", m)
			write(socket, string.format("m %d,%d %d,%d\n", m.prevr, m.prevc, m.r, m.c))
		elseif ffi.istype(Wall, m) then
			print("\tGot wall:", m)
			write(socket, string.format("w %d,%d %d,%d\n", m.r1,m.c1, m.r2,m.c2))
		else
			error("Got bad move object from ai:getMove(): "..tostring(m))
		end
	
	-- ------------------------------------------------------------------------------------
	-- Part 1 Support
	
	elseif cmd == "adj" then
		local r,c = args:match("^(%d+),(%d)$")
		if not r then
			print("Invalid adj line:", args)
			return true
		end
		
		printf("GetAdj: %s,%s", r, c)
		
		local adj = ai:getNeighbors(tonumber(r), tonumber(c))
		for i=1,#adj do
			adj[i] = string.format("%d,%d", adj[i][1], adj[i][2])
		end
		write(socket, table.concat(adj, " "))
		write(socket, "\n")
		
	elseif cmd == "path" then
		local r1,c1,r2,c2 = args:match("^(%d+),(%d) (%d+),(%d)$")
		if not r1 then
			print("Invalid adj line:", args)
			return true
		end
		
		printf("GetPath: %s,%s -> %s,%s", r1,c1, r2,c2)
		
		local path = ai:getPath(tonumber(r1),tonumber(c1),tonumber(r2), tonumber(c2))
		for i=1,#path do
			path[i] = string.format("%d,%d", unCoord(path[i]))
		end
		write(socket, table.concat(path, " "))
		write(socket, "\n")
	
	-- ------------------------------------------------------------------------------------
	
	else
		print("Unknown command:", cmd)
		return true
	end
end

local function main(cl_socket)
	print("Connection received")
	local ai
	do
		-- Receive header
		local header, err = readLine(cl_socket)
		if not header then return end
		local me, walls, locs = header:match("^(%d+) +(%d+) +(.-)$")
		if not me then
			print("Got invalid header:", header)
			return
		end
		
		print("Received connection.")
		print("Me:", me)
		print("Walls:", walls)
		local locations = {}
		local i = 1
		for l in locs:gmatch("[^%s]+") do
			if l == "inv" then
				print("Player "..i.." invalid")
				table.insert(locations, false)
			else
				r,c = l:match("(%d+),(%d+)")
				r,c = tonumber(r), tonumber(c)
				if not r then
					print("Got invalid header:", header)
					return
				end
				print("Player "..i.." location:", r, c)
				table.insert(locations, Coord(r,c))
			end
		end
		writeAck(cl_socket)
		
		ai = AI:new(tonumber(me), tonumber(walls), locations)
	end
	
	while true do
		local cmdstr, err = readLine(cl_socket)
		if err then
			if err ~= "eof" then
				error(err)
			end
			print("Connection closed")
			break
		end
		
		local cmd, args = cmdstr:match("^([^ ]+) ?(.-)$")
		if processCmd(cl_socket, ai, cmd, args) then
			print("Connection terminated due to protocol errors")
			break
		end
		
		local c = Utils.getch_nonblock()
		if c == "d" then
			print("--- Debug mode ---")
			require("main_cli")(ai)
		elseif c == "r" then
			print("--- Resetting ---")
			break
		end
	end
	ai:shutdown()
	print(string.rep("-", 60))
end

local function xpcall_hook(err)
	return debug.traceback(err, 2)
end

local sv_socket, err = SocketUtils.CreateTcpServerSocket({port = PORT, backlog=1, nonblocking=false, nodelay=false})
if not sv_socket then error(err) end
print("Server starting")
while true do
	local cl_socket = assert(sv_socket:Accept())
	local ok, err = xpcall(main, xpcall_hook, cl_socket)
	assert(cl_socket:CloseDown())
	ffi.gc(cl_socket, nil)
	if not ok then
		print(err)
	end
	--break
end
sv_socket:CloseDown()
ffi.gc(sv_socket, nil)
sv_socket = nil
