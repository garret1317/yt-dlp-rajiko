This repository contains a plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme).
See [yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#plugins) for more details.

# ytdlp-rajiko

This plugin adds an improved [radiko](https://radiko.jp) extractor to yt-dlp.

It bypasses the region blocks entirely, meaning you can download programmes and listen to stations from any prefecture, even from outside Japan.

It provides more metadata for timefree programmes, and less for live station streams (it's a station that happens to be playing a programme at that point in time, not a programme itself).

You can also download from search pages. If, for example, you want to download all available episodes of JET STREAM on Tokyo FM, [search for jet stream and set 地域 to
東京](https://radiko.jp/#!/search/live?key=jet%20stream&filter=&start_day=&end_day=&region_id=&area_id=JP13&cul_area_id=JP13&page_idx=0). yt-dlp the url, and it'll download every result.

The authentication code is based heavily on [the work of jackyzy823](https://github.com/jackyzy823/rajiko/), which is where the name of the plugin comes from.
It also borrows bits from [Lesmiscore's extractor](https://github.com/yt-dlp/yt-dlp/blob/d1795f4a6af99c976c9d3ea2dabe5cf4f8965d3c/yt_dlp/extractor/radiko.py) from yt-dlp proper.

I've been advised that it would be risky to merge this extractor into yt-dlp proper as it uses a key reverse-engineered from the mobile app, so it's a plugin instead.

## Installation

Requires yt-dlp `2023.01.02` or above.

You can install this package with pip:
```
python3 -m pip install -U https://github.com/garret1317/yt-dlp-rajiko/archive/master.zip
```
but you probably shouldn't, i'm not nearly religious enough about updating the version number

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the other methods this plugin package can be installed.

----

ごめんなさい、僕の日本語はまだあんまりうまくない。だから、このREADMEは英語を書いた。
