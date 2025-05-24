# yt-dlp-rajiko

yt-dlp-rajiko is an improved [radiko.jp](https://radiko.jp) extractor plugin for yt-dlp.

[日本語訳はこちら](https://427738.xyz/yt-dlp-rajiko/index.ja.html)

## Installation

[Download the Python wheel](https://427738.xyz/yt-dlp-rajiko/dl/yt_dlp_rajiko-latest.whl) or `pip install
--extra-index-url https://427738.xyz/yt-dlp-rajiko/pip/ yt-dlp-rajiko`

Requires yt-dlp 2025.02.19 or above.

Use the pip command if you installed yt-dlp with pip. If you installed
yt-dlp with `pipx`, use `pipx inject --index-url
https://427738.xyz/yt-dlp-rajiko/pip/ yt-dlp yt-dlp-rajiko` to install
the plugin in yt-dlp's environment.

Otherwise, download the wheel, and place it in one of these locations:

  - `~/.config/yt-dlp/plugins/` (on Linux and Mac)
  - `%appdata%/yt-dlp/plugins/` (on Windows)
  - anywhere else listed in [the yt-dlp
    documentation](https://github.com/yt-dlp/yt-dlp#installing-plugins).

You'll have to create those folders if they don't already exist.

More information about yt-dlp plugins is available from [yt-dlp's documentation](https://github.com/yt-dlp/yt-dlp#plugins).

## Usage

simply:
```
# timefree download
yt-dlp 'https://radiko.jp/#!/ts/INT/20240308230000'
# live recording
yt-dlp 'https://radiko.jp/#!/live/CCL'
# live shorthand
yt-dlp 'https://radiko.jp/#FMT'
```

You can semi-automatically grab the latest episodes of programmes by using the search page, like this:
```
# single-station programme yt-dlp
'https://radiko.jp/#!/search/live?key=World Jazz Warehouse&filter=past'
# area filtering also works
yt-dlp 'https://radiko.jp/#!/search/live?key=tokyo speakeasy&filter=past&area_id=JP13'
```
(though of course you still need to be there to press the button)

If you can reliably get it in the search, you can somewhat-automate downloading it.
If there's a programme that airs on multiple stations, the best way to filter down to the station you want is to use the search's 地域 (region) filter.

You can also get programmes that a person has appeared in, using the links from those little boxes on the side:
`yt-dlp 'https://radiko.jp/persons/3363'`

you can limit it to the "key station" only, like so:
`yt-dlp 'https://radiko.jp/persons/33635' --extractor-args rajiko:key-station-only`

This is meant as an alternative to the region filter, for networked programmes where the same thing airs on multiple stations.
Currently /persons/ URLs are the only place where that option works, as the information just isn't available for normal search results.

As a general rule, just copying from the browser URL bar should work with no changes. (if it doesn't, [let me know!](https://github.com/garret1317/yt-dlp-rajiko/issues))

(Apparently on Windows it won't work unless you use "double quotes", but on Linux it won't work unless you use 'single quotes'. If the command doesnt work with one quote type then try the other.)

**[You can find more usage tips on the website](https://427738.xyz/yt-dlp-rajiko/)**

## notes about this repository

this is just where the source code and bug tracker live. most of the info is on the website.

Generally you should use the release versions.
`master` branch usually works, but should be considered experimental and may have bugs
