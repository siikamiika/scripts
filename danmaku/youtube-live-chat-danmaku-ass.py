#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import sys
import struct
import hashlib
import datetime
import pytz
import requests

RES_X = 1280
RES_Y = 720
FONT_SIZE = 30
TIMEZONES = [
    'Asia/Tokyo',
    'Europe/Helsinki',
    'US/Eastern',
    'US/Pacific',
]

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
Style: Rtl,{fontFamily},{fontSize},&H{alpha}FFFFFF,&H{alpha}FFFFFF,&H{alpha}000000,&H{alpha}000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,2,0
Style: Datetime,{fontFamily},{datetimeFontSize},&H{datetimeAlpha}FFFFFF,&H{datetimeAlpha}FFFFFF,&H{datetimeAlpha}000000,&H{datetimeAlpha}000000,1,0,0,0,100,100,0,0,1,2,0,7,20,20,2,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

""".format(**{
    'title': 'title',
    'playResX': RES_X,
    'playResY': RES_Y,
    'fontFamily': 'Noto Sans',
    'fontSize': FONT_SIZE,
    'datetimeFontSize': int(FONT_SIZE * 0.6),
    'alpha': '00',
    'datetimeAlpha': '77',
})

    def __init__(self):
        self.default_duration = 7000
        self.y_layer_count = int(RES_Y / FONT_SIZE) - 1
        self.z_layer_to_danmaku_index = {}
        self.danmaku_layers = []
        self._start_timestamp = None
        self._previous_minutes = -1

    def generate(self, messages):
        yield self.ass_header
        for message in messages:
            if message['offset_msec'] > 0:
                yield from self._generate_datetime(message['timestamp'], message['offset_msec'])
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
            # if emoji_match in emoji:
            #     return emoji[emoji_match]
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

        y_offset = FONT_SIZE * (layer_index + 1.2)
        start_pos = (RES_X + text_width_half, y_offset)
        end_pos = (-text_width_half, y_offset)

        start_time += time_offset
        end_time += time_offset

        def convert_color(color_argb):
            color_bgra = struct.unpack('<I', struct.pack('>I', color_argb))[0]
            alpha = color_bgra & 0xff
            color_bgr = (color_bgra >> 8) & 0xffffff
            return color_bgr, alpha

        color_bgr, alpha = convert_color(message['color'])
        author_color_bgr, author_alpha = convert_color(message['author_color'])

        ass_nowrap = "\\q2"
        ass_color = '\\1c&H{:06x}'.format(color_bgr)
        ass_author_color = '\\1c&H{:06x}'.format(author_color_bgr)
        ass_alpha = '\\alpha&H{:02x}'.format(alpha)
        ass_author_alpha = '\\alpha&H{:02x}'.format(author_alpha)
        ass_font_size = "\\fs{}".format(int(FONT_SIZE * message['size']))
        ass_move = "\\move({start[0]:.0f},{start[1]:.0f},{end[0]:.0f},{end[1]:.0f})".format(start=start_pos, end=end_pos)

        ass_formatted_text = "{{{format}}}{{{author_format}}}{author}: {{{body_format}}}{body}".format(**{
            'format': ass_nowrap + ass_font_size + ass_move,
            'author_format': ass_author_color + ass_author_alpha,
            'body_format': ass_color + ass_alpha,
            'author': sanitize(author),
            'body': sanitize(body),
        })
        return "Dialogue: {z_layer},{start},{end},Rtl,,20,20,2,,{formatted_text}\n".format(**{
            'z_layer': z_layer,
            'start': self._format_time(start_time),
            'end': self._format_time(end_time),
            'formatted_text': ass_formatted_text,
        })

    def _generate_datetime(self, timestamp, offset_msec):
        if self._start_timestamp is None:
            self._start_timestamp = timestamp - (offset_msec / 1000)
        minute_in_msec = 60 * 1000
        new_minutes = int(offset_msec / minute_in_msec) - self._previous_minutes
        for i in range(new_minutes):
            start_time = (self._previous_minutes + i + 1) * minute_in_msec
            for timezone in TIMEZONES:
                yield "Dialogue: 999,{start},{end},Datetime,,20,20,2,,{formatted_text}\n".format(**{
                    'start': self._format_time(start_time),
                    'end': self._format_time(start_time + minute_in_msec),
                    'formatted_text': self._format_datetime(self._start_timestamp + start_time / 1000, timezone),
                })
            self._previous_minutes += new_minutes

    def _format_time(self, time_msec):
        time_sec = time_msec / 1000
        mm, ss = divmod(time_sec, 60)
        mm = int(mm)
        hh, mm = divmod(mm, 60)
        return "{}:{:02d}:{:05.2f}".format(hh, mm, ss)

    def _format_datetime(self, timestamp, timezone):
        dt = datetime.datetime.fromtimestamp(timestamp, pytz.timezone(timezone))
        return dt.strftime('%a %Y-%m-%d %H:%M %Z')

    def _estimate_width(self, text):
        length = 0
        for char in text:
            length += char_widths[char] / 100
        return length * FONT_SIZE * 0.9


class UrlCache:

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0',
        'Accept-Encoding': 'gzip, deflate',
    }

    def __init__(self, base_dir):
        self._base_dir = base_dir

    def ensure(self, context, url):
        context_path = self._build_context_path(context)
        cache_filename = self._hash_url(url)
        full_path = os.path.join(context_path, cache_filename)
        if os.path.isfile(full_path):
            return full_path
        self._download_url_content(url, full_path)
        if not os.path.isfile(full_path):
            raise RuntimeError('File download failed:\n  {}\n  --> {}'.format(url, full_path))
        return full_path

    def _hash_url(self, url):
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def _build_context_path(self, context):
        path = os.path.join(self._base_dir, *context)
        os.makedirs(path, exist_ok=True)
        return path

    def _download_url_content(self, url, full_path):
        req = requests.get(url, headers=UrlCache.HEADERS)
        with open(full_path, 'wb') as f:
            f.write(req.content)


class CustomEmojiMapper:

    # hopefully avoid collisions with font awesome, mpv font, openmoji and others
    PRIVATE_RANGE = range(0xe400, 0xeeff)

    def __init__(self):
        self._image_cache = UrlCache(os.path.join(SCRIPT_PATH, 'image_cache'))
        self._url_by_emoji = self._load_mapped_emoji()
        self._emoji_by_url = {self._url_by_emoji[emoji]: emoji for emoji in self._url_by_emoji}
        self._codepoints = iter(CustomEmojiMapper.PRIVATE_RANGE)

    def get_mapping(self, url):
        if url in self._emoji_by_url:
            return self._emoji_by_url[url]
        return self._generate_mapping(url)

    def _generate_mapping(self, url):
        while True:
            codepoint = str(next(self._codepoints))
            if codepoint not in self._url_by_emoji:
                break
        self._image_cache.ensure(['emoji'], url)
        self._url_by_emoji[codepoint] = url
        self._emoji_by_url[url] = codepoint
        self._save_mapped_emoji()
        return codepoint

    def _load_mapped_emoji(self):
        path = self._get_mapped_emoji_path()
        if not os.path.isfile(path):
            return {}
        with open(path, encoding='utf-8') as f:
            return json.loads(f.read())

    def _save_mapped_emoji(self):
        path = self._get_mapped_emoji_path()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self._url_by_emoji))

    def _get_mapped_emoji_path(self):
        return os.path.join(SCRIPT_PATH, 'mapped_emoji.json')


class YoutubeLiveChatReplayParser:
    def __init__(self):
        self._custom_emoji_mapper = CustomEmojiMapper()

    def parse_messages(self, input_buffer):
        for line in input_buffer:
            yield from self._parse_replay_chat_item_action(json.loads(line))

    def _transform_renderer_message(self, data):
        def map_run(run):
            if 'text' in run:
                return run['text']
            if 'emoji' in run:
                best_thumbnail = None
                for thumbnail in run['emoji']['image']['thumbnails']:
                    if best_thumbnail is None:
                        best_thumbnail = thumbnail
                    elif best_thumbnail['width'] < thumbnail['width']:
                        best_thumbnail = thumbnail
                return chr(int(self._custom_emoji_mapper.get_mapping(best_thumbnail['url'])))
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
        if 'owner' in badge_types:
            return 0x00ffd600
        if 'moderator' in badge_types:
            return 0x005e84f1
        if 'sponsor' in badge_types:
            return 0xaa2ba640
        return 0xbb888888

    def _badge_text(self, badge_types):
        badges = [b[0] for b in badge_types]
        if len(badges) == 0:
            return ''
        return '({})'.format(','.join(badges))

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
        # some of these are bugged and have timestamp instead, just skip them
        if offset_msec > 1262304000: # year 2010
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

            body = ''
            author = ''
            paid = None
            size = 1.0
            color = 0x00ffffff # argb
            author_color = 0xbb888888
            duration = 1.0
            timestamp = None
            renderer = None

            def update_common_props(renderer):
                nonlocal author, author_color, size, duration, timestamp, body
                if 'timestampUsec' in renderer:
                    timestamp = float(renderer['timestampUsec']) / 1000000
                if 'authorName' in renderer:
                    author = renderer['authorName']['simpleText']
                if 'authorBadges' in renderer:
                    badge_types = self._parse_badge_types(renderer['authorBadges'])
                    author = (author + ' ' + self._badge_text(badge_types)).strip()
                    author_color = self._badge_color(badge_types)
                    size *= self._badge_size(badge_types)
                    duration *= self._badge_duration(badge_types)
                if 'message' in renderer:
                    body = self._transform_renderer_message(renderer['message'])
                elif 'headerSubtext' in renderer:
                    body = self._transform_renderer_message(renderer['headerSubtext'])

            if 'liveChatTextMessageRenderer' in action:
                renderer = action['liveChatTextMessageRenderer']
                update_common_props(renderer)
            elif 'liveChatPaidMessageRenderer' in action:
                renderer = action['liveChatPaidMessageRenderer']
                update_common_props(renderer)
                paid = renderer['purchaseAmountText']['simpleText']
                size *= 1.1
                color = (color & ~0xffffff) ^ (renderer['bodyBackgroundColor'] & 0xffffff)
                duration *= self._color_duration(color)
            elif 'liveChatMembershipItemRenderer' in action:
                renderer = action['liveChatMembershipItemRenderer']
                update_common_props(renderer)
                color = (color & ~0xffffff) ^ 0x000f9d58

            if renderer is not None:
                yield {
                    'body': body,
                    'author': author,
                    'paid': paid,
                    'size': size,
                    'color': color,
                    'author_color': author_color,
                    'duration': duration,
                    'timestamp': timestamp,
                    'renderer': renderer,
                    'offset_msec': offset_msec,
                }


def main():
    input_buffer = sys.stdin if sys.argv[1] == '-' else open(sys.argv[1], 'r', encoding="utf-8")
    output_buffer = sys.stdout if sys.argv[2] == '-' else open(sys.argv[2], 'w', encoding="utf-8")

    ass_generator = DanmakuASSGenerator()
    parser = YoutubeLiveChatReplayParser()

    messages = parser.parse_messages(input_buffer)
    ass_parts = ass_generator.generate(messages)
    for ass_part in ass_parts:
        output_buffer.write(ass_part)

if __name__ == '__main__':
    main()
