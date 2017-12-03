#!/usr/bin/env python3
import socket
import configparser
import win32api
import win32process
import win32con
from subprocess import Popen, PIPE

class Linco(object):

    def __init__(self, depth='16', chan='2', rate='48000', dev='Line 1 (Virtual Audio Cable)'):
        self.process = Popen([
            'linco',
            '-B', depth,
            '-C', chan,
            '-R', rate,
            '-dev', dev
        ], stdout=PIPE)

        self._set_priority_high()

    def _set_priority_high(self):
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, self.process.pid)
        win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
    
    def read_audio(self):
        return self.process.stdout.read(8192)


def read_credentials():
    config = configparser.ConfigParser()
    config.read('conf.ini')
    credentials = config['Vfio']['Credentials']
    if credentials.startswith('"') and credentials.endswith('"'):
        credentials = credentials[1:-1]

    return credentials

def main():
    credentials = read_credentials()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 9889))
    s.sendall(credentials.encode('utf-8'))

    linco = Linco()
    data = linco.read_audio()
    while data:
        s.sendall(data)
        data = linco.read_audio()

if __name__ == '__main__':
    main()
