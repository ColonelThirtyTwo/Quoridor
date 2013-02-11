
local ffi = require "ffi"
local bit = require "bit"
local floor = math.floor
local abs = math.abs

local Utils = {}

function printTable(t, depth, tabs)
	depth = depth or 3
	if depth <= 0 then return end
	tabs = tabs or 0
	local tstr = string.rep("\t", tabs)
	io.write(tstr,"{\n")
	for k,v in pairs(t) do
		print(tstr,k,v)
		if type(v) == "table" then
			printTable(v, depth-1, tabs+1)
		end
	end
	io.write(tstr,"}\n")
end

function Utils.coroutineWrapDebug(f)
	local r = coroutine.create(f)
	return function(...)
		local ok, a, b, c, d = coroutine.resume(r, ...)
		if not ok then
			error(debug.traceback(r,a,0),2)
		end
		return a,b,c,d
	end
end

-- ------------------------------------------------------------------------------------

function Utils.arrayCopy(a1, a2)
	a2 = a2 or {}
	for i=1,#a1 do
		a2[i] = a1[i]
	end
	return a2
end

function Utils.arrayReverse(arr)
	local l = #arr
	for i=1,floor(l/2) do
		arr[i], arr[l-i+1] = arr[l-i+1], arr[i]
	end
	return arr
end

-- ------------------------------------------------------------------------------------

-- Trick for packing coordinates into Lua numbers, which can then be used in tables, etc.
-- Only works for positive coordinates
function Utils.Coord(r,c)
	return bit.bor(bit.lshift(bit.band(r, 0xFF), 8), bit.band(c, 0xFF))
end
function Utils.unCoord(d)
	return bit.rshift(d, 8), bit.band(d, 0xFF)
end
local Coord, unCoord = Utils.Coord, Utils.unCoord
function Utils.addCoord(a, b)
	local r1, c1 = unCoord(a)
	local r2, c2 = unCoord(b)
	return Coord(r1+r2, c1+c2)
end

-- These work on negatives, but are more expensive
--[[
function Utils.NegCoord(r,c)
	return bit.bor(
		r < 0 and bit.lshift(1, 8+8-1) or 0,
		bit.lshift(bit.band(abs(r), 0x7F), 8),
		c < 0 and bit.lshift(1, 8-1) or 0,
		bit.band(abs(c), 0x7F)
	)
end
function Utils.unNegCoord(d)
	return bit.band(bit.rshift(d, 8), 0x7F) * (bit.band(bit.rshift(d,8+8-1),1) ~= 0 and -1 or 1),
		bit.band(d, 0x7F) * (bit.band(bit.rshift(d,8-1),1) ~= 0 and -1 or 1)
end
]]

--[[
function Utils.packLoc(r,c)
	return bit.bor(bit.lshift(r, 0xF), c)
end
function Utils.unpackLoc(d)
	return bit.rshift(d, 0xF), bit.band(d, 0xF)
end
function Utils.unpackLoc2Coord(d)
	return Coord(Utils.unpackLoc(d))
end
]]

function Utils.testCoord()
	for i=0,9 do
		for j=0,9 do
			local r,c = unCoord(Coord(i,j))
			assert(r == i and c == j, string.format("%d,%d != %d,%d (%d)", i,j, r,c, Coord(i,j)))
		end
	end
end

-- ------------------------------------------------------------------------------------

require "WTypes"
ffi.cdef[[
typedef struct {
	short x,y;
} COORD;
typedef struct {
	short left, top, right, bottom;
} SMALL_RECT;
typedef struct {
	COORD dwSize;
	COORD dwCursorPosition;
	WORD wAttributes;
	SMALL_RECT srWindow;
	COORD dwMaximumWindowSize;
} CONSOLE_SCREEN_BUFFER_INFO;

void* GetStdHandle(DWORD);
BOOL GetConsoleScreenBufferInfo(void*, CONSOLE_SCREEN_BUFFER_INFO*);
BOOL SetConsoleTextAttribute(void*, WORD);
int printf ( const char * format, ... );
]]

local colorbuf = ffi.new("CONSOLE_SCREEN_BUFFER_INFO")

Utils.textColors = {
	blue = 1,
	green = 2,
	red = 4,
	intensity = 8,
	bg_blue = 16,
	bg_green = 32,
	bg_red = 64,
	bg_intensity = 128,
}

function Utils.writeColored(str, c)
	local h = ffi.C.GetStdHandle( 0xfffffff5)
	ffi.C.GetConsoleScreenBufferInfo(h, colorbuf)
	ffi.C.SetConsoleTextAttribute(h, c)
	ffi.C.printf(str)
	ffi.C.SetConsoleTextAttribute(h, colorbuf.wAttributes)
end

return Utils
