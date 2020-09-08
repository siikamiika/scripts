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
    def f(text, start_time, end_time):
        nonlocal counter
        counter += 1
        return \
'''{counter}
{time}
{text}
'''.format(
    counter=counter,
    time=format_srt_time(start_time) + ' --> ' + format_srt_time(end_time),
    text=text
)
    return f
get_srt_line = _get_srt_line()

def interpolate_srt_lines(lines, start_time, end_time):
    length = end_time - start_time
    total_chars = sum(map(lambda l: len(l[1]), lines[:-1]))
    ext_end_time = start_time + length * ((total_chars + len(lines[-1][1])) / total_chars)

    def gen_lines():
        cur_chars = 0
        for text_prev, text, text_next in lines:
            start_time2 = start_time + length * (cur_chars / total_chars)
            cur_chars += len(text)
            end_time2 = start_time + length * (cur_chars / total_chars)
            text_all = '<font color="#888888">{}</font>\n{}\n<font color="#888888">{}</font>'.format(text_prev or '', text, text_next or '')
            yield get_srt_line(text_all, start_time2, end_time2)

    return gen_lines(), ext_end_time

def iter_next_prev(iterable, transform=lambda v: v):
    iterable = iter(iterable)
    empty_val = transform(None)
    try:
        prev_val = transform(next(iterable))
    except StopIteration:
        yield empty_val, prev_val, empty_val
        return
    try:
        cur_val = transform(next(iterable))
    except StopIteration:
        yield empty_val, prev_val, cur_val
        yield prev_val, cur_val, empty_val
        return
    yield empty_val, prev_val, cur_val
    while True:
        try:
            next_val = transform(next(iterable))
            yield prev_val, cur_val, next_val
            prev_val = cur_val
            cur_val = next_val
        except StopIteration:
            yield prev_val, cur_val, empty_val
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
    if line is None:
        return None, None
    try:
        text, time_str = json.loads(line)
        return text, parse_seconds(time_str)
    except json.decoder.JSONDecodeError:
        return line.strip(), None

def lines_to_srt(lines):
    start_time = None
    buf = []
    for line_prev, line, line_next in iter_next_prev(lines, parse_json_or_raw):
        text, seconds = line
        buf.append([line_prev[0], text, line_next[0]])

        if start_time is None:
            start_time = seconds
            continue
        if seconds is not None:
            srt_lines, start_time = interpolate_srt_lines(buf, start_time, seconds)
            yield from srt_lines
            buf = []
            continue
    if len(buf) > 0:
        raise Exception('Extrapolation not supported')

for l in lines_to_srt(sys.stdin):
    print(l)
