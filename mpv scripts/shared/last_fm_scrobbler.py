import pylast
from os.path import expanduser, join
from traceback import print_exc
import sys
import pickle
import time
import json

LASTFM_DIR = join(expanduser('~'), 'lastfm')

try:
    with open(join(LASTFM_DIR, 'apikey.secret'), 'r') as apikey:
        API_KEY, API_SECRET = apikey.read().splitlines()[:2]
    with open(join(LASTFM_DIR, 'login.secret'), 'r') as login:
        USERNAME, PASSWORD_HASH = login.read().splitlines()[:2]
except Exception as e:
    print_exc()
    sys.exit()

def debug_msg(text):
    print(json.dumps(text))

def auth():
    return pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=USERNAME,
        password_hash=PASSWORD_HASH
    )

def scrobble(scrobbler, artist, title, album=None, duration=None, timestamp=None):
    result = "scrobbled: {} - {}".format(artist, title)
    track_args = dict(
            artist=artist,
            title=title,
            album=album or None,
            duration=duration or None,
            timestamp=timestamp or int(time.time())
        )
    try:
        scrobbler.scrobble(**track_args)
        debug_msg(result)
    except Exception as e:
        debug_msg('{}, attempting reauth...'.format(e))
        scrobbler = auth()
        scrobbler.scrobble(**track_args)
        debug_msg(result)
    return scrobbler

def publish_nowplaying(scrobbler, artist, title):
    scrobbler.update_now_playing(artist, title)

def main():
    try:
        scrobbler = pickle.load(open(join(LASTFM_DIR, 'scrobbler.pickle'), 'rb'))
    except Exception as e:
        print_exc()
        scrobbler = auth()

    args = sys.argv[1:]
    if args[0] == 'scrobble':
        scrobbler = scrobble(scrobbler, *[json.loads(a) for a in (args[1:] + ['null']*4)[:4]])
    elif args[0] == 'np':
        publish_nowplaying(scrobbler, *[json.loads(a) for a in args[1:3]])

    pickle.dump(scrobbler, open(join(LASTFM_DIR, 'scrobbler.pickle'), 'wb'))


if __name__ == '__main__':
    main()
