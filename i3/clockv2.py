from datetime import datetime

from i3pystatus import IntervalModule

class Clock(IntervalModule):

    settings = (
        "format",
        "color",
        "interval",
    )
    format = "%a %d %b %Y %X, Week %V"
    interval = 1
    color = "#FFFFFF"

    def run(self):
        self.output = {
            "full_text": datetime.now().strftime(self.format),
            "color": self.color,
        }

