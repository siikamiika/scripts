require "shared.helpers"

local timer = nil
local old_title = nil
local is_r_a_dio = false
local osd_title, dj, osd_text = ""
local listeners, songlen, songpos, r_a_dio_info_fetch_time = 0

function ass(str)
    local ass = mp.get_property_osd("osd-ass-cc/0")
    local no_ass = mp.get_property_osd("osd-ass-cc/1")
    return ass..str..no_ass
end

function get_r_a_dio_info()
    local data = readAllHTTP("https://r-a-d.io/api")
    -- something fails when parsing the whole json...
    local ebj = extract_broken_json
    local starttime = ebj(data, "main,start_time")
    local endtime = ebj(data, "main,end_time")
    local curtime = ebj(data, "main,current")
    osd_title = ebj(data, "main,np")
    dj = ebj(data, "main,dj,djname")
    listeners = ebj(data, "main,listeners")
    songlen = endtime-starttime
    songpos = curtime-starttime
    r_a_dio_info_fetch_time = mp.get_time()
end

function update_osd_text()
    if is_r_a_dio then
        local songpos_ = math.floor(songpos + mp.get_time() - r_a_dio_info_fetch_time)
        local songpos_text = ("%02d:%02d"):format(math.floor(songpos_ / 60), songpos_ % 60)
        local songlen_text = ("%02d:%02d"):format(math.floor(songlen / 60), songlen % 60)
        osd_text = "R/a/dio ("..dj..")\n"..
            osd_title.."\n"..
            ("%s/%s"):format(songpos_text, songlen_text).."\n"..
            ("%s listeners"):format(listeners)
    else
        osd_text = osd_title
    end
    mp.osd_message(ass([[{\\fs30}]])..osd_text)
end

function check_buffer(_, buffer_length)
    if buffer_length and buffer_length > 9 then
        mp.set_property("speed", 100)
        mp.add_timeout(0.1, function()
            mp.set_property("speed", 1)
        end)
    end
end

function on_metadata_update(_, metadata)
    local title = nil
    if metadata then
        title = metadata["icy-title"]
    end
    if title then
        if is_r_a_dio then
            get_r_a_dio_info()
        else
            osd_title = title
        end
    else
        osd_title = ""
    end
end

mp.register_event("file-loaded", function()
    mp.unobserve_property(check_buffer)
    mp.unobserve_property(on_metadata_update)
    if timer then
        timer:kill()
        timer = nil
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
            mp.observe_property("demuxer-cache-duration", "number", check_buffer)
            mp.observe_property("metadata", "native", on_metadata_update)
            timer = mp.add_periodic_timer(1, update_osd_text)
            break
        end
    end
end)
