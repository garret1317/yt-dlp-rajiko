#!/usr/bin/env python3
import unittest

from yt_dlp_plugins.extractor import radiko
from yt_dlp import YoutubeDL


ie = radiko._RadikoBaseIE()
ydl = YoutubeDL(auto_init=False)
ie.set_downloader(ydl)

info = ie._generate_random_info()
print("random device info")
print(info)
