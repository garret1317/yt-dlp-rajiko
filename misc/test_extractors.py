#!/usr/bin/env python3

# programmes expire, so i have to update the times in the tests every time i run them
# but thats a massive ballache, so i end up just not running them, which leads to cockups
# so, this script has the tests automatically use the latest episode as you run it, by setting dynamically generated time values
# everything else is always the same so it should be fine lol


import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, "/home/g/Downloads/yt-dlp/")  # TODO: un-hardcode. has to be the source/git repo because pip doesnt carry the tests

from yt_dlp_plugins.extractor import radiko_time as rtime
from yt_dlp_plugins.extractor.radiko import RadikoTimeFreeIE


MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
weekdays = {0: "MON", 1: "TUE", 2: "WED", 3: "THU", 4: "FRI", 5: "SAT", 6: "SUN"}

now = rtime.RadikoTime.now(tz = rtime.JST)
UTC = datetime.timezone.utc

def get_latest_airtimes(now, weekday, hour, minute, duration):
	days_after_weekday = (7 - (now.weekday() - weekday)) % 7
	latest_airdate = (now + datetime.timedelta(days=days_after_weekday)).replace(hour=hour, minute=minute, second=0, microsecond=0)
	if (latest_airdate + duration) > now:
		latest_airdate -= datetime.timedelta(days=7)
	return latest_airdate, latest_airdate + duration

def get_test_timefields(airtime, release_time):
	return {
		"timestamp": airtime.timestamp(),
		"release_timestamp": release_time.timestamp(),
		"upload_date": airtime.astimezone(UTC).strftime("%Y%m%d"),
		"release_date": release_time.astimezone(UTC).strftime("%Y%m%d"),

		"duration": (release_time - airtime).total_seconds(),
	}





RadikoTimeFreeIE._TESTS = []

# TOKYO MOON - interfm - EVERY FRI 2300
airtime, release_time = get_latest_airtimes(now, FRI, 23, 0, datetime.timedelta(hours=1))
RadikoTimeFreeIE._TESTS.append({
	"url": f"https://radiko.jp/#!/ts/INT/{airtime.timestring()}",
	"info_dict": {
		"ext": "m4a",
		"id": f"INT-{airtime.timestring()}",

		**get_test_timefields(airtime, release_time),

		'title': 'TOKYO MOON',
		'description': 'md5:4185349a530cfc4d0580e6996a511273',
		'uploader': 'interfm',
		'uploader_id': 'INT',
		'uploader_url': 'https://www.interfm.co.jp/',
		'channel': 'interfm',
		'channel_id': 'INT',
		'channel_url': 'https://www.interfm.co.jp/',
		'thumbnail': 'https://program-static.cf.radiko.jp/ehwtw6mcvy.jpg',
		'chapters': list,
		'tags': ['松浦俊夫', 'ジャズの魅力を楽しめる'],
		'cast': ['松浦\u3000俊夫'],
		'series': 'Tokyo Moon',
		'live_status': 'was_live',
	}
})






IEs = [RadikoTimeFreeIE]

import test.helper as th

# override to only get testcases from our IEs

def _new_gettestcases(include_onlymatching=False):
	import yt_dlp.plugins as plugins
	plugins.load_all_plugins()

	for ie in IEs:
		yield from ie.get_testcases(include_onlymatching)

def _new_getwebpagetestcases():
	import yt_dlp.plugins as plugins
	plugins.load_all_plugins()

	for ie in IEs:
		for tc in ie.get_webpage_testcases():
			tc.setdefault('add_ie', []).append('Generic')
			yield tc

th.gettestcases = _new_gettestcases
th.getwebpagetestcases = _new_getwebpagetestcases

import test.test_download as td

class TestDownload(td.TestDownload):
	pass

if __name__ == "__main__":
	unittest.main()
