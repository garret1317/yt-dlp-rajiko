This repository contains a plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme).
See [yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#plugins) for more details.

# yt-dlp-rajiko

This plugin adds an improved [radiko](https://radiko.jp) extractor to yt-dlp.

It bypasses the region blocks entirely, meaning you can download programmes and listen to stations from any prefecture, even from outside Japan.

It provides more metadata for timefree programmes, and less for live station streams (it's a station that happens to be playing a programme at that point in time, not a programme itself).

You should use `-N` (multi-threaded download) for timefree, otherwise it'll be extremely slow.

Tracklists can be embedded as chapters for timefree programmes. The accuracy of the timestamps varies - it depends on what the stations provide. The duration/end time of the song is not provided at all, so you may get very long chapters if there's a big gap between songs.

You can download multiple programmes in one go by downloading the search pages.
For example, to download all available episodes of JET STREAM on Tokyo FM, [search for jet stream and set 地域 to 東京](https://radiko.jp/#!/search/live?key=jet%20stream&area_id=JP13&cul_area_id=JP13&page_idx=0). yt-dlp the url, and it'll download every result.

----

The authentication code is based heavily on [the work of jackyzy823](https://github.com/jackyzy823/rajiko/), which is where the name of the plugin comes from.
It also borrows bits from [Lesmiscore's extractor](https://github.com/yt-dlp/yt-dlp/blob/d1795f4a6af99c976c9d3ea2dabe5cf4f8965d3c/yt_dlp/extractor/radiko.py) from yt-dlp proper.

I've been advised that it would be risky to merge this extractor into yt-dlp proper as it uses a key reverse-engineered from the mobile app, so it's a plugin instead.

If you prefer not to take the risk, the `pc_html5` "law abiding citizen mode" branch uses the website's key, the same as in yt-dlp (in fact, the key-grabbing code is copied directly from lesmiscore's extractor). Premium accounts are not supported at this time.

## Installation

Requires yt-dlp `2023.01.02` or above.

You can install this package with pip:
```
python3 -m pip install -U https://github.com/garret1317/yt-dlp-rajiko/archive/master.zip
```
but you probably shouldn't, i'm not nearly religious enough about updating the version number

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the other methods this plugin package can be installed.

----

すみません、日本語はまだあまり上手ではありません。だから、このREADMEは英語で書きました。
