#!/usr/bin/env python3
# monitor stream APIs for any changes, so I can check they don't break anything
# run via cronjob every now and then

import difflib
import os
import sys
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

for device in devices:
	for station in stations:
		url = STREAMS_API.format(device=device, station=station)
		now = s.get(url).text

		filename = f"{PATH}{station}-{device}.xml"
		with open(filename, "a+") as f:
			f.seek(0)
			past = f.read()

			modtime = datetime.fromtimestamp(os.path.getmtime(filename))
			diff = difflib.unified_diff(
				past.splitlines(), now.splitlines(),
				fromfile=url, tofile=url,
				fromfiledate=str(modtime), tofiledate=str(datetime.now()),
			)

			diff_str = "\n".join(diff)
			if diff_str != "":
				f.truncate(0)
				f.write(now)

				s.post(DISCORD_WEBHOOK, json={
					"embeds": [{
						"type": "rich",
						"title": f"Streams changed: {station} {device}",
						"description": "\n".join(("```diff", diff_str, "```"))
					}]
				})
