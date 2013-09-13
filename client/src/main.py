# -*- coding: utf-8 -*-
import random
import sys
import time
import json
import subprocess
from collections import OrderedDict
import threading
import uuid

import requests


songs = OrderedDict()


def get_song(api_root):
    url = "{0}/next".format(api_root)
    d = json.loads(requests.get(url).text)
    song = {
        'uid': d['uid'],
        'url': d['url'],
        'filename': None
    }
    print "fetched", song['url'], "from server"
    return song


def delete_remote_song(api_root, song):
    url = "{0}/{1}".format(api_root, song['uid'])
    requests.delete(url)
    print "deleted", song['url'], "from server"


def delete_local_song(song):
    command = "rm {0}".format(song['filename'])
    subprocess.call(command, shell=True)
    print "unlinked local file", song['filename']


def download_song(song):
    print "Downloading", song['url']
    fname = "{0}".format(unicode(uuid.uuid4()))
    command = "youtube-dl -x --audio-format wav -o {0}.mp4 {1}".format(fname, song['url'])
    call_result = subprocess.call(command, shell=True)
    song['filename'] = "{0}.wav".format(fname)
    print "Downloaded", song['url'], "as", song['filename']
    return call_result


def play_song(song):
    print "Playing", s['url']
    command = "aplay -f cd \"{0}\"".format(song['filename'])
    call_result = subprocess.call(command, shell=True)
    print "Finished playing", s['url']
    return call_result


def keep_downloading_songs(api_root):
    while True:
        need_download = filter(lambda s: s['filename'] is None, songs.values())
        if len(need_download) == 0:
            time.sleep(1)
            continue
        song = need_download[0]
        download_status = download_song(song)
        if download_status != 0:
            delete_remote_song(api_root, song)
            songs.pop(song['uid'])
            continue


def keep_playing_songs(api_root):
    while True:
        good_for_playing = filter(lambda s: s['filename'], songs.values())
        if len(good_for_playing) == 0:
            time.sleep(1)
            continue
        else:
            song = good_for_playing[0]
            play_result = play_song(song)
            delete_local_song(song)
            if play_result != 0:
                delete_remote_song(api_root, song)
            new_song = get_song(api_root)
            songs[new_song['uid']] = new_song


if __name__ == "__main__":
    api_root = sys.argv[1]
    music_loop = threading.Thread(target=keep_playing_songs, args=[api_root])
    download_loop = threading.Thread(
        target=keep_downloading_songs,
        args=[api_root]
    )
    initial_songs = [get_song(api_root) for _ in range(10)]
    for s in initial_songs:
        songs[s['uid']] = s
    music_loop.daemon = True
    music_loop.start()
    download_loop.daemon = True
    download_loop.start()
    while True:
        time.sleep(1)