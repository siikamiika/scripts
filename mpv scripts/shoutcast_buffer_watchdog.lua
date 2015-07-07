local timer = nil

function check_buffer()
    local buffer_length = mp.get_property_native("demuxer-cache-duration")
    if buffer_length and buffer_length > 9 then
        mp.command("seek 5")
    end
end

mp.register_event("file-loaded", function ()
    local metadata = mp.get_property("metadata")
    if metadata and metadata:lower():find("shoutcast") then
        timer = mp.add_periodic_timer(1, check_buffer)
    elseif timer then
        timer:stop()
        timer = nil
    end
end)
