---------------------------------------------
-- (for mpv media player)                  --
-- attempt ignore english subtitle tracks  --
-- that are intended to be used with the   --
-- english audio track on dual audio anime --
---------------------------------------------

-- local sub_languages = mp.get_property_native("options/slang")
local tracklist = mp.get_property_native("track-list")
for idx, track in pairs(tracklist) do
    if track["type"] == "sub" then
        if (track["lang"] == "eng" or track["lang"] == "en") then
            local track_title = track["title"]:lower()
            if not string.match(track_title, "sign") then
                good_track = track["id"]
                break
            end
        end
    end
end

if good_track then
    mp.set_property("sid", good_track)
end
