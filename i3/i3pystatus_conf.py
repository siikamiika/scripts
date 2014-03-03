from i3pystatus import Status
from colored_mpd import MPD
from openweather import Weather
from pavutoggle import PulseAudio
from nvidia_temp import NvGpuTemp
#from nvidia import GpuInfo
from colored_load import Load
from colored_cpu import CpuUsage
from clockv2 import Clock

status = Status(standalone=True)

NVIDIA = "#619701"
INTEL  = "#0860A7"
I3BLUE = "#285577"
TEMP_OK = "#05A600"

status.register(PulseAudio,
    format="♪{volume}",
    color=I3BLUE,
    )

status.register(Clock,
    format="%X",
    #color="#FFFFFF",
    )

status.register(Clock,
    format="%a %-d %b %Y, Week %V",
    interval=10,
    color=I3BLUE,
    )

#status.register(Weather,
#    location="Turku,fi",
#    #color=I3BLUE,
#    #format="{location}: {current_temp} °C, {description}",
#    )

status.register(CpuUsage,
    format="{usage:02}%",
    color=INTEL,
    )

status.register(Load,
    format="{avg1} {avg5} {avg15}",
    color=INTEL,
    )

status.register("temp",
    format="{temp:.0f}°",
    high_factor=0.5,
    color=TEMP_OK,
    )

status.register("text",
    text="i5 3550:",
    color=INTEL,
    )

# status.register(GpuInfo,
#     format="fan: {gpucurrentfanspeed}% "
#            "VRAM: {useddedicatedgpumemory}MiB/{totaldedicatedgpumemory}MiB",
#     color=NVIDIA,
#     )

status.register(NvGpuTemp,
    #format="{gpu_temp}°",
    color=TEMP_OK,
    )

status.register("text",
    text="GTX 760:",
    color=NVIDIA,
    )

status.register(MPD,
    format="[{artist} - ]{title} {status} ♪{volume}",
    status={
        "pause": "▷",
        "play": "▶",
        "stop": "◾",
    },
    color=I3BLUE,
    )

status.run()

