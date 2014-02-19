from i3pystatus import IntervalModule
from subprocess import getoutput

class NvGpuTemp(IntervalModule):

    interval = 5

    settings = (
        "format",
        "color",
        "color_high",
        "limit_high",
        "color_crit",
        "limit_crit",
    )

    format = "{gpu_tmp}°"
    color = "#FFFFFF"
    color_high = "#FFFF00"
    color_crit = "#FF0000"
    limit_high = 50
    limit_crit = 75

    def run(self):
        raw = getoutput("nvidia-settings -q gpucoretemp -t")
        try:
            tmp = int(raw.splitlines()[0])
        except Exception as e:
            print(e)
            self.output = {"full_text": "error"}
            return
        color = self.color
        if tmp >= self.limit_crit:
            color = self.color_crit
        elif tmp >= self.limit_high:
            color = self.color_high

        self.output = {
            "full_text": self.format.format(gpu_tmp=tmp),
            "color": color,
        }
