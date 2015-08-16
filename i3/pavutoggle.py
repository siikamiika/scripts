from i3pystatus.pulseaudio import *
from subprocess import Popen, DEVNULL, getoutput
from os import kill
from signal import SIGTERM

class PulseAudio(PulseAudio):
    settings = PulseAudio.settings + ["color"]
    color = "#FFFFFF"

    def sink_info_cb(self, context, sink_info_p, _, __):
        super().sink_info_cb(context, sink_info_p, _, __)
        self.output["color"] = self.color

    def on_leftclick(self):
        pids = getoutput("pgrep pavucontrol").splitlines()
        if pids:
            for pid in pids:
                kill(int(pid), SIGTERM)

        else:
            Popen(['pavucontrol'], stdout=DEVNULL, stderr=DEVNULL)
