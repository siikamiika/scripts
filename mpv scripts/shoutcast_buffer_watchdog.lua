require "shared.helpers"

local timer = nil

function check_buffer()
    local buffer_length = mp.get_property_native("demuxer-cache-duration")
    if buffer_length and buffer_length > 9 then
        mp.command("seek 5")
    end
end

mp.register_event("file-loaded", function ()
    if timer then
        timer:stop()
        timer = nil
    end
    local metadata = utils.parse_json(mp.get_property("metadata"))
    for k, _ in pairs(metadata or {}) do
        k = tostring(k)
        if k:lower():starts("icy-") then
            msg.info("shoutcast/icecast stream detected ("..k.." in metadata)")
            timer = mp.add_periodic_timer(1, check_buffer)
            break
        end
    end
end)
