import time
import sched
import tweepy
from decouple import config
import requests
import json
import os
import random
import re


def sendDiscordMessage(message, action):
    if action == 'error':
        url = config('DISCORD_WEBHOOK_ERROR')
    else:
        url = config('DISCORD_WEBHOOK_MAIN')
    Message = {
        "content": message
    }
    requests.post(url, data=Message)


def readData():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data


def setSong(data, gen=False):
    if gen:
        nextSong = random.choice(list(data.keys()))
        with open('currentSong.txt', 'w') as f:
            f.write("[POINTER]\n")
            regex = '\[(.*?)\]'
            songlyrics = data[nextSong].split('\n')
            for lyric in songlyrics:
                if lyric == '':
                    continue
                if not re.search(regex, lyric):
                    if lyric == songlyrics[-1]:
                        lyric_modified = lyric.replace('Embed', '')
                        digits = []
                        for c in lyric_modified:
                            if c.isdigit():
                                digits.append(c)
                        if len(digits) == 0:
                            f.write(f"{lyric_modified}")

                        else:
                            f.write(f"{lyric_modified[:-len(digits)]}")
                    else:
                        f.write(lyric+'\n')
        return nextSong

    else:
        with open('currentSong.txt', 'w') as f:
            f.write("[POINTER]\n")
            f.write(list(data.keys())[0])
        return list(data.keys())[0]


def getNextLyrics(data):
    if not os.path.exists('currentSong.txt'):
        setSong(data, gen=True)
    with open('currentSong.txt', 'r') as f:
        lyrics = f.read().split('\n')

    for i in range(len(lyrics)):
        if lyrics[i] == '[POINTER]':
            if i + 5 < len(lyrics):
                setPointer(i, i+5)
                lyrics = [i for i in lyrics if i]
                if len(lyrics) == 0:
                    return "-1"
                return lyrics[i+1:i+5]
            else:
                setSong(data, gen=True)
                lyrics = [i for i in lyrics if i]
                if len(lyrics) == 0:
                    return "-1"
                return lyrics[i+1:]


def setPointer(currentIndex, nextindex):
    with open('currentSong.txt', 'r') as f:
        lyrics = f.read().split('\n')
    with open('currentSong.txt', 'w') as f:
        for i in range(len(lyrics)):
            if i == currentIndex:
                continue
            if i == nextindex:
                f.write('[POINTER]\n')
            else:
                f.write(lyrics[i] + '\n')


###############
auth = tweepy.OAuthHandler(config('TWITTER_API_KEY'),
                           config("TWITTER_API_SECRET"))
auth.set_access_token(config("TWITTER_ACCESS_TOKEN"),
                      config("TWITTER_ACCESS_TOKEN_SECRET"))

# Create API object
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

s = sched.scheduler(time.time, time.sleep)


def sendTweet(sc, api):
    sendDiscordMessage('Starting the process...', 'main')
    try:
        originalData = readData()
        nextLyrics = getNextLyrics(originalData)
        if nextLyrics == '-1':
            sendDiscordMessage('No lyrics found!', 'error')

        nextLyrics = [s + '\n' for s in nextLyrics]
        if len(nextLyrics) == 0:
            sendDiscordMessage('No lyrics found!', 'error')
        sendDiscordMessage('Sending Tweet', 'main')
        api.update_status(''.join(nextLyrics))
    except Exception as e:
        sendDiscordMessage(
            f'Error sending tweet, "ErrorType : {type(e).__name__}, Error : {e}"', 'error')
    sc.enter(5, 1, sendTweet, (sc, api,))


s.enter(5, 1, sendTweet, (s, api,))
s.run()
