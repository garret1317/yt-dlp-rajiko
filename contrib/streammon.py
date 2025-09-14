#!/usr/bin/env python3
# monitor stream APIs for any changes, so I can check they don't break anything
# run via cronjob every now and then

import difflib
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

s = requests.Session()

DISCORD_WEBHOOK = "PUT WEBHOOK HERE"
STREAMS_API = "https://radiko.jp/v3/station/stream/{device}/{station}.xml"

if len(sys.argv) > 1:
	PATH = sys.argv[1]
else:
	PATH = ""

devices = ('pc_html5', 'aSmartPhone7a', 'aSmartPhone8')
stations = ('FMT', 'CCL', 'NORTHWAVE', 'TBS')

def format_xml(txt):
	root = ET.fromstring(txt)
	res = ""
	for el in root.findall("url"):
		res += el.find("playlist_create_url").text
		for k, v in el.attrib.items():
			res += f" {k}:{v}"

		res += "\n"
	return res

for device in devices:
	for station in stations:
		url = STREAMS_API.format(device=device, station=station)
		now_response = s.get(url)
		now = now_response.text
		now_modified = now_response.headers["last-modified"]
		now_datetime = datetime.strptime(now_modified, "%a, %d %b %Y %H:%M:%S %Z")


		filename = f"{PATH}{station}-{device}.xml"
		with open(filename, "a+") as f:
			f.seek(0)
			past = f.read()

			modtime = datetime.fromtimestamp(os.path.getmtime(filename))
			diff = difflib.unified_diff(
				format_xml(past).splitlines(), format_xml(now).splitlines(),
				fromfile=url, tofile=url,
				fromfiledate=str(modtime), tofiledate=str(now_datetime.now()),
			)

			diff_str = "\n".join(diff)
			if diff_str != "":
				f.truncate(0)
				f.write(now)

				s.post(DISCORD_WEBHOOK, json={
					"content": f"**Streams changed: {station} {device}**\n" + "\n".join(("```diff", diff_str, "```")),
				})
		os.utime(filename, (now_datetime.timestamp(), now_datetime.timestamp()))
