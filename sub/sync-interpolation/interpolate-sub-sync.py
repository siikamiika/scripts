#!/usr/bin/env python3

import sys
import json
import re

def format_srt_time(seconds):
    ss, frac = divmod(seconds, 1)
    ms = min(int(frac * 1000), 999)
    mm, ss = divmod(ss, 60)
    hh, mm = divmod(mm, 60)
    return '{h:02.0f}:{m:02.0f}:{s:02.0f},{ms:03.0f}'.format(h=hh, m=mm, s=ss, ms=ms)

def _get_srt_line():
    counter = 0
    def f(line):
        nonlocal counter
        counter += 1
        return \
'''{counter}
{time}
<font color="#888888">{prev_text}</font>
{text}
<font color="#888888">{next_text}</font>
'''.format(
    counter=counter,
    time=format_srt_time(line.start_time) + ' --> ' + format_srt_time(line.end_time),
    prev_text=line.prev_text or '',
    text=line.text,
    next_text=line.next_text or '',
)
    return f
get_srt_line = _get_srt_line()

def interpolate_lines(lines):
    start_time = lines[0].value.time or lines[0].prev.value.end_time
    end_time = lines[-1].value.time
    length = end_time - start_time
    total_chars = sum(map(lambda n: len(n.value.text), lines[:-1]))
    ext_end_time = start_time + length * ((total_chars + len(lines[-1].value.text)) / total_chars)

    def gen_lines():
        class Line:
            def __init__(self, text, prev_text, next_text, start_time, end_time):
                self.text = text
                self.prev_text = prev_text
                self.next_text = next_text
                self.start_time = start_time
                self.end_time = end_time
        cur_chars = 0
        for node in lines:
            start_time2 = start_time + length * (cur_chars / total_chars)
            cur_chars += len(node.value.text)
            end_time2 = start_time + length * (cur_chars / total_chars)
            yield Line(
                node.value.text,
                node.prev.value.text,
                node.next.value.text,
                start_time2,
                end_time2
            )

    return gen_lines(), ext_end_time

def linked_iter(iterable, transform=lambda v: v):
    class Node:
        def __init__(self, value, prev_node=None, next_node=None):
            self.value = value
            self._prev = prev_node
            self._next = next_node

        def __repr__(self):
            prev_value = self.prev.value if self.prev else None
            next_value = self.next.value if self.next else None
            return 'Node<value={}, prev=Node<value={}>, next=Node<value={}>>'.format(self.value, prev_value, next_value)

        @property
        def prev(self):
            return self._prev or Node(transform(None))

        @property
        def next(self):
            return self._next or Node(transform(None))

        @prev.setter
        def prev(self, val):
            self._prev = val

        @next.setter
        def next(self, val):
            self._next = val

    iterable = iter(iterable)
    try:
        node_prev = Node(transform(next(iterable)))
    except StopIteration:
        return
    try:
        node_cur = Node(transform(next(iterable)), prev_node=node_prev)
        node_prev.next = node_cur
    except StopIteration:
        yield node_prev
        return
    yield node_prev
    while True:
        try:
            node_next = Node(transform(next(iterable)), prev_node=node_cur)
            node_cur.next = node_next
            yield node_cur
            node_prev = node_cur
            node_cur = node_next
        except StopIteration:
            yield node_cur
            break

def parse_seconds(time_str):
    # [hhh*:]mm:ss[.f+]
    hh, mm, ss = re.match(r'(?:(\d\d\d*):)?(\d\d):(\d\d(?:\.\d+)?)', time_str).groups()
    return (
        int(hh or 0) * 60 * 60
        + int(mm) * 60
        + float(ss)
    )

def parse_json_or_raw(line):
    class TimedText:
        def __init__(self, text, time_str):
            self.text = text
            self.time = time_str
            self.end_time = None

        def __repr__(self):
            return 'TimedText<text={} time={} end_time={}>'.format(self.text, self.time, self.end_time)

    if line is None:
        return TimedText(None, None)
    try:
        text, time_str = json.loads(line)
        return TimedText(text, parse_seconds(time_str))
    except json.decoder.JSONDecodeError:
        return TimedText(line.strip(), None)

def lines_to_srt(lines):
    buf = []
    first = True
    for node in linked_iter(lines, parse_json_or_raw):
        buf.append(node)
        if not first and node.value.time is not None:
            lines, node.value.end_time = interpolate_lines(buf)
            yield from map(get_srt_line, lines)
            buf = []
            continue
        first = False
    if len(buf) > 0:
        raise Exception('Extrapolation not supported')

for l in lines_to_srt(sys.stdin):
    print(l)
