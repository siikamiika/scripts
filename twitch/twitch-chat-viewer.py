#!/usr/bin/env python3
import websocket
import time
import re
from sys import argv

class ChatMessage(object):

    msg_pattern = re.compile(r'PRIVMSG #.*? :(.*?)$')
    username_pattern = re.compile(r'user-type= ?:(.*?)!')

    def __init__(self, text):
        self.text = text
        self.username = None
        self.color = None
        self.message = None
        self._parse()

    def _parse(self):
        for data in self.text.split(';'):
            if data.startswith('color='): # TODO actually use the colors
                self.color = data[len('color='):]
            elif data.startswith('display-name='):
                self.username = data[len('display-name='):]
            elif data.startswith('user-type='):
                if not self.username:
                    self.username = self.username_pattern.search(data).group(1)
                self.message = self.msg_pattern.search(data).group(1)

    def __str__(self):
        if not self.username:
            return self.text.strip()
        return '{}: {}'.format(self.username, self.message)


class ChatConnection(object):

    def __init__(self, channel, nick=None):
        self.channel = channel
        self.nick = nick
        self.web_socket = None

    def _connect(self):
        self.web_socket = websocket.WebSocketApp(
            'wss://irc-ws.chat.twitch.tv/',
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
            )
        self.web_socket.on_open = self.on_open
        self.web_socket.run_forever()

    def on_message(self, ws, message):
        message = ChatMessage(message)
        print(message)

    def on_error(self, ws, error):
        pass

    def on_close(self, ws):
        pass

    def on_open(self, ws):
        ws.send('CAP REQ :twitch.tv/tags twitch.tv/commands\n')
        ws.send('PASS blah\n')
        nick = self.nick or 'justinfan' + str(int(time.time()))
        ws.send('NICK {}\n'.format(nick))
        ws.send('JOIN #{}\n'.format(self.channel))


def main():
    channel = argv[1].lstrip('#')
    chat_connection = ChatConnection(channel)
    chat_connection._connect()



if __name__ == '__main__':
    main()
