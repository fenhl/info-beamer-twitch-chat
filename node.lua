node.alias("twitch-chat")

gl.setup(NATIVE_WIDTH, NATIVE_HEIGHT)

local json = require "json"
local text = require "text"

util.resource_loader{
    "dejavu_sans.ttf"
}

local write = text{font=dejavu_sans, width=WIDTH, height=HEIGHT, r=1, g=1, b=1}

local data = nil

util.file_watch("data.json", function(content)
    data = json.decode(content)
end)

function node.render()
    gl.clear(0, 0, 0, 1)
    write{text=data, size=64, halign="left", valign="bottom"}
end
