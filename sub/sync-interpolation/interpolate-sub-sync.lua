function shift_subs(offset)
    local r = mp.command_native({
        name = "subprocess",
        playback_only = false,
        capture_stdout = true,
        args = {
            "interpolate-sub-sync",
            mp.get_property_native("filename"),
            tostring(mp.get_property_native("time-pos")),
            tostring(offset),
        },
    })

    if r.status == 0 then
        print("result: " .. r.stdout)
    end

    mp.commandv("sub-reload")
end

function shift_back() shift_subs(-1) end
function shift_forward() shift_subs(1) end

mp.add_key_binding("Alt+z", mp.get_script_name() .. "_shift_back", shift_back)
mp.add_key_binding("Alt+x", mp.get_script_name() .. "_shift_forward", shift_forward)
