#!/usr/bin/env python3
import socket
import time
import sys
import pylast
from datetime import datetime
from html.parser import HTMLParser
hp = HTMLParser()

try:
    with open('apikey.secret', 'r') as apikey:
        API_KEY, API_SECRET = apikey.read().splitlines()[:2]
    with open('login.secret', 'r') as login:
        USERNAME, PASSWORD = login.read().splitlines()[:2]
except Exception as e:
    print(e)
    sys.exit()

def auth():
    return pylast.LastFMNetwork(
        api_key = API_KEY,
        api_secret = API_SECRET,
        username = USERNAME,
        password_hash = pylast.md5(PASSWORD)
    )

def connect():
    """Return a new connection to MPD or None on error."""
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect(('localhost', 6600))
        print(conn.recv(1024).decode())
        return conn
    except Exception as e:
        print(e)
        return


def track(currentsong):
    """
    Return dictionary containing MPD currentsong output.
    If no Artist is specified, try to find it from Title before ' - '.
    If Artist is not found, return None.
    """
    try:
        song_dict = dict(
                (l[:l.index(':')], l[l.index(' ')+1:])
                for l in currentsong.decode().strip().splitlines()[:-1]
            )

        song_dict['timestamp'] = int(time.time())
        if not song_dict.get('Artist'):
            if ' - ' in str(song_dict.get('Title')):
                song_dict['Artist'], song_dict['Title'] = \
                    song_dict.get('Title').split(' - ', 1)
            else:
                return

        return song_dict

    except Exception as e:
        print(e)
        return

def scrobble(scrobbler, track):
    if not (track['Artist'] and track['Title']):
        return
    track_args = dict(
            artist=hp.unescape(track['Artist']),
            title=hp.unescape(track['Title']),
            album=track.get('Album'),
            album_artist=track.get('AlbumArtist'),
            duration=track.get('Time'),
            track_number=track['Track'].split('/')[0] if track.get('Track')
                         else None,
            timestamp=track['timestamp']
        )
    scrobble_info = '{0} scrobbled: {1} - {2}'.format(
            datetime.now().replace(microsecond=0),
            track['Artist'], track['Title']
        )
    try:
        scrobbler.scrobble(**track_args)
        print(scrobble_info)
    except Exception as e:
        print('{}, attempting reauth...'.format(e))
        scrobbler = auth()
        scrobbler.scrobble(**track_args)
        print(scrobble_info)
        return scrobbler

if __name__ == '__main__':
    # start loop
    conn = connect()
    scrobbler = auth()
    queue = None
    while True:
        submittable = None
        try:
            conn.send(b'currentsong\n')
            response = conn.recv(1024)
            submittable = track(response)
        except Exception as e:
            print(e)
            conn = connect()
            if not conn:
                time.sleep(60)
                continue
            conn.send(b'currentsong\n')
            response = conn.recv(1024)
            submittable = track(response)

        if submittable:
            if not queue:
                queue = dict(submittable)
            queued = queue.get('Id'), queue.get('Artist'), queue.get('Title')
            upcoming = (submittable.get('Id'), submittable.get('Artist'),
                submittable.get('Title'))
            if queued != upcoming:
                reauth = scrobble(scrobbler, queue)
                if reauth:
                    scrobbler = reauth
                queue = dict(submittable)

        time.sleep(10)
