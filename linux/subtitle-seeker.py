#!/usr/bin/env python3
import sys
import subprocess
import json
import requests

YTDL_ARGUMENTS = ["-j", "--skip-download", "--all-subs", "ytsearch999:{query}, cc"]


def download_subtitled(query, wanted_words=None):
    arguments = list(YTDL_ARGUMENTS)
    arguments[3] = arguments[3].format(query=query)

    ytdl = subprocess.Popen(["youtube-dl"] + arguments, stdout=subprocess.PIPE)
    while True:
        line = ytdl.stdout.readline()
        if not line:
            break
        try:
            info = json.loads(line)
            print(info["fulltitle"])
            subs = info["requested_subtitles"]
            download = False
            for lang in subs:
                url = subs[lang]["url"]
                r = requests.get(url)
                if wanted_words:
                    if [w for w in wanted_words.split() if w in r.text]:
                        download = True
                        break
                else:
                    download = True
                    break

            if download:
                subprocess.call(["youtube-dl", "--all-subs", info["display_id"]])
        except:
            print(line)


def main():
    download_subtitled(*sys.argv[1:])


if __name__ == "__main__":
    main()
