require "shared.helpers"

local check_title_timer = nil
local old_title = nil
local osd_text = ""

function show_osd_text()
    local cmd = {}
    cmd[#cmd+1] = "show-text"
    cmd[#cmd+1] = "\"${osd-ass-cc/0}{\\\\fs30}"..osd_text.."\""
    mp.command(table.concat(cmd, " "))
end

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

function update_osd_text(metadata)
    if metadata and metadata["icy-title"] then
        local title = metadata["icy-title"]
        local djname = get_dj()
        if djname then
            msg.info("dj: "..djname)
            osd_text = "R/a/dio ("..djname..")\n"..title
        end
    end
end

function check_title()
    local metadata = mp.get_property_native("metadata")
    local title = nil
    if metadata then
        title = metadata["icy-title"]
    end
    if title then
        if title ~= old_title then
            update_osd_text(metadata)
            old_title = title
        end
    else
        osd_text = ""
    end
    show_osd_text()
end

mp.register_event("file-loaded", function()
    if check_title_timer then
        check_title_timer:stop()
        check_title_timer = nil
        old_title = nil
    end
    if mp.get_property("stream-open-filename"):find("r-a-d.io") then
        -- for some reason metadata-update doesn't fire when icy-title changes
        check_title_timer = mp.add_periodic_timer(1, check_title)
    end
end)
