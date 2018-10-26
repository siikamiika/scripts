import time
import configparser
import socket
from ctypes import windll, Structure, c_long, byref

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def get_mouse_pos():
    point = POINT()
    windll.user32.GetCursorPos(byref(point))
    return point.x, point.y

def read_credentials():
    config = configparser.ConfigParser()
    config.read('conf.ini')
    credentials = config['Vfio']['Credentials']
    if credentials.startswith('"') and credentials.endswith('"'):
        credentials = credentials[1:-1]

    return credentials

def switch(auth, mouse_y):
    sock = socket.socket()
    sock.connect(('es.lan', 9898))
    sock.send(auth + b'\n')
    sock.send(f'linux {mouse_y}\n'.encode('utf-8'))

def main():
    auth = read_credentials().encode('utf-8')
    # last differing position
    last_pos = (0, 0)
    while True:
        current_pos = get_mouse_pos()
        # switch if we are at the edge and the mouse has moved
        if current_pos != last_pos:
            if current_pos[0] >= 1919:
                switch(auth, current_pos[1])
            last_pos = current_pos
        time.sleep(0.05)

if __name__ == '__main__':
    main()
