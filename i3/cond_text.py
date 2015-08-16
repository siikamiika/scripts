from i3pystatus import IntervalModule
from subprocess import call


class Text(IntervalModule):

    settings = [
        "text",
        "condition",
        "color",
    ]
    required = ("text", "condition")

    color = None

    def run(self):
        if call(self.condition, shell=True) == 0:
            text = self.text
        else:
            text = ""
        self.output = {
            "full_text": text
        }
        if self.color:
            self.output["color"] = self.color
