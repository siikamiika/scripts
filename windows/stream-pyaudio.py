#!/usr/bin/env python3
import socket
import configparser
import pyaudio
import atexit
import win32api
import win32process
import win32con

CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
INPUT_DEVICE = 'Line 1 (Virtual Audio Cable)'

class Audio(object):

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.device_info = self.pyaudio.get_host_api_info_by_index(0)
        self.audio_stream = None

    def _get_device_index(self):
        for i in range(self.device_info.get('deviceCount')):
            device = self.pyaudio.get_device_info_by_host_api_device_index(0, i)
            if device.get('maxInputChannels') > 0 and device.get('name') == INPUT_DEVICE:
                return i
        raise Exception('Input device {} not found'.format(INPUT_DEVICE))

    def start_audio_stream(self):
        self.audio_stream = self.pyaudio.open(
            input_device_index=self._get_device_index(),
            format=FORMAT, 
            channels=CHANNELS,
            rate=RATE,
            input=True, 
            frames_per_buffer=CHUNK_SIZE,
        )

    def read_audio(self):
        return self.audio_stream.read(CHUNK_SIZE)

    def close(self):
        self.audio_stream.close()
        self.pyaudio.terminate()


def read_credentials():
    config = configparser.ConfigParser()
    config.read('conf.ini')
    credentials = config['Vfio']['Credentials']
    if credentials.startswith('"') and credentials.endswith('"'):
        credentials = credentials[1:-1]

    return credentials

def main():
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)

    credentials = read_credentials()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 9889))
    s.sendall(credentials.encode('utf-8'))

    audio = Audio()

    atexit.register(audio.close)

    audio.start_audio_stream()
    data = audio.read_audio()
    while data:
        s.sendall(data)
        data = audio.read_audio()

if __name__ == '__main__':
    main()
