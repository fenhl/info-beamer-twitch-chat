#!/usr/bin/env python3

import sys

import basedir
import datetime
import json
import more_itertools
import pathlib
import re
import requests
import sleeptill
import time

CACHE = {
    'client_id': None
}

def client_id():
    if CACHE['client_id'] is None:
        CACHE['client_id'] = basedir.config_dirs('info-beamer-twitch-chat.json').json()['clientID']
    return CACHE['client_id']

def format_timedelta(timestamp):
    minutes, seconds = divmod(timestamp.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

def format_color(color_str):
    if color_str.startswith('#'):
        color_str = color_str[1:]
    return {
        'r': int(color_str[0:2], 16) / 255,
        'g': int(color_str[2:4], 16) / 255,
        'b': int(color_str[4:6], 16) / 255
    }

def format_message(message):
    result = {
        'timestamp': format_timedelta(datetime.timedelta(seconds=message['content_offset_seconds'])),
        'user': message['commenter']['display_name'],
        'message': message['message']['body'].split(' ') #TODO use fragments instead and apply formatting
    }
    if 'user_color' in message['message']:
        result['userColor'] = format_color(message['message']['user_color'])
    return result

def get_json(*args, headers={}, **kwargs):
    response = requests.get(*args, headers={'Client-ID': client_id(), **headers}, **kwargs)
    response.raise_for_status()
    return response.json()

def parse_duration(duration_str):
    total = datetime.timedelta()
    while duration_str:
        match = re.match('([0-9]+[hms])', duration_str)
        if not match:
            return total + datetime.timedelta(seconds=float(duration_str))
        part = match.group(1)
        num = int(part[:-1])
        unit = part[-1]
        total += datetime.timedelta(**{{'h': 'hours', 'm': 'minutes', 's': 'seconds'}[unit]: num})
        duration_str = duration_str[len(part):]
    return total

def replay(video_id, start=datetime.timedelta(), *, max_lines=50, out=pathlib.Path('data.json')):
    replay_start = datetime.datetime.now(datetime.timezone.utc) - start
    #vod_info = get_json('https://api.twitch.tv/helix/videos', params={'id': video_id})
    #video_len = parse_duration(more_itertools.one(vod_info['data'])['duration'])
    j = get_json('https://api.twitch.tv/v5/videos/{}/comments'.format(video_id), params={'content_offset_seconds': start.total_seconds()})
    data = []
    while j is not None:
        for message in j['comments']:
            if message['state'] != 'published':
                raise ValueError('Unknown message state: {}'.format(message['state']))
            if message['more_replies']:
                raise ValueError('Not sure what message["more_replies"] does')
            msg_offset = datetime.timedelta(seconds=message['content_offset_seconds'])
            if msg_offset < start:
                continue
            data.append(format_message(message))
            if len(data) > max_lines:
                data = data[-max_lines:]
            sleeptill.sleep_until(replay_start + msg_offset)
            with out.open('w') as out_f:
                json.dump(data, out_f, indent=4, sort_keys=True)
                print(file=out_f)
        if '_next' in j:
            j = get_json('https://api.twitch.tv/v5/videos/{}/comments'.format(video_id), params={'cursor': j['_next']})
        else:
            j = None

if __name__ == '__main__':
    if len(sys.argv) > 2:
        start = parse_duration(sys.argv[2])
    else:
        start = datetime.timedelta()
    replay(sys.argv[1], start)
    while True:
        time.sleep(1) # keep script alive so info-beamer can be quit using ^C
