-- set mpv title to what it says in #EXTINF

require "shared.helpers"

function set_title()
    local pos = mp.get_property("playlist-pos")
    local title = mp.get_property("playlist/"..pos.."/title")
    if title then
        mp.set_property("file-local-options/force-media-title", title)
        msg.info("Title set to "..title)
    end
end

mp.register_event("start-file", set_title)
