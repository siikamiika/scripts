#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import sys
import struct

RES_X = 1280
RES_Y = 720
FONT_SIZE = 30

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

# libass doesn't support emoji well
with open(SCRIPT_PATH + '/emoji.json', encoding='utf-8') as f:
    emoji = {o['emoji']: o['shortname'] for o in json.loads(f.read())}
with open(SCRIPT_PATH + '/char_widths.json', encoding='utf-8') as f:
    char_widths = json.loads(f.read())

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

class DanmakuBullet:
    def __init__(self, length, start_time, end_time):
        self.length = length
        self.start_time = start_time
        self.end_time = end_time

    def shift(self, offset):
        self.start_time += offset
        self.end_time += offset

    def __repr__(self):
        return 'DanmakuBullet<length={}, start_time={}, end_time={}>'.format(self.length, self.start_time, self.end_time)

class DanmakuLayers:
    def __init__(self, width, layer_count):
        self.width = width

        self.layers = [[] for _ in range(layer_count)]
        self.layer_order = list(range(len(self.layers)))

    def add_element(self, length, start_time, end_time):
        bullet = DanmakuBullet(length, start_time, end_time)

        for i in self.layer_order:
            layer = self.layers[i]
            layer2 = []
            self.layers[i] = layer2
            is_full = False
            for bullet2 in layer:
                if bullet2.end_time > bullet.start_time:
                    layer2.append(bullet2)
                bullet2_tail_start1 = self._bullet_tail_position(bullet2, bullet.start_time)
                bullet1_head_end2 = self._bullet_head_position(bullet, bullet2.end_time)
                if bullet2_tail_start1 < 0 or bullet1_head_end2 > self.width:
                    is_full = True
            if not is_full:
                layer2.append(bullet)
                return i, 0

        min_offset_idx = None
        min_offset = None
        for i in self.layer_order:
            layer = self.layers[i]
            max_offset = 0.0
            for bullet2 in layer:
                bullet2_tail_start1 = self._bullet_tail_position(bullet2, bullet.start_time)
                bullet1_head_end2 = self._bullet_head_position(bullet, bullet2.end_time)
                bullet2_tail_start1_offset = max(0, 0 - bullet2_tail_start1)
                bullet1_head_end2_offset = max(0, bullet1_head_end2 - self.width)
                max_offset = max(max_offset, bullet2_tail_start1_offset, bullet1_head_end2_offset)
            if min_offset_idx is None or max_offset < min_offset:
                min_offset_idx, min_offset = i, max_offset
        min_time_offset = self._bullet_travel_time(bullet, min_offset)
        bullet.shift(min_time_offset)
        self.layers[min_offset_idx].append(bullet)
        return min_offset_idx, min_time_offset

    def update_priority(self, n, remainder):
        priority = []
        rest = []
        for i in range(len(self.layers)):
            if i % n == remainder:
                priority.append(i)
            else:
                rest.append(i)
        self.layer_order = priority + rest

    def _bullet_tail_position(self, bullet, current_time):
        return self._bullet_distance(bullet, current_time) - bullet.length

    def _bullet_head_position(self, bullet, current_time):
        return self._bullet_distance(bullet, current_time)

    def _bullet_distance(self, bullet, current_time):
        velocity = self._bullet_velocity(bullet)
        return velocity * (current_time - bullet.start_time)

    def _bullet_velocity(self, bullet):
        return (bullet.length + self.width) / (bullet.end_time - bullet.start_time)

    def _bullet_travel_time(self, bullet, distance):
        velocity = self._bullet_velocity(bullet)
        return distance / velocity


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
        self.y_layer_count = int(RES_Y / FONT_SIZE) - 1
        self.z_layer_to_danmaku_index = {}
        self.danmaku_layers = []

    def generate(self, messages):
        yield self.ass_header
        for message in messages:
            yield self._generate_dialogue(message)

    def _generate_dialogue(self, message):
        # Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        # Dialogue: 0,0:00:00.00,0:00:07.00,Rtl,,20,20,2,,{\q2\fs36\move(1478,72,-198,72)}{\1c&H888888\alpha&H44}Author: {\1c&Hffffff\alpha&H00}body

        start_time = message['offset_msec']
        duration = self.default_duration * message['duration']
        end_time = start_time + duration

        z_layer = int((message['duration'] - 1.0) * 10)
        danmaku_index = self.z_layer_to_danmaku_index.get(z_layer)
        if danmaku_index is None:
            danmaku_index = len(self.danmaku_layers)
            self.z_layer_to_danmaku_index[z_layer] = danmaku_index
            self.danmaku_layers.append(DanmakuLayers(RES_X, self.y_layer_count))
            for danmaku_index2, danmaku_layers2 in enumerate(self.danmaku_layers):
                danmaku_layers2.update_priority(danmaku_index + 1, danmaku_index2)
        danmaku_layers = self.danmaku_layers[danmaku_index]

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

        layer_index, time_offset = danmaku_layers.add_element(text_width, start_time, end_time)

        y_offset = FONT_SIZE * (layer_index + 1)
        start_pos = (RES_X + text_width_half, y_offset)
        end_pos = (-text_width_half, y_offset)

        start_time += time_offset
        end_time += time_offset

        def convert_color(color_argb):
            color_bgra = struct.unpack('<I', struct.pack('>I', color_argb))[0]
            color_bgr = color_bgra >> 8
            return color_bgr

        color_bgr = convert_color(message['color'])
        author_color_bgr = convert_color(message['author_color'])

        nowrap = "\\q2"
        color = '\\1c&H{:06x}'.format(color_bgr)
        author_color = '\\1c&H{:06x}'.format(author_color_bgr)
        alpha = '\\alpha&H{:02x}'.format(message['alpha'])
        author_alpha = '\\alpha&H{:02x}'.format(message['author_alpha'])
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
            'z_layer': z_layer,
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
            length += char_widths[char] / 100
        return length * FONT_SIZE * 0.9


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

    def _parse_badge_types(self, data):
        badge_types = set()
        for badge in data:
            badge = badge['liveChatAuthorBadgeRenderer']
            if 'icon' in badge:
                icon = badge['icon']
                if icon['iconType'] == 'OWNER':
                    badge_types.add('owner')
                if icon['iconType'] == 'MODERATOR':
                    badge_types.add('moderator')
                if icon['iconType'] == 'VERIFIED':
                    badge_types.add('verified')
            if 'customThumbnail' in badge:
                badge_types.add('sponsor')
        return badge_types

    def _badge_color(self, badge_types):
        # color is argb
        for badge_type, color in (('owner', 0x00ffd600), ('moderator', 0x005e84f1), ('sponsor', 0x002ba640)):
            if badge_type in badge_types:
                return color
        return 0x00888888

    def _badge_text(self, badge_types):
        badges = [b[0] for b in badge_types]
        if len(badges) == 0:
            return ''
        return '({})'.format(','.join(badges))

    def _badge_alpha(self, badge_types):
        if 'owner' in badge_types:
            return 0x00
        if 'moderator' in badge_types:
            return 0x00
        if 'verified' in badge_types:
            return 0x00
        if 'sponsor' in badge_types:
            return 0xaa
        return 0xbb

    def _badge_size(self, badge_types):
        if 'owner' in badge_types:
            return 1.3
        if 'moderator' in badge_types:
            return 1.3
        return 1.0

    def _badge_duration(self, badge_types):
        if 'owner' in badge_types:
            return 2.5
        if 'moderator' in badge_types:
            return 2.5
        if 'verified' in badge_types:
            return 1.5
        return 1.0

    def _color_duration(self, color):
        duration = 0x1fe
        duration += (color >> 16) & 0xff # red
        duration -= (color >> 8) & 0xff # green
        duration -= color & 0xff # blue
        return (1 + (duration / 0x2fd) * 0.8)

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
            author_color = 0x00888888
            alpha = 0x00
            author_alpha = 0xbb
            duration = 1.0
            renderer = None

            def update_badges(renderer):
                nonlocal author, author_color, author_alpha, size, duration
                if 'authorBadges' in renderer:
                    badge_types = self._parse_badge_types(renderer['authorBadges'])
                    author = (author + ' ' + self._badge_text(badge_types)).strip()
                    author_color = self._badge_color(badge_types)
                    author_alpha = self._badge_alpha(badge_types)
                    size *= self._badge_size(badge_types)
                    duration *= self._badge_duration(badge_types)

            if 'liveChatTextMessageRenderer' in action:
                renderer = action['liveChatTextMessageRenderer']
                body = self._transform_renderer_message(renderer['message']) if 'message' in renderer else ''
                author = renderer['authorName']['simpleText']
                update_badges(renderer)
            elif 'liveChatPaidMessageRenderer' in action:
                renderer = action['liveChatPaidMessageRenderer']
                body = self._transform_renderer_message(renderer['message']) if 'message' in renderer else ''
                author = renderer['authorName']['simpleText']
                paid = renderer['purchaseAmountText']['simpleText']
                update_badges(renderer)
                size *= 1.1
                color = renderer['bodyBackgroundColor']
                duration *= self._color_duration(color)
            elif 'liveChatMembershipItemRenderer' in action:
                renderer = action['liveChatMembershipItemRenderer']
                body = self._transform_renderer_message(renderer['headerSubtext']) if 'headerSubtext' in renderer else ''
                author = renderer['authorName']['simpleText']
                update_badges(renderer)
                color = 0x000f9d58 # argb

            if body is not None:
                yield {
                    'body': body,
                    'author': author,
                    'paid': paid,
                    'size': size,
                    'color': color,
                    'author_color': author_color,
                    'alpha': alpha,
                    'author_alpha': author_alpha,
                    'duration': duration,
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
