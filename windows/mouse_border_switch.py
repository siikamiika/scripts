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

def switch(auth):
    sock = socket.socket()
    sock.connect(('es.lan', 9898))
    sock.send(auth + b'\n')
    sock.send(b'linux\n')

def main():
    auth = read_credentials().encode('utf-8')
    should_switch = True
    while True:
        mouse_x, mouse_y = get_mouse_pos()
        if mouse_x >= 1919:
            if should_switch:
                switch(auth)
            should_switch = False
        else:
            should_switch = True
        time.sleep(0.05)

if __name__ == '__main__':
    main()
