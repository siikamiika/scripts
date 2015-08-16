from i3pystatus import IntervalModule

class CpuTemp(IntervalModule):
    settings = [
        "format",
        "color",
        "alert_temp",
        "medium_temp",
        "alert_color",
        "medium_color",
    ]
    format = "{temp}"
    color = "#FFFFFF"
    file = "/sys/class/thermal/thermal_zone0/temp"
    alert_temp = 80
    medium_temp = 50
    medium_color = "#FFFF00"
    alert_color="#FF0000"

    def run(self):
        with open(self.file, "r") as f:
            temp = float(f.read().strip()) / 1000

        if temp < self.medium_temp:
            color = self.color
        elif temp < self.alert_temp:
            color = self.medium_color
        else:
            color = self.alert_color

        self.output = {
            "full_text": self.format.format(temp=temp),
            "color": color,
        }

