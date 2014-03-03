from i3pystatus import IntervalModule
from subprocess import getoutput

class GpuInfo(IntervalModule):

    interval = 5

    settings = (
        "format",
        "color",
    )

    format_options = (
        "gpucoretemp",
        "gpucurrentfanspeed",
        "gpucurrentfanspeedrpm",
        "useddedicatedgpumemory",
        "totaldedicatedgpumemory",
    )

    format = ""
    color = "#FFFFFF"

    def run(self):
        try:
            info = dict(
                (
                    f,
                    int(
                        getoutput("nvidia-settings -t -q {}".format(f))
                        .splitlines()[0]
                    )
                )
                for f in self.format_options if f in self.format
            )
        except Exception as e:
            self.output = {"full_text": e}
            return

        self.output = {
            "full_text": self.format.format(**info),
            "color": self.color,
        }
