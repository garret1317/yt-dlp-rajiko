This repository contains a plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme).
See [yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#plugins) for more details.

# yt-dlp-rajiko

This plugin adds an improved [radiko](https://radiko.jp) extractor to yt-dlp.

It bypasses radiko's geo-block using the same technique as the [rajiko](https://github.com/jackyzy823/rajiko/) browser extension by jackyzy823 (from which this plugin gets its name). You can read their write-up (in Chinese) [here](https://jackyzy823.github.io/tech/battle-with-radiko.html).

More metadata is extracted for timefree programmes, including tracklists (as chapters).
Only the station metadata is extracted for live streams, not the programme that's airing at the time.

You should use `-N` (multi-threaded download) to increase download speed for timefree programmes.

You can somewhat automate downloading programmes by using the search page.
For instance, if I wanted all episodes of JET STREAM from K-MIX, i'd search for `jet stream` with the region set to Shizuoka (`JP22`). I'd also filter for just timefree, to avoid needlessly extracting yet-to-air programmes.

Personally, I have a shell script with a load of search URLs that are piped to yt-dlp. I run this script when I want to download new episodes of the programmes I listen to.

An effort is made to support share links and radiko embeds. However, I don't use these features often myself, so they don't recieve regular testing. Issues are welcome.

This extractor uses an API key obtained by reverse-engineering the radiko mobile app. As such, I've been advised that it would be risky to merge it into yt-dlp proper.

## Installation

Requires yt-dlp `2023.01.02` or above.

You can install this package with pip:
```
python3 -m pip install -U https://github.com/garret1317/yt-dlp-rajiko/archive/master.zip
```
but i don't update the version number ever, so i'm not sure how well that'll work when you need to update

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for the other methods this plugin package can be installed.


## Acknowledgements


The mobile spoofing code is based heavily on the [rajiko](https://github.com/jackyzy823/rajiko/) browser extension by jackyzy823, released under the Unlicense.
In particular, the fake phone details and GPS coordinate generation code was copied almost verbatim, with just a few changes for python syntax.
And of course, the mobile API key itself, without which this extractor would not have been possible, was originally obtained by jackyzy823.

The authentication code, and some parts of the metadata extraction, were adapted from [yt-dlp's radiko extractor](https://github.com/yt-dlp/yt-dlp/blob/d1795f4a6af99c976c9d3ea2dabe5cf4f8965d3c/yt_dlp/extractor/radiko.py), which was primarily authored by Lesmiscore (also released under the Unlicense).

----

すみません、日本語はまだあまり上手ではありません。だから、このREADMEは英語で書きました。
