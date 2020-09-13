function run_interpolate_sub_sync(args)
    local args2 = {"interpolate-sub-sync"}
    for i = 1, #args do
        table.insert(args2, args[i])
    end

    return mp.command_native({
        name = "subprocess",
        playback_only = false,
        args = args2,
    })
end

function shift_subs(offset)
    run_interpolate_sub_sync({
        mp.get_property_native("filename"),
        tostring(mp.get_property_native("time-pos")),
        tostring(offset),
    })

    mp.commandv("sub-reload")
end

function reload()
    run_interpolate_sub_sync({
        mp.get_property_native("filename"),
        "reload",
    })

    mp.commandv("sub-reload")
end

function shift_back() shift_subs(-1) end
function shift_forward() shift_subs(1) end
function shift_current() shift_subs(0) end

mp.add_key_binding("Alt+z", mp.get_script_name() .. "_shift_back", shift_back)
mp.add_key_binding("Alt+x", mp.get_script_name() .. "_shift_forward", shift_forward)
mp.add_key_binding("Alt+c", mp.get_script_name() .. "_shift_current", shift_current)
mp.add_key_binding("Alt+r", mp.get_script_name() .. "_reload", reload)
