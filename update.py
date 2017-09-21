#!/usr/bin/env python3

import sys

import datetime
import json
import pathlib
import re
import requests
import sleeptill

def format_timedelta(timestamp):
    minutes, seconds = divmod(timestamp.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))

def format_message(message):
    a = message['attributes']
    return [
        format_timedelta(datetime.timedelta(milliseconds=a['video-offset'])),
        '{}:'.format(a['from'])
    ] + a['message'].split(' ')

def replay(video_id, start=datetime.timedelta(), *, max_lines=50, out=pathlib.Path('data.json')):
    replay_start = datetime.datetime.now(datetime.timezone.utc) - start
    video_id_str = 'v{}'.format(video_id)
    j = requests.get('https://rechat.twitch.tv/rechat-messages', params={'video_id': video_id_str, 'start': '0'}).json()
    match = re.fullmatch('0 is not between ([0-9]+) and ([0-9]+)', j['errors'][0]['detail'])
    if not match:
        raise RuntimeError(j['errors'][0]['detail'])
    video_len = (int(match.group(2)) - int(match.group(1)))
    data = []
    for offset_secs in range((start // datetime.timedelta(seconds=30)) * 30, video_len, 30):
        offset = datetime.timedelta(seconds=offset_secs)
        j = requests.get('https://rechat.twitch.tv/rechat-messages', params={'video_id': video_id_str, 'offset_seconds': str(offset_secs)}).json()
        for message in j['data']:
            if message['type'] != 'rechat-message':
                raise ValueError('Unknown message type: {}'.format(message['type']))
            msg_offset = datetime.timedelta(milliseconds=message['attributes']['video-offset'])
            if msg_offset < start:
                continue
            data.append(format_message(message))
            if len(data) > max_lines:
                data = data[-max_lines:]
            sleeptill.sleep_until(replay_start + msg_offset)
            with out.open('w') as out_f:
                json.dump(data, out_f, indent=4, sort_keys=True)
                print(file=out_f)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        start = datetime.timedelta(seconds=int(sys.argv[2]))
    else:
        start = datetime.timedelta()
    replay(sys.argv[1], start)
