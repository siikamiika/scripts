from i3pystatus import IntervalModule
from i3pystatus.core.util import internet, require
from urllib.request import urlopen
from urllib.parse import quote
import json
from subprocess import Popen, DEVNULL


class Weather(IntervalModule):

    interval = 3600 # 1h

    settings = (
        "location",
        "format",
        "color",
    )
    required = ("location",)

    color = "#FFFFFF"
    format = "{location}: {current_temp:.1f} °C, {description}"

    @require(internet)
    def run(self):
        data = urlopen("http://api.openweathermap.org/data/2.5/weather?q="
            "{loc}&units=metric".format(loc=self.location)).read()
        weather = json.loads(data.decode())
        current_temp = weather["main"]["temp"]
        description = weather["weather"][0]["description"]
        self.output = {
            "full_text": self.format.format(
                current_temp=current_temp,
                description=description,
                location=self.location,
                ),
            "color": self.color
        }

    def on_leftclick(self):
        lucky_weather = ("http://www.google.com/search?btnI=1&"
            "q={location}+weather").format(location=quote(self.location))
        Popen(["xdg-open", lucky_weather], stdout=DEVNULL, stderr=DEVNULL)
