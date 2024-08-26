# yt-dlp-rajiko

yt-dlp-rajiko is an improved [radiko.jp](https://radiko.jp) extractor plugin for yt-dlp.

## Installation

[Download the Python wheel](https://427738.xyz/yt-dlp-rajiko/dl/yt_dlp_rajiko-latest.whl) or `pip install
--extra-index-url https://427738.xyz/yt-dlp-rajiko/pip/ yt-dlp-rajiko`

Requires yt-dlp 2023.06.22 or above.

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

    # timefree download
    yt-dlp 'https://radiko.jp/#!/ts/INT/20240308230000'
    # live recording
    yt-dlp 'https://radiko.jp/#!/live/CCL'
    # live shorthand
    yt-dlp 'https://radiko.jp/#FMT'

You can somewhat automate downloading programmes by using the search
page.

    # all programmes related to Toshiki Kadomatsu
    yt-dlp 'https://radiko.jp/#!/search/live?key=角松敏生&filter=past&region_id=all'
    # specific programme from Osaka
    yt-dlp 'https://radiko.jp/#!/search/live?key=world%20jazz%20warehouse&filter=past&area_id=JP27'

Just copying from the browser URL bar should work with no changes.

----

[Please see the website for more information](https://427738.xyz/yt-dlp-rajiko/).
If the website is down, an archived copy may be available on [the Internet Archive's Wayback Machine](https://web.archive.org/web/*/https://427738.xyz/yt-dlp-rajiko/).

[日本語訳は公式サイトをご覧ください。](https://427738.xyz/yt-dlp-rajiko/index.ja.html)
サイトが無くなった場合は、多分[Internet ArchiveのWayback Machineにアーカイブされています](https://web.archive.org/web/*/https://427738.xyz/yt-dlp-rajiko/index.ja.html)。
