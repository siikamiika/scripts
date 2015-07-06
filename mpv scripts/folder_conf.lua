require "shared.helpers"

local conf_read = false
local conf = {}

local allowed_properties = Set{
    "vid",
    "aid",
    "sid",
    "secondary-sid",
    "alang",
    "slang",
    "audio-delay",
    "sub-delay",
    "video-aspect"
}

function set_property_flo(property, value)
    mp.set_property("file-local-options/"..property, value)
end

function set_properties()
    for p, v in pairs(conf) do
        set_property_flo(p, v)
    end
end

mp.add_hook("on_load", 50, function ()
    if not conf_read then
        local path = mp.get_property("stream-open-filename")
        path = utils.join_path(utils.getcwd(), path)
        path = utils.split_path(path)
        for line in readAll(utils.join_path(path, "mpv.conf")):gmatch("[^\r\n]+") do
            local line = trim(line)
            if not string.starts(line, "#") then
                line = string.split(line, "=", 1)
                if line[1] and line[2] and allowed_properties[line[1]] then
                    conf[line[1]] = line[2]
                else
                    msg.info("property not allowed: "..line[1])
                end
            end
        end
        set_properties()
        conf_read = true
    else
        set_properties()
    end
end)
