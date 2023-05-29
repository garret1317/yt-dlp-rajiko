This repository contains a plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme).
See [yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#plugins) for more details.

# ytdlp-rajiko

This plugin adds an improved [radiko](https://radiko.jp) extractor to yt-dlp.

It bypasses the region blocks entirely, meaning you can download programmes and listen to stations from any prefecture, even from outside Japan.
It provides more metadata for timefree programmes, and less for live station streams (it's a station that happens to be playing a programme at that point in time, not a programme itself).

The authentication code is based heavily on [the work of jackyzy823](https://github.com/jackyzy823/rajiko/).

I've been advised that it would be risky to merge it into yt-dlp proper as it uses a key reverse-engineered from the mobile app, so it's a plugin instead.

## Installation

Requires yt-dlp `2023.01.02` or above.

You can install this package with pip:
```
python3 -m pip install -U https://github.com/garret1317/yt-dlp-rajiko/archive/master.zip
```
but you probably shouldn't, i'm not nearly religious enough about updating the version number

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the other methods this plugin package can be installed.
