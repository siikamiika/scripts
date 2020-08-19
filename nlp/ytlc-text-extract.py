#!/usr/bin/env python3

import sys
import json


class YoutubeLiveChatReplayParser:
    def parse_messages(self, input_buffer):
        for line in input_buffer:
            yield from self._parse_replay_chat_item_action(json.loads(line))

    def _transform_renderer_message(self, data):
        results = []
        for run in data['runs']:
            if 'text' in run:
                results.append(run['text'])
        return results

    def _parse_replay_chat_item_action(self, data):
        if 'replayChatItemAction' not in data:
            return
        data = data['replayChatItemAction']
        if 'videoOffsetTimeMsec' not in data:
            return
        if 'actions' not in data:
            return
        data = data['actions']
        for action in data:
            if 'addChatItemAction' not in action:
                continue
            action = action['addChatItemAction']
            if 'item' not in action:
                continue
            action = action['item']

            body = None

            if 'liveChatTextMessageRenderer' in action:
                renderer = action['liveChatTextMessageRenderer']
                if 'message' in renderer:
                    body = self._transform_renderer_message(renderer['message'])
            elif 'liveChatPaidMessageRenderer' in action:
                renderer = action['liveChatPaidMessageRenderer']
                if 'message' in renderer:
                    body = self._transform_renderer_message(renderer['message'])

            if body is not None:
                yield from body


def main():
    parser = YoutubeLiveChatReplayParser()

    for text in parser.parse_messages(sys.stdin):
        sys.stdout.write(text + '\n')

if __name__ == '__main__':
    main()
