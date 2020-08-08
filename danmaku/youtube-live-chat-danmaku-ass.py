#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import random
import sys
import struct

RES_X = 1280
RES_Y = 720
FONT_SIZE = 36

# libass doesn't support emoji well
with open('./emoji.json', encoding='utf-8') as f:
    emoji = {o['emoji']: o['shortname'] for o in json.loads(f.read())}

test_data = {
    "replayChatItemAction": {
        "actions": [
            {"addChatItemAction": {
                "item": {
                    "liveChatTextMessageRenderer": { # liveChatPaidMessageRenderer, liveChatMembershipItemRenderer
                        "message": { # liveChatMembershipItemRenderer: New member: authorName
                            "runs": [
                                {"text": "???"},
                                {'emoji': {
                                    'emojiId': '???',
                                    'shortcuts': [':???:'],
                                    'searchTerms': ['???'],
                                    'image': {
                                        'thumbnails': [
                                            {'url': 'https://???.ggpht.com/???', 'width': 24, 'height': 24},
                                            {'url': 'https://???.ggpht.com/???', 'width': 48, 'height': 48}
                                        ],
                                        'accessibility': {'accessibilityData': {'label': ':???:'}}
                                    },
                                    'isCustomEmoji': True
                                }},
                                {"text": "???"}
                            ]
                        },
                        "authorName": {"simpleText": "???"},
                        "authorPhoto": {
                            "thumbnails": [
                                {"url": "https://???.ggpht.com/???", "width": 32, "height": 32},
                                {"url": "https://yt3.ggpht.com/???", "width": 64, "height": 64}
                            ]
                        },
                        "contextMenuEndpoint": {},
                        "id": "???",
                        "timestampUsec": "1596582299312096",
                        "authorExternalChannelId": "???",
                        "contextMenuAccessibility": {"accessibilityData": {"label": "Comment actions"}},
                        "timestampText": {"simpleText": "2:46"}
                    }
                },
                "clientId": "???"
            }}
        ],
        "videoOffsetTimeMsec": "166067"
    }
}

class DanmakuLayers:
    def __init__(self, width, height, size):
        self.width = width
        self.height = height
        self.size = size

        self.layers = [[] for _ in range(int(self.height / size) - 1)]

    def add_bullet(self, bullet):
        length, start_time, end_time = bullet
        for i, layer in enumerate(self.layers):
            layer2 = []
            self.layers[i] = layer2
            for bullet2 in layer:
                bullet2_tail_start1 = self._bullet_tail_position(bullet2, start_time)
                bullet2_tail_end1 = self._bullet_tail_position(bullet2, end_time)
                bullet1_head_end1 = self._bullet_head_position(bullet, end_time)
                if (bullet2_tail_start1 < 0 or bullet2_tail_end1 < bullet1_head_end1):
                    layer2.append(bullet2)
            if len(layer2) == 0:
                layer2.append(bullet)
                return i
        return random.randint(0, len(self.layers))

    def _bullet_tail_position(self, bullet, current_time):
        length, start_time, end_time = bullet
        velocity = (length + self.width) / (end_time - start_time)
        distance = velocity * (current_time - start_time)
        return distance - length

    def _bullet_head_position(self, bullet, current_time):
        length, start_time, end_time = bullet
        velocity = (length + self.width) / (end_time - start_time)
        distance = velocity * (current_time - start_time)
        return distance


