require "shared.helpers"

local timer = nil

function check_buffer()
    local buffer_length = mp.get_property_native("demuxer-cache-duration")
    if buffer_length and buffer_length > 9 then
        mp.command("seek 5")
    end
end

mp.register_event("file-loaded", function ()
    local metadata = utils.parse_json(mp.get_property("metadata"))
    if metadata then
        for k, _ in pairs(metadata) do
            if k:lower():find("icy-") then
                timer = mp.add_periodic_timer(1, check_buffer)
                break
            end
        end
    elseif timer then
        timer:stop()
        timer = nil
    end
end)
