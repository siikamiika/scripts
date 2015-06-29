local utils = require 'mp.utils'

HOST = "http://localhost:8888"

function string.starts(String,Start)
   return string.sub(String,1,string.len(Start))==Start
end

function string.ends(String,End)
   return End=='' or string.sub(String,-string.len(End))==End
end

mp.add_hook("on_load", 50, function ()
    local fn = mp.get_property("stream-open-filename")
    local torrent = nil
    if string.ends(fn, ".torrent") then
        torrent = utils.join_path(utils.getcwd(), fn)
    elseif string.starts(fn, "magnet:") then
        torrent = fn
    end
    if torrent then
        mp.set_property("stream-open-filename", HOST.."/stream_torrent/"..torrent)
    end
end)
