utils = require "mp.utils"
msg = require "mp.msg"

function string:starts(Start)
   return self:sub(1, Start:len()) == Start
end

function string:ends(End)
   return End == "" or self:sub(-End:len()) == End
end

function string:split(delim, max_splits)
    if max_splits == nil or max_splits < 1 then
        max_splits = 0
    end
    local result = {}
    local pattern = "(.-)"..delim.."()"
    local splits = 0
    local last_pos = 1
    for part, pos in self:gmatch(pattern) do
        splits = splits + 1
        result[splits] = part
        last_pos = pos
        if splits == max_splits then break end
    end
    result[splits + 1] = self:sub(last_pos)
    return result
end

function string:trim()
    return self:match("^%s*(.*%S)") or ""
end

function script_dir()
   local path = debug.getinfo(2, "S").source:sub(2)
   path = utils.split_path(path)
   return path
end

function extract_broken_json(str, keys, url)
    local path = script_dir()
    path = utils.join_path(path, "get_json.py")
    local args = {"python", path}
    if url then
        args[#args + 1] = "url"
    end
    args[#args + 1] = str
    args[#args + 1] = keys
    local ret = utils.subprocess({args = args})
    return utils.parse_json(ret.stdout)
end

function Set(list)
    local set = {}
    for _, l in ipairs(list) do set[l] = true end
    return set
end

function exec(args)
    local ret = utils.subprocess({args = args})
    return ret.status, ret.stdout, ret
end

function readAll(file)
    local f = io.open(file, "rb")
    local content = ""
    if f then
        content = f:read("*all")
        f:close()
    end
    return content
end

function readAllHTTP(url)
    local command = {"curl", "-k", "-s", url}
    local status, content = exec(command)
    return content or ""
end

function ass(str)
    local ass = mp.get_property_osd("osd-ass-cc/0")
    local no_ass = mp.get_property_osd("osd-ass-cc/1")
    return ass..str..no_ass
end

function white_ass()
    return ass([[{\c&Hffffff&}]])
end

function colored(text, bgr, default)
    local return_color = default
    if return_color then
        return_color = ass([[{\c&H]]..return_color..[[&}]])
    else
        return_color = white_ass()
    end
    return ass([[{\c&H]]..bgr..[[&}]])..text..return_color
end
