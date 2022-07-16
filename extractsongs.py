from lyricsgenius import Genius
from decouple import config
import json
genius = Genius(config('GENIUS_TOKEN'))
artist = genius.search_artist(config('SONG_AUTHOR'), max_songs=3)
data = {}
for song in artist.songs:
    data[song.title] = song.lyrics
with open('data.json', 'w') as outfile:
    json.dump(data, outfile)