#!/usr/bin/env python3
import datetime
import locale
import re

from xml.etree import ElementTree
from bs4 import BeautifulSoup

tree = ElementTree.parse("CHANGELOG.xml")
rss = tree.getroot()

latest = rss.find(".//item[last()]")

url = latest.find("link").text
ver = re.search(r"\d+\.\d+", url).group()

date = latest.find("pubDate").text

dt = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
locale.setlocale(locale.LC_TIME, "ja_JP.utf8")  # what could possibly go wrong
ja_date = dt.strftime("%x (%a) %H:%M:%S %z")

desc = latest.find("description").text

soup = BeautifulSoup(desc, 'html.parser')

en_notes = f"""<p><b>yt-dlp-rajiko v{ver} has been released</b></p>
{soup.find("div", lang="en").decode_contents()}"""

ja_notes = f"""<p><b>yt-dlp-rajiko v{ver} がリリースされました。</b></p>
{soup.find("div", lang="ja").decode_contents()}"""


def update_marker(page, marker, content):
	start_marker = f"<!--{marker} START-->"
	end_marker = f"<!--{marker} END-->"
	return re.sub(f"{start_marker}.+{end_marker}", f"{start_marker}{content}{end_marker}", page, flags=re.DOTALL)


for i in ["index.html", "index.ja.html"]:
	with open(i, "r+") as f:
		page = f.read()

		page = update_marker(page, "LATEST VERSION", f"v{ver}")

		page = update_marker(page, "EN RELEASE DATE", date)
		page = update_marker(page, "JA RELEASE DATE", ja_date)

		page = update_marker(page, "EN RELEASENOTES", en_notes)
		page = update_marker(page, "JA RELEASENOTES", ja_notes)

		f.seek(0)
		f.truncate(0)
		f.write(page)
