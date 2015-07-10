require "shared.helpers"

local conf_read = false

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

function set_option(property, value)
    mp.set_property("options/"..property, value)
end

mp.add_hook("on_load", 50, function ()
    if not conf_read then
        local path = mp.get_property("stream-open-filename")
        path = utils.join_path(utils.getcwd(), path)
        path = utils.split_path(path)
        path = utils.join_path(path, "mpv.conf")
        for line in readAll(path):gmatch("[^\r\n]+") do
            local line = line:trim()
            if not line:starts("#") then
                line = line:split("=", 1)
                if line[1] and line[2] and allowed_properties[line[1]] then
                    set_option(line[1], line[2])
                    msg.info(line[1], "set to", line[2])
                else
                    msg.info("property not allowed:", line[1])
                end
            end
        end
        conf_read = true
    end
end)
