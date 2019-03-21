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
    local max_y = HEIGHT - text_size / 2
    for i = #data, 1, -1 do
        local timestamp_dims = write{text={{data[i].timestamp}}, size=text_size, max_y=max_y, halign="left", valign="bottom"}
        local username_dims
        if data[i].userColor == nil then
            username_dims = write{text={{data[i].user}}, size=text_size, max_y=max_y, indent=timestamp_dims.final_indent_space, halign="left", valign="bottom"}
        else
            username_dims = write{text={{data[i].user}}, size=text_size, max_y=max_y, indent=timestamp_dims.final_indent_space, halign="left", valign="bottom", color=data[i].userColor}
        end
        local msg_dims = write{text={concat{{":"}, data[i].message}}, size=text_size, max_y=max_y, indent=username_dims.final_indent, halign="left", valign="bottom"}
        max_y = max_y - msg_dims.height - text_size / 2
    end
end
