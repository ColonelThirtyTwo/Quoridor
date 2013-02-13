
-- Queue data structure
-- See http://www.lua.org/pil/11.4.html

local Queue = {}
Queue.__index = Queue

function Queue:new()
	return setmetatable({
		first = 1,
		last = 1,
	}, self)
end

function Queue:add(v)
	self[self.last] = v
	self.last = self.last + 1
end

function Queue:poll()
	if self.first == self.last then
		error("Attempted to poll empty queue", 2)
	end
	
	local v = self[self.first]
	self[self.first] = nil
	self.first = self.first + 1
	return v
end

function Queue:peek()
	if self.first == self.last then
		error("Attempted to peek empty queue", 2)
	end
	
	return self[self.first]
end

function Queue:__len()
	return self.last - self.first
end

function Queue:empty()
	return self.last == self.first
end

return Queue
