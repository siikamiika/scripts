from i3pystatus.load import *

class Load(Load):
    settings = Load.settings + ["color"]

    color = "#FFFFFF"

    def run(self):
        super().run()
        self.output["color"] = self.color
