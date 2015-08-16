from i3pystatus import IntervalModule
from subprocess import check_output

class GpuInfo(IntervalModule):

    interval = 5

    settings = (
        "format",
        "color",
    )

    format_options = (
        "temperature.gpu",
        "memory.used",
        "memory.total",
        "utilization.gpu",
        "utilization.memory",
    )

    format = ""
    color = "#FFFFFF"

    def run(self):
        try:
            info = dict(
                (
                    f,
                    check_output(
                        "nvidia-smi --query-gpu="+f+
                        " --format=csv,noheader", shell=True).decode().splitlines()[0],
                )
                for f in self.format_options if f in self.format
            )
        except Exception as e:
            self.output = {"full_text": ""}
            return
        self.output = {
            "full_text": self.format.format(info),
            "color": self.color,
        }
