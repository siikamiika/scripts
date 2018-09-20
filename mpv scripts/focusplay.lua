local paused = false

function play()
    if paused then
        mp.set_property_native('pause', false)
        paused = false
    end
end

function pause()
    mp.set_property_native('pause', true)
    paused = true
end

local mouse_enabled = false

function do_enable_keybindings()
    if not mouse_enabled then
        mp.enable_key_bindings("showhide", "allow-vo-dragging+allow-hide-cursor")
        mouse_enabled = true
    end
end

mp.set_key_bindings({
    {"mouse_move", play},
    {"mouse_leave", pause},
}, "showhide")
do_enable_keybindings()
