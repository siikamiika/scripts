from i3pystatus import Status
from colored_mpd import MPD
from openweather import Weather
from pavutoggle import PulseAudio
from gpu_temp import NvGpuTemp
from colored_load import Load
from colored_cpu import CpuUsage

status = Status(standalone=True)

status.register(PulseAudio,
    format="♪{volume}",
    #color="#FFFFFF",
    )

status.register("clock",
    format="%a %-d %b %Y %X Week %V",
    )

status.register(Weather,
    location="Turku,fi",
    #color="#FFFFFF",
    #format="{location}: {current_temp} °C, {description}",
    )

status.register("temp",
    format="{temp:.0f}°",
    high_factor=0.5,
    color="#05A600",
    color_critical="#A60700",
    )

status.register(CpuUsage,
    format="{usage:02}%",
    color="#0860A7",
    )

status.register(Load,
    format="{avg1} {avg5} {avg15}",
    color="#0860A7",
    )

status.register("text",
    text="i5 3550:",
    color="#0860A7",
    )

status.register(NvGpuTemp,
    #format="{gpu_tmp}°",
    color="#05A600",
    )

status.register("text",
    text="GTX 760:",
    color="#619701",
    )

status.register(MPD,
    format="[{artist} - ]{title} {status}",
    status={
        "pause": "▷",
        "play": "▶",
        "stop": "◾",
    },
    color="#285577",
    )

status.run()
