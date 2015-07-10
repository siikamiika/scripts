require "shared.helpers"

local timer = nil
local old_title = nil

function get_dj()
    local data = readAllHTTP("https://r-a-d.io/api")
    local dj_name = nil
    -- something fails when parsing the whole json...
    for djname in data:gmatch("[^%\\](\"djname\":\".-[^%\\]\")") do
        dj_name = djname
    end
    if dj_name then
        dj_name = utils.parse_json("{"..dj_name.."}")
        return dj_name["djname"]
    else
        return nil
    end
end

function display_dj(metadata)
    if metadata and metadata["icy-title"] then
        local title = metadata["icy-title"]
        local djname = get_dj()
        if djname then
            msg.info(djname)
            mp.set_property("file-local-options/force-media-title", "R/a/dio ["..djname.."]: "..title)
        end
    end
end

mp.register_event("file-loaded", function()
    if timer then
        timer:stop()
        timer = nil
        old_title = nil
    end
    if mp.get_property("stream-open-filename"):find("r-a-d.io") then
        -- for some reason metadata-update doesn't fire when icy-title changes
        timer = mp.add_periodic_timer(1, function()
            local metadata = mp.get_property_native("metadata")
            local title = nil
            if metadata then
                title = metadata["icy-title"]
            end
            if title and title ~= old_title then
                display_dj(metadata)
                old_title = title
            end
        end)
    end
end)
