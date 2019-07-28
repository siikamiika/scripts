#!/bin/bash
TITLES=$(xdotool search --class spotify)

while IFS= read -r window_id; do
    mute=0
    title=$(xdotool getwindowname $window_id)
    window_pid=$(xdotool getwindowpid $window_id)
    sinks=$(
        pacmd list-sink-inputs |
        grep "application.process.id = \"$window_pid\"" -B 22 |
        grep 'index: ' |
        awk '{print $2}'
    )
    # ignore trap title
    if [[ "$title" == "spotify" ]]; then
        continue
    elif [[ "$title" == *"Advertisement"* ]]; then
        mute=1
    fi
    # TODO fix copypaste
    muted_inputs=$(
        pacmd list-sink-inputs |
        grep "application.process.id = \"$window_pid\"" -B 22 |
        grep 'muted: ' |
        awk '{print $2}'
    )
    everything_ok=1
    while IFS= read -r is_muted; do
        if [[ $mute -eq 1 ]] && [[ "$is_muted" == "no" ]]; then
            everything_ok=0
        elif [[ $mute -eq 0 ]] && [[ "$is_muted" == "yes" ]]; then
            everything_ok=0
        fi
    done <<< "$muted_inputs"
    # everything ok, exit
    if [[ $everything_ok -eq 1 ]]; then
        exit 0
    fi
    while IFS= read -r sink_id; do
        pacmd set-sink-input-mute "$sink_id" $mute
    done <<< "$sinks"
done <<< "$TITLES"
