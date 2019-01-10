import os
import urllib.request
import vlc
import youtube_dl
from bs4 import BeautifulSoup
from lxml import etree
from random import choice


def pick_random_song():
    """Play a random song mode

    Could be useful if you want to give the user the option
    to not download anything but play something that is already there.
    """
    song_list = []
    for root, dirs, files in os.walk("./songs"):  
        for filename in files:
            if filename[-5:] == ".opus":
                song_list.append(filename)
    temp = choice(song_list)
    return temp


def which_song(plus_one=False):
    """Keep songs in order

    We numerate new songs 1.opus ,2.opus, .. here we create the next name.
    We do this so that VLC knows which song to play and so that we can find
    out easily which song has been downloaded most recent.
    """
    sep = ".opus"
    song_list = []
    max = 0
    for root, dirs, files in os.walk("./songs"):  
        for filename in files:
            if filename[-5:] == sep:
                temp = filename.split(sep, 1)[0]
                if temp.isdigit():
                    if int(temp) > max:
                        max = int(temp)
    if plus_one:
        return str(max+1) + ".opus"
    else:
        return str(max) + ".opus"


def get_title(url_list):
    """Gets video titles from Youtube URLs

    Pretty neat isn't it.
    """
    with urllib.request.urlopen(url_list) as url:
        youtube = etree.HTML(url.read())
    video_title = youtube.xpath("//span[@id='eow-title']/@title")
    return "".join(video_title)


def get_url_list(user_input):
    """Get YouTube results

    We basically open youtube and input whatever the user wants to input.
    Then we return the first page of results that Youtube gives us.
    """
    textToSearch = user_input
    query = urllib.parse.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        url_list.append('https://www.youtube.com' + vid['href'])
    for index, i in enumerate(url_list, start=1):
        print(str(index) + ": " + get_title(i))


url_list = []
next_song = which_song(True)
param = "./songs/"+ next_song
user_input = input("Which song do you want to stream: ")
get_url_list(user_input)
# never trust user input
while True:
    user_pick = input("\nPlease enter the number of the song you want to play: ")
    if user_pick.isdigit():
        user_pick = int(user_pick)
        if 1 <= user_pick <= 20:
            break
        else:
            print("Not a valid option.")
    else:
        print("Please enter the NUMBER of the song you want to listen to.")
url = url_list[user_pick-1]
ydl_opts = {'format': 'bestaudio/best',
            'outtmpl': param,
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '192',}],}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

# play newest song in vlc
song_name = which_song()
play_this = "./songs/" + song_name
player = vlc.MediaPlayer(play_this)
player.play()
