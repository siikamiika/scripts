-- set mpv title to what it says in #EXTINF

function string.starts(String,Start)
   return string.sub(String,1,string.len(Start))==Start
end

function string.ends(String,End)
   return End=='' or string.sub(String,-string.len(End))==End
end

function trim(s)
    return s:match'^%s*(.*%S)' or ''
end

function readAll(file)
    local f = io.open(file, "rb")
    local content = f:read("*all")
    f:close()
    return content
end

function parse_titles(m3u_file)
    local titles = {}
    local file_content = readAll(m3u_file)
    local playlist_counter = 1
    for line in file_content:gmatch("[^\r\n]+") do
        local line = trim(line)
        if string.starts(line, "#EXTINF") then
            local extinf_table = {}
            for extinf in line:gmatch("[^,]+") do
                table.insert(extinf_table, extinf)
            end
            table.remove(extinf_table, 1)
            local title = table.concat(extinf_table, "")
            table.insert(titles, playlist_counter, title)
        elseif not ((line == "") or string.starts(line, "#")) then
            playlist_counter = playlist_counter + 1
        end
    end
    return titles
end

function get_titles()
    local path = mp.get_property("path")
    if string.ends(path, ".m3u") then
        print("Getting titles from "..path)
        titles = parse_titles(path)
    end
end

function set_title()
    local pos = mp.get_property("playlist-pos")
    if titles then
        local title = titles[pos + 1]
        if title then
            print("Setting title to "..title)
            mp.set_property("file-local-options/force-media-title", title)
        end
    end
end

mp.register_event("start-file", get_titles)
mp.register_event("file-loaded", set_title)
