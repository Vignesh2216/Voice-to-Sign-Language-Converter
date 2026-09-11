import fetchLink
from pytube import YouTube
from conf import SAMPLE_INPUTS, SAMPLE_OUTPUTS, SAMPLES
from moviepy import VideoFileClip, concatenate_videoclips
import os
import re
import wget
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
os.chdir(SAMPLE_INPUTS)

def downloader(word):
    word = list(word.split(" "))
    print("[ytdownload.downloader] words:", word)
    for w in word:
        print("[ytdownload.downloader] processing word:", w)
        # Fast path: if the word is purely alphabetic (like 'hello'),
        # build it from per-letter clips without doing web lookups.
        if re.match(r'^[A-Za-z]+$', w):
            clips = []
            for l in w:
                filename = l + ".mp4"
                filepath = os.path.join("alphabets", filename)
                clip = VideoFileClip(filepath)
                print("[ytdownload.downloader] letter clip:", l, "duration:", clip.duration)
                clips.append(clip)
            clip = concatenate_videoclips(clips, method='compose')
            os.chdir(SAMPLE_INPUTS)
            filename = w + ".mp4"
            print("[ytdownload.downloader] writing word clip:", filename, "duration:", clip.duration)
            clip.write_videofile(filename)
            print("[ytdownload.downloader] finished word clip:", filename)
            continue

        link = fetchLink.getLink(w)
        print("**********", link, "***********")
        if link == 0:
            clips = []
            for l in w:
                filename = l + ".mp4"
                filepath = os.path.join("alphabets", filename)
                print(filepath)
                clip = VideoFileClip(filepath)
                print("[ytdownload.downloader] letter clip:", l, "duration:", clip.duration)
                clips.append(clip)
            clip = concatenate_videoclips(clips, method='compose')
            os.chdir(SAMPLE_INPUTS)
            filename = w + ".mp4"
            print("[ytdownload.downloader] writing fallback word clip:", filename, "duration:", clip.duration)
            clip.write_videofile(filename)
            print("[ytdownload.downloader] finished fallback word clip:", filename)

        elif re.match(r'^(https?://)?(www\.youtube\.com|youtu\.?be)/.+$', link):
            print("[ytdownload.downloader] downloading youtube video for:", w)
            clip = YouTube(link)
            clip.streams.first().download()
            print("[ytdownload.downloader] finished youtube download for:", w)
        else:
            print("[ytdownload.downloader] downloading direct video for:", w)
            wget.download(link, out=SAMPLE_INPUTS)
            print("[ytdownload.downloader] finished direct download for:", w)
