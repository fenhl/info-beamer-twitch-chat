node.alias("twitch-chat")

gl.setup(NATIVE_WIDTH, NATIVE_HEIGHT)

local json = require "json"
local text = require "text"

util.resource_loader{
    "dejavu_sans.ttf"
}

local write = text{font=dejavu_sans, width=WIDTH, height=HEIGHT, r=1, g=1, b=1}

local data = nil

function concat(arrays)
    local result = {}
    for i = 1, #arrays do
        for j = 1, #arrays[i] do
            result[#result + 1] = arrays[i][j]
        end
    end
    return result
end

util.file_watch("data.json", function(content)
    data = json.decode(content)
end)

function node.render()
    gl.clear(0, 0, 0, 1)
    local text_size = 64
    local text = {}
    for i = 1, #data do
        local formatted_username
        if data[i].userColor == nil then
            formatted_username = data[i].user
        else
            formatted_username = {word=data[i].user, color=data[i].userColor}
        end
        local msg_prefix
        if data[i].isAction then
            msg_prefix = {}
        else
            msg_prefix = {{word=":", space_before=false}}
        end
        text[#text + 1] = concat{{data[i].timestamp, formatted_username}, msg_prefix, data[i].message}
    end
    write{text=text, size=text_size, max_y=max_y, halign="left", valign="bottom"}
end
