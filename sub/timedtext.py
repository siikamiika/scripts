import json
import sys

# TODO use offset to shift visible text between events

def format_ms_hmsf(ms):
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return '{:02d}:{:02d}:{:02d},{:03d}'.format(h, m, s, ms)

d = json.loads(sys.stdin.read())

rows = []
for ev in d['events']:
    if 'segs' not in ev or 'dDurationMs' not in ev:
        continue
    text = ''.join(p['utf8'] for p in ev['segs']).strip()
    if not text:
        continue
    start = ev['tStartMs']
    end = start + ev['dDurationMs']
    if rows:
        # avoid overlap
        rows[-1][1] = start
    rows.append([
        start,
        end,
        text,
    ])

ctr = 1
for start, end, text in rows:
    # counter
    print(ctr)
    # start/end
    print('{} --> {}'.format(
        format_ms_hmsf(start),
        format_ms_hmsf(end),
    ))
    # text
    print(text)
    print()
    ctr += 1
