utils = require "mp.utils"
msg = require "mp.msg"

function string.starts(String,Start)
   return string.sub(String,1,string.len(Start))==Start
end

function string.ends(String,End)
   return End=='' or string.sub(String,-string.len(End))==End
end

function string.split(str, delim, maxNb)
    if str:find(delim) == nil then
        return {str}
    end
    if maxNb == nil or maxNb < 1 then
        maxNb = 0
    end
    local result = {}
    local pat = "(.-)" .. delim .. "()"
    local nb = 0
    local lastPos = 1
    for part, pos in str:gmatch(pat) do
        nb = nb + 1
        result[nb] = part
        lastPos = pos
        if nb == maxNb then break end
    end
    result[nb + 1] = str:sub(lastPos)
    return result
end

function string.trim(s)
    return s:match'^%s*(.*%S)' or ''
end

function script_path()
   local str = debug.getinfo(2, "S").source:sub(2)
   return str
end

function extract_broken_json(str, keys)
    local path = script_path()
    path = utils.split_path(path)
    path = utils.join_path(path, "get_json.py")
    local args = {"python", path, str, keys}
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
