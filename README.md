
<div align="right">
  <details>
    <summary >🌐 Language</summary>
    <div>
      <div align="center">
        <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=en">English</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=zh-CN">简体中文</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=zh-TW">繁體中文</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=ja">日本語</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=ko">한국어</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=hi">हिन्दी</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=th">ไทย</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=fr">Français</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=de">Deutsch</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=es">Español</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=it">Italiano</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=ru">Русский</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=pt">Português</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=nl">Nederlands</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=pl">Polski</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=ar">العربية</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=fa">فارسی</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=tr">Türkçe</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=vi">Tiếng Việt</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=id">Bahasa Indonesia</a>
        | <a href="https://openaitx.github.io/view.html?user=garret1317&project=yt-dlp-rajiko&lang=as">অসমীয়া</
      </div>
    </div>
  </details>
</div>

# yt-dlp-rajiko

improved [radiko.jp](https://radiko.jp) extractor plugin for yt-dlp (fast and areafree)

<p>yt-dlp-rajiko lets you download Japanese radio shows from <a href="https://radiko.jp">radiko.jp</a> without a VPN, using <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a>.
It downloads quickly, and works for any participating station*, from anywhere in the world.<br>
<small>*except NHK, but they have <a href="https://www.nhk.or.jp/radio/">their own site</a> which is supported
in yt-dlp proper</small></p>


<p>Intended for personal archiving, not for commercial use. Please subscribe to radiko Premium if you are able.<br>
<small>(It's Free Software, so this is just me asking nicely, not a hard requirement. but you should do it so that radiko can keep existing)<br>
(also, if you get the timefree30 plan you can use it with yt-dlp :P)
</small></p>

### [日本語  🇯🇵](https://427738.xyz/yt-dlp-rajiko/index.ja.html)

## Installation

[Download the plugin bundle](https://427738.xyz/yt-dlp-rajiko/dl/yt_dlp_rajiko-latest.bundle.zip) or `pip install yt-dlp-rajiko`

<p>Requires yt-dlp 2025.02.19 or newer.</p>

<p>If you installed yt-dlp with pip, use the pip command above.
If you installed yt-dlp with <code>pipx</code>,
use <code>pipx inject yt-dlp yt-dlp-rajiko</code> to install the plugin in yt-dlp's environment.</p>

<p>If you installed with the .exe/binary or any other method,
download the bundle and place it in one of these locations: </p>

<ul>
	<li><code>%appdata%\yt-dlp\plugins\</code> (on Windows)</li>
	<li><code>~/.config/yt-dlp/plugins/</code> (on Linux and Mac)</li>
	<li>a <code>yt-dlp-plugins</code> folder next to your <code>yt-dlp.exe</code> <a href="https://427738.xyz/yt-dlp-rajiko/i/installation-pluginsfolder2.png">(like this)</a><br>
	<li>anywhere else listed in <a href="https://github.com/yt-dlp/yt-dlp#installing-plugins">the yt-dlp documentation</a>.</li>
</ul>

<p>You'll have to create those folders if they don't already exist.<br>
<b>There is no need to extract the zip file.</b></p>

<p>You can check you've installed correctly by running <code>yt-dlp -v</code> and looking for the <code>[debug] Extractor Plugins:</code> or <code>[debug] Plugin directories:</code> lines. <a href="https://427738.xyz/yt-dlp-rajiko/i/plugincheck.png">(like this)</a>
</p>

More information about yt-dlp plugins is available from [yt-dlp's documentation](https://github.com/yt-dlp/yt-dlp#plugins).

## More info

[Please see the website for more information](https://427738.xyz/yt-dlp-rajiko/) (usage, contact methods, etc)

[日本語訳もあります](https://427738.xyz/yt-dlp-rajiko/index.ja.html)

## about this repository

this is just where the source code and bug tracker live. most of the info is on the website.

Generally you should use the release versions.
`master` branch usually works, but should be considered experimental and may have bugs
