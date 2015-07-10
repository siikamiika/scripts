require "shared.helpers"

local timer = nil
local old_title = nil
local is_r_a_dio = false
local osd_title, dj, listeners, songlen, songpos, playertime = nil
local osd_text = ""

function show_osd_text()
    local cmd = {}
    cmd[#cmd+1] = "show-text"
    cmd[#cmd+1] = "\"${osd-ass-cc/0}{\\\\fs30}"..osd_text.."\""
    mp.command(table.concat(cmd, " "))
end

function get_r_a_dio_info()
    local data = readAllHTTP("https://r-a-d.io/api")
    -- something fails when parsing the whole json...
    local ebj = extract_broken_json
    local starttime = ebj(data, "main,start_time")
    local endtime = ebj(data, "main,end_time")
    local curtime = ebj(data, "main,current")
    return ebj(data, "main,np"), ebj(data, "main,dj,djname"), ebj(data, "main,listeners"), endtime-starttime, curtime-starttime
end

function update_osd_text()
    if is_r_a_dio then
        local songpos_ = math.floor(songpos + mp.get_time() - playertime)
        local songpos_text = ("%02d:%02d"):format(math.floor(songpos_ / 60), songpos_ % 60)
        local songlen_text = ("%02d:%02d"):format(math.floor(songlen / 60), songlen % 60)
        osd_text = "R/a/dio ("..dj..")\n"..
            osd_title.."\n"..
            ("%s/%s"):format(songpos_text, songlen_text).."\n"..
            ("%s listeners"):format(listeners)
    else
        osd_text = osd_title
    end
end

function periodic()
    local buffer_length = mp.get_property_native("demuxer-cache-duration")
    if buffer_length and buffer_length > 9 then
        mp.command("seek 5")
    end
    local metadata = mp.get_property_native("metadata")
    local title = nil
    if metadata then
        title = metadata["icy-title"]
    end
    if title then
        if title ~= old_title then
            if is_r_a_dio then
                osd_title, dj, listeners, songlen, songpos = get_r_a_dio_info()
                playertime = mp.get_time()
                msg.info("R/a/dio dj: "..dj)
            else
                osd_title = title
            end
            old_title = title
        end
    else
        osd_text = ""
    end
    update_osd_text()
    show_osd_text()
end

mp.register_event("file-loaded", function()
    if timer then
        timer:stop()
        timer = nil
        old_title = nil
        is_r_a_dio = false
    end
    if mp.get_property("stream-open-filename"):find("r-a-d.io") then
        is_r_a_dio = true
    end
    local metadata = mp.get_property_native("metadata")
    for k, _ in pairs(metadata or {}) do
        k = tostring(k)
        if k:lower():starts("icy-") then
            msg.info("shoutcast/icecast stream detected ("..k.." in metadata)")
            timer = mp.add_periodic_timer(1, periodic)
            break
        end
    end
end)
