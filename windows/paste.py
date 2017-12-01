#!/usr/bin/env python3
import socket
import configparser
from sys import argv
from io import BytesIO, StringIO
import pyperclip

def unescape_newlines_and_spaces(text):
    result = StringIO()
    text_iter = iter(text)
    for char in text_iter:
        if char != '\\':
            result.write(char)
        else:
            try:
                char = next(text_iter)
            except StopIteration:
                break
            if char == '\\':
                result.write('\\')
            elif char == 'n':
                result.write('\r\n')
            elif char == 's':
                result.write(' ')
            else:
                result.write('\\' + char)

    return result.getvalue()

def read_credentials():
    config = configparser.ConfigParser()
    config.read('conf.ini')
    credentials = config['Vfio']['Credentials']
    if credentials.startswith('"') and credentials.endswith('"'):
        credentials = credentials[1:-1]

    return credentials

def socket_readline(sock):
    result = BytesIO()
    buffer = sock.recv(4096)
    while buffer:
        if b'\n' in buffer:
            line, buffer = buffer.split(b'\n', 1)
            result.write(line)
            break
        else:
            result.write(buffer)
            buffer = sock.recv(4096)

    return result.getvalue()

def main():
    credentials = read_credentials()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 9888))
    s.sendall(credentials.encode('utf-8') + b'\n')
    if argv[1] == 'clipboard':
        s.sendall(b'clipboard_paste\n')
    elif argv[1] == 'primary':
        s.sendall(b'primary_paste\n')

    result = socket_readline(s).decode('utf-8').split(' ')
    s.sendall(b'quit\n')
    if result[0] in ['clipboard_paste', 'primary_paste']:
        text = unescape_newlines_and_spaces(result[1])
        pyperclip.copy(text)

if __name__ == '__main__':
    main()
