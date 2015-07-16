-- original: TOOLS/lua/autoload.lua
-- this version is disabled by default and supports toggling
-- stored_path is needed for playlist files that have a stream url in them

require "shared.helpers"

MAXENTRIES = 5

EXTENSIONS = Set {
    'mkv', 'avi', 'mp4', 'ogv', 'webm', 'rmvb', 'flv', 'wmv', 'mpeg', 'mpg', 'm4v', '3gp',
    'mp3', 'wav', 'flac', 'm4a', 'wma', 'm3u',
}

local enabled  = false

local stored_path

function add_files_at(index, files)
    index = index - 1
    local oldcount = mp.get_property_number("playlist-count", 1)
    for i = 1, #files do
        mp.commandv("loadfile", files[i], "append")
        mp.commandv("playlist_move", oldcount + i - 1, index + i - 1)
    end
end

function get_extension(path)
    return string.match(path, "%.([^%.]+)$" )
end

table.filter = function(t, iter)
    for i = #t, 1, -1 do
        if not iter(t[i]) then
            table.remove(t, i)
        end
    end
end

function find_and_add_entries(firstrun)
    local path
    if firstrun == true then
        path = stored_path
    else
        path = mp.get_property("path", "")
    end
    local dir, filename = utils.split_path(path)
    if #dir == 0 then
        return
    end
    local files = utils.readdir(dir, "files")
    if files == nil then
        return
    end
    table.filter(files, function (v, k)
        local ext = get_extension(v)
        if ext == nil then
            return false
        end
        return EXTENSIONS[string.lower(ext)]
    end)
    table.sort(files, function (a, b)
        return string.lower(a) < string.lower(b)
    end)

    if dir == "." then
        dir = ""
    end

    local pl = mp.get_property_native("playlist", {})
    local pl_current = mp.get_property_number("playlist-pos", 0) + 1
    -- Find the current pl entry (dir+"/"+filename) in the sorted dir list
    local current
    for i = 1, #files do
        if files[i] == filename then
            current = i
            break
        end
    end
    if current == nil then
        return
    end

    local append = {[-1] = {}, [1] = {}}
    for direction = -1, 1, 2 do -- 2 iterations, with direction = -1 and +1
        for i = 1, MAXENTRIES do
            local file = files[current + i * direction]
            local pl_e = pl[pl_current + i * direction]
            if file == nil or file[1] == "." then
                break
            end

            local filepath = dir .. file
            if pl_e then
                -- If there's a playlist entry, and it's the same file, stop.
                if pl_e.filename == filepath then
                    break
                end
            end

            if direction == -1 then
                if pl_current == 1 then -- never add additional entries in the middle
                    msg.info("Prepending " .. file)
                    table.insert(append[-1], 1, filepath)
                end
            else
                msg.info("Adding " .. file)
                table.insert(append[1], filepath)
            end
        end
    end

    add_files_at(pl_current + 1, append[1])
    add_files_at(pl_current, append[-1])
end

function toggle_autoload()
    if enabled then
        mp.unregister_event(find_and_add_entries)
        mp.osd_message("autoload disabled")
    else
        find_and_add_entries(true)
        mp.register_event("start-file", find_and_add_entries)
        mp.osd_message("autoload enabled")
    end
    enabled = not enabled
end

mp.add_hook("on_load", 50, function()
    local _path = mp.get_property("path", "")
    local _dir, _filename = utils.split_path(_path)
    if #_dir == 0 then
        return
    end
    local _files = utils.readdir(_dir, "files")
    if _files == nil then
        return
    end
    stored_path = _path
end)

mp.add_key_binding("F3", "toggle_autoload", toggle_autoload)
