from i3pystatus.mpd import *
from subprocess import getoutput, Popen
from os import kill
from signal import SIGTERM
from html.parser import HTMLParser
hp = HTMLParser()

class MPD(MPD):
    settings = MPD.settings + ("color",)
    color = "#FFFFFF"
    def run(self):
        super().run()
        self.output["color"] = self.color
        self.output["full_text"] = hp.unescape(self.output["full_text"])
        # lol
        if self.status["stop"] in self.output["full_text"]:
            self.output["full_text"] = self.status["stop"]

    on_rightclick = MPD.on_leftclick

    def on_leftclick(self):
        pids = getoutput("pgrep qmpdclient").splitlines()
        if pids:
            for pid in pids:
                kill(int(pid), SIGTERM)

        else:
            Popen(['qmpdclient'])