class DanmakuASSGenerator:
    ass_header = """[Script Info]
Title: {title}
ScriptType: v4.00+
Collisions: Normal
PlayResX: {playResX}
PlayResY: {playResY}
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Fix,{fontFamily},{fontSize},&H{alpha}FFFFFF,&H{alpha}FFFFFF,&H{alpha}000000,&H{alpha}000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,2,0
Style: Rtl,{fontFamily},{fontSize},&H{alpha}FFFFFF,&H{alpha}FFFFFF,&H{alpha}000000,&H{alpha}000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,2,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

""".format(**{
    'title': 'title',
    'playResX': RES_X,
    'playResY': RES_Y,
    'fontFamily': 'Noto Sans',
    'fontSize': FONT_SIZE,
    'alpha': '00',
})

    def __init__(self):
        self.default_duration = 7000
        self.layers = DanmakuLayers(RES_X, RES_Y, FONT_SIZE)

    def generate(self, messages):
        yield self.ass_header
        for message in messages:
            yield self._generate_dialogue(message)

    def _generate_dialogue(self, message, duration=None):
        # Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        # Dialogue: 0,0:00:00.00,0:00:07.00,Rtl,,20,20,2,,{\q2\fs36\move(1478,72,-198,72)}{\1c&H888888\alpha&H44}Author: {\1c&Hffffff\alpha&H00}body

        start_time = message['offset_msec']
        if duration is None:
            duration = self.default_duration
        end_time = start_time + duration

        def sub_emoji(match):
            emoji_match = match.group(0)
            if emoji_match in emoji:
                return emoji[emoji_match]
            return emoji_match
        def sanitize(text):
            text = re.sub('\s+', ' ', text)
            text = text.replace('{', '｛')
            text = text.replace('}', '｝')
            return text

        body = re.sub('.', sub_emoji, message['body'])
        if message['paid'] is not None:
            body = '[{}] {}'.format(message['paid'], body)
        author = message['author']

        text_width = int(self._estimate_width(author + ': ' + body) * message['size'])
        text_width_half = int(text_width / 2)
        y_offset = FONT_SIZE * (self.layers.add_bullet((text_width, start_time, end_time)) + 1)
        start_pos = (RES_X + text_width_half, y_offset)
        end_pos = (-text_width_half, y_offset)

        color_argb = message['color']
        color_bgra = struct.unpack('<I', struct.pack('>I', color_argb))[0]
        color_bgr = color_bgra >> 8

        z_layer = 0
        if message['size'] > 1:
            z_layer = 0x1fe
            z_layer += color_bgr & 0xff # red
            z_layer -= (color_bgr >> 8) & 0xff # green
            z_layer -= (color_bgr >> 16) & 0xff # blue

        nowrap = "\\q2"
        color = '\\1c&H{:06x}'.format(color_bgr)
        author_color = '\\1c&H888888'
        alpha = '\\alpha&H00'
        author_alpha = '\\alpha&H44'
        font_size = "\\fs{}".format(int(FONT_SIZE * message['size']))
        move = "\\move({start[0]},{start[1]},{end[0]},{end[1]})".format(start=start_pos, end=end_pos)

        formatted_text = "{{{format}}}{{{author_format}}}{author}: {{{body_format}}}{body}".format(**{
            'format': nowrap + font_size + move,
            'author_format': author_color + author_alpha,
            'body_format': color + alpha,
            'author': sanitize(author),
            'body': sanitize(body),
        })
        return "Dialogue: {z_layer},{start},{end},{type},,20,20,2,,{formatted_text}\n".format(**{
            'z_layer': max(0, z_layer),
            'start': self._format_time(start_time),
            'end': self._format_time(end_time),
            'type': 'Rtl',
            'formatted_text': formatted_text,
        })

    def _format_time(self, time_msec):
        time_sec = time_msec / 1000
        mm, ss = divmod(time_sec, 60)
        mm = int(mm)
        hh, mm = divmod(mm, 60)
        return "{}:{:02d}:{:05.2f}".format(hh, mm, ss)

    def _estimate_width(self, text):
        length = 0
        for char in text:
            if 0x4e00 <= ord(char) <= 0x9fff:
                length += 2
            else:
                length += 1
        return length * FONT_SIZE * 0.5


class YoutubeLiveChatReplayParser:
    def parse_messages(self, input_buffer):
        for line in input_buffer:
            yield from self._parse_replay_chat_item_action(json.loads(line))

    def _transform_renderer_message(self, data):
        def map_run(run):
            if 'text' in run:
                return run['text']
            if 'emoji' in run:
                # todo download and embed image
                emoji_shortcuts = sorted(run['emoji']['shortcuts'], key=lambda s: (s.startswith(':_') + 1) * len(s))
                return emoji_shortcuts[0] if len(emoji_shortcuts) > 0 else ''
        return ''.join(map(map_run, data['runs']))

    def _parse_replay_chat_item_action(self, data):
        if 'replayChatItemAction' not in data:
            return
        data = data['replayChatItemAction']
        if 'videoOffsetTimeMsec' not in data:
            return
        offset_msec = int(data['videoOffsetTimeMsec'])
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
            author = None
            paid = None
            size = 1.0
            color = 0x00ffffff # argb
            renderer = None

            if 'liveChatTextMessageRenderer' in action:
                renderer = action['liveChatTextMessageRenderer']
                body = self._transform_renderer_message(renderer['message']) if 'message' in renderer else ''
                author = renderer['authorName']['simpleText']
            elif 'liveChatPaidMessageRenderer' in action:
                renderer = action['liveChatPaidMessageRenderer']
                body = self._transform_renderer_message(renderer['message']) if 'message' in renderer else ''
                author = renderer['authorName']['simpleText']
                paid = renderer['purchaseAmountText']['simpleText']
                size = 1.3
                color = renderer['bodyBackgroundColor']
            elif 'liveChatMembershipItemRenderer' in action:
                renderer = action['liveChatMembershipItemRenderer']
                body = self._transform_renderer_message(renderer['headerSubtext']) if 'headerSubtext' in renderer else ''
                author = renderer['authorName']['simpleText']
                size = 1.2
                color = 0x000f9d58 # argb

            if body is not None:
                yield {
                    'body': body,
                    'author': author,
                    'paid': paid,
                    'size': size,
                    'color': color,
                    'renderer': renderer,
                    'offset_msec': offset_msec,
                }


def main():
    input_buffer = sys.stdin if sys.argv[1] == '-' else open(sys.argv[1], 'r')
    output_buffer = sys.stdout if sys.argv[2] == '-' else open(sys.argv[2], 'w')

    ass_generator = DanmakuASSGenerator()
    parser = YoutubeLiveChatReplayParser()

    messages = parser.parse_messages(input_buffer)
    ass_parts = ass_generator.generate(messages)
    for ass_part in ass_parts:
        output_buffer.write(ass_part)

if __name__ == '__main__':
    main()
