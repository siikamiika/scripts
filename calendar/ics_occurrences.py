#!/usr/bin/env python3

import argparse
import datetime
import json

import icalendar
import dateutil.rrule

def coerce_datetime(date_obj):
    if type(date_obj) == datetime.date:
        return datetime.datetime.combine(date_obj, datetime.datetime.min.time(), tzinfo=datetime.timezone.utc)
    return date_obj

def convert_rrule_attr(rrule, name, fallback=None):
    res = rrule.get(name)
    if res:
        assert len(res) == 1
        if isinstance(res[0], str):
            return getattr(dateutil.rrule, res[0])
        elif isinstance(res[0], datetime.date):
            return coerce_datetime(res[0])
        return res[0]
    return fallback

def parse_rrule(vevent):
    rrule = vevent.get('RRULE')
    assert len(rrule.get('FREQ')) == 1

    dtstart = coerce_datetime(vevent.get('DTSTART').dt)
    return dateutil.rrule.rrule(
        convert_rrule_attr(rrule, 'FREQ'),
        dtstart=dtstart,
        interval=convert_rrule_attr(rrule, 'INTERVAL', 1),
        wkst=convert_rrule_attr(rrule, 'WKST'),
        count=convert_rrule_attr(rrule, 'COUNT'),
        until=convert_rrule_attr(rrule, 'UNTIL'),
        bysetpos=None,
        bymonth=convert_rrule_attr(rrule, 'BYMONTH'),
        bymonthday=convert_rrule_attr(rrule, 'BYMONTHDAY'),
        byyearday=convert_rrule_attr(rrule, 'BYYEARDAY'),
        byeaster=None,
        byweekno=convert_rrule_attr(rrule, 'BYWEEKNO'),
        byweekday=convert_rrule_attr(rrule, 'BYWEEKDAY'),
        byhour=convert_rrule_attr(rrule, 'BYHOUR'),
        byminute=convert_rrule_attr(rrule, 'BYMINUTE'),
        bysecond=convert_rrule_attr(rrule, 'BYSECOND'),
        cache=False
    )

def get_occurrences(vevent, start_dt, end_dt):
    """
    Check whether `vevent` starting time is between `start_dt` and `end_dt`
    """
    dt = coerce_datetime(vevent.get('DTSTART').dt)
    if vevent.get('RRULE'):
        rrule_parsed = parse_rrule(vevent)
        occurrences = rrule_parsed.between(start_dt, end_dt, inc=True)
        for occurrence in occurrences:
            yield dt.replace(**{k: getattr(occurrence, k) for k in ['year', 'month', 'day']})
        return None
    else:
        if start_dt <= dt <= end_dt:
            yield dt

def parse_date_to_utc(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)

def main():
    parser = argparse.ArgumentParser(description='Get matching calendar event occurrences')
    parser.add_argument('calendar', help='ICS calendar file')
    parser.add_argument('--start-date', type=parse_date_to_utc, help='Start date, %Y-%m-%d', required=True)
    parser.add_argument('--end-date', type=parse_date_to_utc, help='End date, %Y-%m-%d', required=True)
    args = parser.parse_args()
    with open(args.calendar) as f:
        cal = icalendar.Calendar.from_ical(f.read())
    matches = []
    for sub in cal.subcomponents:
        if isinstance(sub, icalendar.Event):
            rrule_parsed = parse_rrule(sub) if sub.get('RRULE') else None
            for occurrence in get_occurrences(
                sub,
                args.start_date,
                args.end_date,
            ):
                matches.append((sub, occurrence, rrule_parsed))
    for vevent, occurrence, rrule_parsed in sorted(matches, key=lambda m: m[1]):
        print(json.dumps({
            'start_datetime': occurrence.isoformat(),
            'duration_hours': (vevent.get('DTEND').dt - vevent.get('DTSTART').dt).total_seconds() / 60 / 60,
            'summary': vevent.get('SUMMARY'),
            'description': vevent.get('DESCRIPTION'),
            'rrule': str(rrule_parsed),
        }, ensure_ascii=False))

if __name__ == '__main__':
    main()
