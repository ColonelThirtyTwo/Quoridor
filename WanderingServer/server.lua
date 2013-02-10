
local SocketUtils = require "windows.socketutils"

local Server = {}
Server.__index = Server

function Server:new(port)
	local server = setmetatable({
		port = port or 51894,
	}, self)
	return server
end

function Server:start()
	local socket, err = SocketUtils.CreateTcpServerSocket({port = self.port, backlog=3, nonblocking=true, nodelay=true})
	if not socket then
		error(err)
	end
end
