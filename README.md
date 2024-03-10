This repository contains a plugin package for [yt-dlp](https://github.com/yt-dlp/yt-dlp#readme).
See [yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#plugins) for more details.

# yt-dlp-rajiko

yt-dlp-rajiko is an improved [radiko](https://radiko.jp) extractor for yt-dlp.

It bypasses radiko's geo-block by impersonating the mobile app.
This the same technique as the [rajiko](https://github.com/jackyzy823/rajiko/) browser extension by jackyzy823 (from which this plugin takes its name).

Timefree programmes have more better metadata, including tracklists (as chapters).
Only the station metadata is extracted for the live streams, not the programme that's airing at the time.

Some effort is made to support share links and radiko embeds, but they don't recieve regular testing/[dogfooding](https://en.wikipedia.org/wiki/Eating_your_own_dog_food).

If you find a problem or have a question, please open a github issue.

yt-dlp-rajikoはyt-dlpで、radiko(ラジコ)の生配信とタイムフリー番組をダウンロードできるyt-dlpプラギンです。

スマホアプリをなりすまして、地域制限が完全にバイパスできます。 この方法は[jackyzy823の「rajiko」というブラウザ拡張機能](https://github.com/jackyzy823/rajiko)と同じです。
jackyzy823の中国語での記事は[こちら](https://jackyzy823.github.io/tech/battle-with-radiko.html)で読める。

もし問題や質問があれば、イシューを提出してください。
申し訳ありませんが、私には日本語が難しいので、できれば、イシューは英語で書いてください。

## Installation

Requires yt-dlp `2023.06.22` or above.

You can install this package with pip:
```
python3 -m pip install -U https://github.com/garret1317/yt-dlp-rajiko/archive/master.zip
```
but i don't update the version number ever, so i'm not sure how well that'll work when updates happen.

See [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) for other ways this plugin package can be installed.

## Usage

simply
```sh
# timefree download
yt-dlp 'https://radiko.jp/#!/ts/INT/20240308230000'
# live recording
yt-dlp 'https://radiko.jp/#!/live/RN1'
```

**Pro Tip:** You should use `-N` (multi-threaded download) to increase download speed.

You can somewhat automate downloading programmes by using the search page.

```sh
# all programmes related to 角松敏生
yt-dlp 'https://radiko.jp/#!/search/live?key=角松敏生&filter=past&start_day=&end_day=&region_id=all&area_id=JP26&cul_area_id=JP26&page_idx=0'
# specific programme, limited to certain region
yt-dlp 'https://radiko.jp/#!/search/live?key=world%20jazz%20warehouse&filter=past&start_day=&end_day=&region_id=&area_id=JP27&cul_area_id=JP27&page_idx=0'
```
Those example URLs were directly copied from the browser URL bar.

If you can reliably get it in the search, you can somewhat-automate downloading it.
If there's a programme that airs on multiple stations, the best way to filter down to the station you want is to use the search's `地域` (region) filter.

I recommend:

- filtering for `タイムフリー` (timefree), so you don't get episodes that haven't aired yet.
- using a download archive
- `--playlist-reverse` - the search is ordered oldest-first, so reverse it to get newest first
	- `--break-on-existing` (with `--break-per-input`) - and then you can stop once you've got the latest, skipping older episodes you've already got

to avoid scraping any more than necessary. (faster for you, less load on radiko, everyone wins)

Once you've written your command, you can put it into a shell/batch/etc script, so you can run it after the programme(s) you're interested in have aired.

## Extractor args

You can choose which device's streams to extract with the `device` extractor arg.
For instance, `--extractor-args radikotimefree:device=pc_html5` would extract the streams the website uses.

There is no benefit to using this. It only exists to make development/investigation easier.

Known devices:

- `pc_html5` - the website. has every stream provider.
- `aSmartPhone5`, `aSmartPhone6`, `aSmartPhone6a`, `aSmartPhone7a`, `aSmartPhone7`, `pc_1` - old mobile apps, + old website. the "happy path".
- `MobileWebTrial` - current mobile site.
- `aSmartPhone8` - current mobile app.
- `xExternalWebStations` - embedded players on stations' websites. same streams as `aSmartPhone8`, though the api response isn't exactly the same.

The default is `aSmartPhone7a` as its streams are always the "happy path".

## Acknowledgements


The mobile spoofing code is based heavily on the [rajiko](https://github.com/jackyzy823/rajiko/) browser extension by jackyzy823, released under the Unlicense.
In particular, the fake phone details and GPS coordinate generation code have been copied almost verbatim.
And of course, the mobile API key was (to the best of my knowledge) originally obtained by jackyzy823. You can read their write-up (in Chinese) [here](https://jackyzy823.github.io/tech/battle-with-radiko.html).

The authentication code, and some parts of the metadata extraction, have been adapted from [yt-dlp's radiko extractor](https://github.com/yt-dlp/yt-dlp/blob/d1795f4a6af99c976c9d3ea2dabe5cf4f8965d3c/yt_dlp/extractor/radiko.py), which was primarily authored by Lesmiscore (also released under the Unlicense).

This extractor uses an API key obtained by reverse-engineering the radiko mobile app. As such, I've been advised that it would be risky to merge it into yt-dlp proper.
