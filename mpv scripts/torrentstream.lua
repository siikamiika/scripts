require "shared.helpers"

HOST = "http://localhost:8888"

mp.add_hook("on_load", 50, function ()
    local fn = mp.get_property("stream-open-filename")
    local magnet_idx = string.find(fn, "magnet:")
    local torrent = nil
    if string.ends(fn, ".torrent") then
        torrent = utils.join_path(utils.getcwd(), fn)
    elseif magnet_idx then
        torrent = string.sub(fn, magnet_idx)
    end
    if torrent then
        mp.set_property("stream-open-filename", HOST.."/stream_torrent/"..torrent)
    end
end)
