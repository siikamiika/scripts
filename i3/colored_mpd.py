from i3pystatus.mpd import *
from subprocess import getoutput, Popen
from os import kill
from signal import SIGTERM

class MPD(MPD):
    settings = MPD.settings + ("color",)
    color = "#FFFFFF"
    def run(self):
        super().run()
        self.output["color"] = self.color

    on_rightclick = MPD.on_leftclick

    def on_leftclick(self):
        pids = getoutput("pgrep ncmpcpp").splitlines()
        if pids:
            for pid in pids:
                kill(int(pid), SIGTERM)

        else:
            Popen(['urxvt', '-e', 'ncmpcpp'])
