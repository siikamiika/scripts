local utils = require 'mp.utils'

local CLIPBOARD_PATH = '/tmp/mpv_subcopy'

function on_sub_text(_, sub_text)
    if sub_text and sub_text ~= '' then
        local f = io.open(CLIPBOARD_PATH, 'w')
        f:write(sub_text .. '\n')
        f:close()
        local shell_command = string.format('xclip -selection clipboard %s', CLIPBOARD_PATH)
        os.execute(shell_command)
    end
end

mp.observe_property("sub-text", "native", on_sub_text)
