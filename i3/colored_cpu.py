from i3pystatus.cpu_usage import *

class CpuUsage(CpuUsage):
    settings = CpuUsage.settings + ["color"]
    color = "#FFFFFF"

    def run(self):
        super().run()
        self.output["color"] = self.color
