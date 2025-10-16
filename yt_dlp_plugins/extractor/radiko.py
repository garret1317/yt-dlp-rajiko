import base64
import datetime
import random
import urllib.parse
import json

import pkgutil

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.networking.exceptions import HTTPError
from yt_dlp.utils import (
	ExtractorError,
	OnDemandPagedList,
	clean_html,
	int_or_none,
	join_nonempty,
	parse_qs,
	traverse_obj,
	urlencode_postdata,
	url_or_none,
	update_url_query,
)
from yt_dlp_plugins.extractor.radiko_podcast import RadikoPodcastSearchIE

import yt_dlp_plugins.extractor.radiko_time as rtime
import yt_dlp_plugins.extractor.radiko_hacks as hacks


class _RadikoBaseIE(InfoExtractor):
	_FULL_KEY =  pkgutil.get_data(__name__, "radiko_aSmartPhone8.jpg")
	# https://stackoverflow.com/a/58941536

	_COORDINATES = {
		# source: https://github.com/jackyzy823/rajiko/blob/master/background.js
			# data source (capital of prefectures): https://www.benricho.org/chimei/latlng_data.html
			# data source : jp.radiko.Player.V6FragmentAreaCheck.freeloc_init
		"JP1":  [43.064615, 141.346807], "JP2":  [40.824308, 140.739998], "JP3":  [39.703619, 141.152684],
		"JP4":  [38.268837, 140.8721],   "JP5":  [39.718614, 140.102364], "JP6":  [38.240436, 140.363633],
		"JP7":  [37.750299, 140.467551], "JP8":  [36.341811, 140.446793], "JP9":  [36.565725, 139.883565],
		"JP10": [36.390668, 139.060406], "JP11": [35.856999, 139.648849], "JP12": [35.605057, 140.123306],
		"JP13": [35.689488, 139.691706], "JP14": [35.447507, 139.642345], "JP15": [37.902552, 139.023095],
		"JP16": [36.695291, 137.211338], "JP17": [36.594682, 136.625573], "JP18": [36.065178, 136.221527],
		"JP19": [35.664158, 138.568449], "JP20": [36.651299, 138.180956], "JP21": [35.391227, 136.722291],
		"JP22": [34.97712, 138.383084],  "JP23": [35.180188, 136.906565], "JP24": [34.730283, 136.508588],
		"JP25": [35.004531, 135.86859],  "JP26": [35.021247, 135.755597], "JP27": [34.686297, 135.519661],
		"JP28": [34.691269, 135.183071], "JP29": [34.685334, 135.832742], "JP30": [34.225987, 135.167509],
		"JP31": [35.503891, 134.237736], "JP32": [35.472295, 133.0505],   "JP33": [34.661751, 133.934406],
		"JP34": [34.39656, 132.459622],  "JP35": [34.185956, 131.470649], "JP36": [34.065718, 134.55936],
		"JP37": [34.340149, 134.043444], "JP38": [33.841624, 132.765681], "JP39": [33.559706, 133.531079],
		"JP40": [33.606576, 130.418297], "JP41": [33.249442, 130.299794], "JP42": [32.744839, 129.873756],
		"JP43": [32.789827, 130.741667], "JP44": [33.238172, 131.612619], "JP45": [31.911096, 131.423893],
		"JP46": [31.560146, 130.557978], "JP47": [26.2124, 127.680932],
	}
	# range detail :http://www.gsi.go.jp/KOKUJYOHO/CENTER/zenken.htm

	_APP_VERSIONS = ["8.1.11"]

	_DELIVERED_ONDEMAND = ('radiko.jp',)
	_DOESNT_WORK_WITH_FFMPEG = ('tf-f-rpaa-radiko.smartstream.ne.jp', 'si-f-radiko.smartstream.ne.jp', 'alliance-stream-radiko.smartstream.ne.jp')
	_AD_INSERTION = ('si-f-radiko.smartstream.ne.jp', )

	_has_tf30 = None

	def _index_regions(self):
		region_data = {}

		tree = self._download_xml("https://radiko.jp/v3/station/region/full.xml", None, note="Indexing station regions")
		for stations in tree:
			for station in stations:
				area = station.find("area_id").text
				station_id = station.find("id").text
				region_data[station_id] = area

		self.cache.store("rajiko", "region_index", region_data)
		return region_data

	def _get_coords(self, area_id):
		latlong = self._COORDINATES[area_id]
		lat = latlong[0]
		long = latlong[1]
		# +/- 0 ~ 0.025 --> 0 ~ 1.5' ->  +/-  0 ~ 2.77/2.13km
		lat = lat + random.random() / 40.0 * (random.choice([1, -1]))
		long = long + random.random() / 40.0 * (random.choice([1, -1]))
		return {"latitude": round(lat, 6), "longitude": round(long, 6)}

	def _get_station_region(self, station):
		regions = self.cache.load("rajiko", "region_index")
		if regions is None or station not in regions:
			self.write_debug(f"station {station} not found, re-indexing in case it's new")
			regions = self._index_regions()

		return regions[station]

	def _negotiate_token(self, station_region):
		ua_header = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Mobile Safari/537.36"}
		# it's hardcoded in the actual app so its ok to hardcode it here

		user_id = ''.join(random.choices('0123456789abcdef', k=32))
		auth1 = self._download_json("https://api.radiko.jp/apparea/auth1", None,
			"Authenticating: step 1", headers=ua_header, data=json.dumps({
				"app_id": "aSmartPhone8",
				"app_version": random.choice(self._APP_VERSIONS),
				"user_id": user_id,
				"device": "android",
			}).encode())

		token_info = auth1["auth_token_info"]

		key_length = auth1["key_length"]
		key_offset = auth1["key_offset"]
		self.write_debug(f"KeyLength: {key_length}")
		self.write_debug(f"KeyOffset: {key_offset}")

		raw_partial_key = self._FULL_KEY[key_offset:key_offset + key_length]
		partial_key = base64.b64encode(raw_partial_key).decode("ascii")
		self.write_debug(partial_key)

		coords = self._get_coords(station_region)
		self.write_debug(coords)

		auth2 = self._download_json("https://api.radiko.jp/apparea/auth2", station_region,
			"Authenticating: step 2", headers=ua_header, data=json.dumps({
				"auth_token": token_info["auth_token"],
				"partial_key": partial_key,
				"connection": random.choice(("wifi", "mobile",)),
				"location": coords,
			}).encode())

		self.write_debug(auth2)

		actual_regions = traverse_obj(auth2, ("areas", ..., "area_id"))

		region_mismatch = station_region not in actual_regions
		if region_mismatch:
			self.report_warning(f"Region mismatch: Expected {station_region}, got {actual_regions}. Coords: {coords}.")
			self.report_warning("Please report this at https://github.com/garret1317/yt-dlp-rajiko/issues")
			self.report_warning(auth2.strip())
			self.report_warning(auth2_headers)

		auth_info = {
			"headers": {
				"X-Radiko-AreaId": station_region if not region_mismatch else actual_region[0],  # i dont know if we ever get more than 1 region
				"X-Radiko-AuthToken": token_info["auth_token"],
			},
			"expiry": datetime.datetime.fromisoformat(token_info["expires_at"]).timestamp(),
			"user_id": user_id,
			"has_tf30": auth2.get("has_timefree_plus")
		}

		if not region_mismatch:
			self.cache.store("rajiko8", station_region, auth_info)
			self._has_tf30 = auth2.get("has_timefree_plus")
		return auth_info

	def _auth(self, station_region, need_tf30=False):
		cachedata = self.cache.load("rajiko8", station_region)
		self.write_debug(cachedata)
		if cachedata is not None:
			if need_tf30 and not cachedata.get("has_tf30"):
				self.write_debug("Cached token doesn't have timefree 30, getting a new one")
				return self._negotiate_token(station_region)
			if cachedata.get("expiry") <= datetime.datetime.now().timestamp():
				self.write_debug("Token has expired, getting a new one")
				return self._negotiate_token(station_region)

			auth_headers = cachedata.get("headers")
			response = self._download_webpage("https://radiko.jp/v2/api/auth_check", station_region, "Checking cached token",
				headers=auth_headers, expected_status=401)
			self.write_debug(response)
			if response == "OK":
				return cachedata
		return self._negotiate_token(station_region)

	def _get_station_meta(self, region, station_id):
		cachedata = self.cache.load("rajiko8", station_id)
		now = datetime.datetime.now()
		if cachedata is None or cachedata.get("expiry") < now.timestamp():
			region = self._download_xml(f"https://radiko.jp/v3/station/list/{region}.xml", station_id,
				note="Downloading station metadata")
			station = region.find(f'.//station/id[.="{station_id}"]/..')  # a <station> with an <id> of our station_id
			station_name = station.find("name").text
			station_url = url_or_none(station.find("href").text)

			thumbnails = []
			for logo in station.findall("logo"):
				thumbnails.append({
					"url": logo.text,
					**traverse_obj(logo.attrib, ({
						"width": ("width", {int_or_none}),
						"height": ("height", {int_or_none}),
					}))
				})

			meta = {
				"id": station_id,
				"title": station_name,
				"alt_title": station.find("ascii_name").text,

				"channel": station_name,
				"channel_id": station_id,
				"channel_url": station_url,

				"uploader": station_name,
				"uploader_id": station_id,
				"uploader_url": station_url,

				"thumbnails": thumbnails,
			}
			self.cache.store("rajiko", station_id, {
				"expiry": (now + datetime.timedelta(days=1)).timestamp(),
				"meta": meta
			})
			return meta

		self.to_screen(f"{station_id}: Using cached station metadata")
		return cachedata.get("meta")

	def _get_station_formats(self, station, timefree, auth_data, start_at=None, end_at=None, use_pc_html5=False):
		config_device = traverse_obj(self._configuration_arg('device', casesense=True, ie_key="rajiko"), 0)

		if not use_pc_html5:
			device = config_device or "aSmartPhone7a"  # still has the radiko.jp on-demand one for timefree
		else:
			device = config_device or "pc_html5" # the on-demand one doesnt work with timefree30 stuff sadly
			# so just use pc_html5 which has everything

		url_data = self._download_xml(f"https://radiko.jp/v3/station/stream/{device}/{station}.xml",
			station, note=f"Downloading {device} stream information")

		seen_urls = []
		formats = []

		timefree_int = 1 if timefree else 0
		do_blacklist_streams = not len(self._configuration_arg("no_stream_blacklist", ie_key="rajiko")) > 0
		do_as_live_chunks = not len(self._configuration_arg("no_as_live_chunks", ie_key="rajiko")) > 0
		for element in url_data.findall(f".//url[@timefree='{timefree_int}'][@areafree='0']/playlist_create_url"):
		# find <url>s with matching timefree and no areafree, then get their <playlist_create_url>
		# we don't want areafree here because we should always be in-region
			url = element.text
			if url in seen_urls:  # there are always dupes, even with ^ specific filtering
				continue

			seen_urls.append(url)
			playlist_url = update_url_query(url, {
					"station_id": station,
					"l": "15",  # l = length, ie how many seconds in the live m3u8 (max 300)
					"lsid": auth_data["user_id"],
					"type": "b",  # a/b = in-region, c = areafree
				})

			if timefree:
				playlist_url = update_url_query(playlist_url, {
					"start_at": start_at.timestring(),
					"ft": start_at.timestring(),

					"end_at": end_at.timestring(),
					"to": end_at.timestring(),
				})

			domain = urllib.parse.urlparse(playlist_url).netloc

			# defaults
			delivered_live = True
			preference = -1
			entry_protocol = 'm3u8'
			format_note=[]

			if timefree and domain in self._DOESNT_WORK_WITH_FFMPEG and do_blacklist_streams:
				# TODO: remove this completely
				# https://github.com/garret1317/yt-dlp-rajiko/issues/29
				self.write_debug(f"skipping {domain} (known not working)")
				continue
			if domain in self._DELIVERED_ONDEMAND:
				# override the defaults for delivered as on-demand
				delivered_live = False
				preference += 2
				entry_protocol = None
			if domain in self._AD_INSERTION:
				preference -= 3
				format_note.append("Ad insertion")


			auth_headers = auth_data["headers"]

			if delivered_live and timefree and do_as_live_chunks:

				chunks_playlist = hacks._generate_as_live_playlist(
					self, playlist_url, start_at, end_at, domain, auth_headers
				)

				m3u8_formats = [{
					"format_id": join_nonempty(domain, "chunked"),
					"hls_media_playlist_data": chunks_playlist,
					"preference": preference,
					"ext": "m4a",
					"vcodec": "none",

					# fallback to live for ffmpeg etc
					"url": playlist_url,
					"http_headers": auth_headers,
				}]
				format_note.append("Chunked")
			else:

				m3u8_formats = self._extract_m3u8_formats(
					playlist_url, station, m3u8_id=domain, fatal=False, headers=auth_headers,
					live=delivered_live, preference=preference, entry_protocol=entry_protocol,
					note=f"Downloading m3u8 information from {domain}")

			for f in m3u8_formats:
				# ffmpeg sends a Range header which some streams reject. here we disable that (and also some icecast header as well)
				f['downloader_options'] = {'ffmpeg_args': ['-seekable', '0', '-http_seekable', '0', '-icy', '0']}
				f['format_note'] = ", ".join(format_note)
				formats.append(f)

		return formats


class RadikoLiveIE(_RadikoBaseIE):
	_VALID_URL = [
		r"https?://(?:www\.)?radiko\.jp/#!/live/(?P<id>[A-Z0-9-_]+)",
		r"https?://(?:www\.)?radiko\.jp/#(?P<id>[A-Z0-9-_]+)"
	]
	_TESTS = [{
		# JP13 (Tokyo)
		"url": "https://radiko.jp/#!/live/FMT",
		"info_dict": {
			"ext": "m4a",
			"live_status": "is_live",

			"id": "FMT",
			"title": "re:^TOKYO FM.+$",
			"alt_title": "TOKYO FM",
			"thumbnail": "https://radiko.jp/v2/static/station/logo/FMT/lrtrim/688x160.png",

			"channel": "TOKYO FM",
			"channel_id": "FMT",
			"channel_url": "https://www.tfm.co.jp/",

			"uploader": "TOKYO FM",
			"uploader_id": "FMT",
			"uploader_url": "https://www.tfm.co.jp/",
		},
	}, {
		# JP1 (Hokkaido) - shorthand
		"url": "https://radiko.jp/#NORTHWAVE",
		"info_dict": {
			"ext": "m4a",
			"live_status": "is_live",

			"id": "NORTHWAVE",
			"title": "re:^FM NORTH WAVE.+$",
			"alt_title": "FM NORTH WAVE",
			"thumbnail": "https://radiko.jp/v2/static/station/logo/NORTHWAVE/lrtrim/688x160.png",

			"uploader": "FM NORTH WAVE",
			"uploader_url": "https://www.fmnorth.co.jp/",
			"uploader_id": "NORTHWAVE",

			"channel": "FM NORTH WAVE",
			"channel_url": "https://www.fmnorth.co.jp/",
			"channel_id": "NORTHWAVE",
		},
	}, {
		# ALL (all prefectures)
		# api still specifies a prefecture though, in this case JP13 (Tokyo), so that's what it auths as
		"url": "https://radiko.jp/#!/live/RN1",
		"info_dict": {
			"ext": "m4a",
			"live_status": "is_live",

			"id": "RN1",
			"title": "re:^ラジオNIKKEI第1.+$",
			"alt_title": "RADIONIKKEI",
			"thumbnail": "https://radiko.jp/v2/static/station/logo/RN1/lrtrim/688x160.png",

			"channel": "ラジオNIKKEI第1",
			"channel_url": "http://www.radionikkei.jp/",
			"channel_id": "RN1",

			"uploader": "ラジオNIKKEI第1",
			"uploader_url": "http://www.radionikkei.jp/",
			"uploader_id": "RN1",
		},
	}]

	def _real_extract(self, url):
		station = self._match_id(url)
		region = self._get_station_region(station)
		station_meta = self._get_station_meta(region, station)
		auth_data = self._auth(region)
		formats = self._get_station_formats(station, False, auth_data, use_pc_html5=True)

		return {
			"is_live": True,
			"id": station,
			**station_meta,
			"formats": formats,
		}


class RadikoTimeFreeIE(_RadikoBaseIE):
	_NETRC_MACHINE = "rajiko"
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/#!/ts/(?P<station>[A-Z0-9-_]+)/(?P<id>\d+)"
	# TESTS use a custom-ish script that updates the airdates automatically, see contrib/test_extractors.py

	def _perform_login(self, username, password):
		try:
			login_info = self._download_json('https://radiko.jp/ap/member/webapi/member/login', None, note='Logging in',
				data=urlencode_postdata({'mail': username, 'pass': password}))
			self._has_tf30 = '2' in login_info.get('privileges')
			# areafree = 1, timefree30 = 2, double plan = both
			self.write_debug({**login_info, "radiko_session": "PRIVATE", "member_ukey": "PRIVATE"})
		except ExtractorError as error:
			if isinstance(error.cause, HTTPError) and error.cause.status == 401:
				raise ExtractorError('Invalid username and/or password', expected=True)
			raise

	def _check_tf30(self):
		if self._has_tf30 is not None:
			return self._has_tf30
		if self._get_cookies('https://radiko.jp').get('radiko_session') is None:
			return
		account_info = self._download_json('https://radiko.jp/ap/member/webapi/v2/member/login/check',
			None, note='Checking account status from cookies', expected_status=400)
		self.write_debug({**account_info, "user_key": "PRIVATE"})
		self._has_tf30 = account_info.get('timefreeplus') == '1'
		return self._has_tf30

	def _get_programme_meta(self, station_id, url_time):
		day = url_time.broadcast_day_string()
		meta = self._download_json(f"https://api.radiko.jp/program/v4/date/{day}/station/{station_id}.json", station_id,
			note="Downloading programme data")
		programmes = traverse_obj(meta, ("stations", lambda _, v: v["station_id"] == station_id,
			"programs", "program"), get_all=False)

		for prog in programmes:
			if prog["ft"] <= url_time.timestring() < prog["to"]:
				actual_start = rtime.RadikoSiteTime(prog["ft"])
				actual_end = rtime.RadikoSiteTime(prog["to"])

				if len(prog.get("person")) > 0:
					cast = [person.get("name") for person in prog.get("person")]
				else:
					cast = [prog.get("performer")]

				return {
					"id": join_nonempty(station_id, actual_start.timestring()),
					"timestamp": actual_start.timestamp(),
					"release_timestamp": actual_end.timestamp(),
					"cast": cast,
					"description": clean_html(join_nonempty("summary", "description", from_dict=prog, delim="\n")),
					**traverse_obj(prog, {
							"title": "title",
							"duration": "dur",
							"thumbnail": "img",
							"series": "season_name",
							"tags": "tag",
						}
					)}, (actual_start, actual_end), int_or_none(prog.get("ts_in_ng")) != 2

	def _extract_chapters(self, station, start, end, video_id=None):
		api_url = update_url_query(f"https://api.radiko.jp/music/api/v1/noas/{station}", {
			"start_time_gte": start.isoformat(),
			"end_time_lt": end.isoformat(),
		})
		data_json = self._download_json(
			api_url, video_id, note="Downloading tracklist", errnote="Downloading tracklist", fatal=False
		)

		chapters = []
		for track in traverse_obj(data_json, "data") or []:
			artist = traverse_obj(track, ("artist", "name")) or track.get("artist_name")
			chapters.append({
				"title": join_nonempty(artist, track.get("title"), delim=" - "),
				"start_time": (datetime.datetime.fromisoformat(track.get("displayed_start_time")) - start).total_seconds(),
			})

		return chapters

	def _real_extract(self, url):
		station, timestring = self._match_valid_url(url).group("station", "id")
		url_time = rtime.RadikoSiteTime(timestring)
		meta, times, available = self._get_programme_meta(station, url_time)
		live_status = "was_live"

		if not available:
			self.raise_no_formats("This programme is not available. If this is an NHK station, you may wish to try NHK Radiru.",
				video_id=meta["id"], expected=True)

		start = times[0]
		end = times[1]
		now = datetime.datetime.now(tz=rtime.JST)
		expiry_free, expiry_tf30 = end.expiry()

		if expiry_tf30 < now:
			self.raise_no_formats("Programme is no longer available.", video_id=meta["id"], expected=True)
		need_tf30 = expiry_free < now
		if need_tf30 and not self._check_tf30():
			self.raise_login_required("Programme is only available with a Timefree 30 subscription")
		elif start > now:
			self.raise_no_formats("Programme has not aired yet.", video_id=meta["id"], expected=True)
			live_status = "is_upcoming"
		elif start <= now < end:
			live_status = "is_upcoming"
			self.raise_no_formats("Programme has not finished airing yet.", video_id=meta["id"], expected=True)

		region = self._get_station_region(station)
		station_meta = self._get_station_meta(region, station)
		if live_status == "was_live":
			chapters = self._extract_chapters(station, start, end, video_id=meta["id"])
			auth_data = self._auth(region, need_tf30=need_tf30)
			formats = self._get_station_formats(station, True, auth_data, start_at=start, end_at=end, use_pc_html5=need_tf30)
		else:
			chapters = None
			formats = None

		return {
			**station_meta,
			"alt_title": None,  # override from station metadata
			"thumbnails": None,

			**meta,
			"chapters": chapters,
			"formats": formats,
			"live_status": live_status,
			"container": "m4a_dash",  # force fixup, AAC-only HLS
		}


class RadikoSearchIE(InfoExtractor):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/#!/search/(?:radio/)?(?:timeshift|live|history)\?"
	_TESTS = [{
		# timefree, specific area
		"url": "https://radiko.jp/#!/search/live?key=city%20chill%20club&filter=past&start_day=&end_day=&region_id=&area_id=JP13&cul_area_id=JP13&page_idx=0",
		"playlist_mincount": 4,
		"info_dict": {
			"id": "city chill club-past-all-JP13",
			"title": "city chill club",
		}
	}, {
		# live/future, whole country
		"url": "https://radiko.jp/#!/search/live?key=%EF%BC%AE%EF%BC%A8%EF%BC%AB%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9&filter=future&start_day=&end_day=&region_id=all&area_id=JP13&cul_area_id=JP13&page_idx=0",
		"playlist_mincount": 8,
		"info_dict": {
			"id": "ＮＨＫニュース-future-all-all",
			"title": "ＮＨＫニュース",
		},
	}, {
		# ludicrous amount of results (multi-page)
		"url": "https://radiko.jp/#!/search/live?key=%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9",
		"playlist_mincount": 100,
		"info_dict": {
			"id": "ニュース-all-all",
			"title": "ニュース"
		},
		'expected_warnings': ['Skipping podcasts. If you really want EVERY EPISODE of EVERY RESULT, set your search filter to Podcasts only.'],
	}]

	def _strip_date(self, date):
		# lazy way of making a timestring (from eg 2025-05-20 01:00:00)
		return date.replace(" ", "").replace("-", "").replace(":", "")

	def _pagefunc(self, url, idx):
		url = update_url_query(url, {"page_idx": idx})
		data = self._download_json(url, None, note=f"Downloading page {idx+1}")

		results = []
		for r in data.get("data"):
			station = r.get("station_id")
			timestring = self._strip_date(r.get("start_time"))

			results.append(
				self.url_result(
					f"https://radiko.jp/#!/ts/{station}/{timestring}",
					id=join_nonempty(station, timestring),
					ie=RadikoTimeFreeIE,
				)
			)
		return results

	def _real_extract(self, url):
		# urllib.parse interprets the path as just one giant fragment because of the #, so we hack it away
		url = url.replace("/#!/", "/!/", 1)
		queries = parse_qs(url)
		key = traverse_obj(queries, ("key", 0))

		# site used to use "cul_area_id" in the search url, now it uses "cur_area_id" (with an r)
		# and outright rejects the old one with HTTP Error 415: Unsupported Media Type
		if queries.get("cul_area_id"):
			queries["cur_area_id"] =  queries.pop("cul_area_id")

		if queries.get("filter"):
			filter_set = set(queries["filter"][0].split("|"))
			del queries["filter"]
		else:
			filter_set = {"future", "past", "channel"}

		if filter_set == {"channel"}:
			podcast_search_url = update_url_query(
				"https://radiko.jp/!/search/podcast/live", {"key": key}
			).replace("!", "#!", 1)  # same shit with urllib.parse
			return self.url_result(podcast_search_url, ie=RadikoPodcastSearchIE)

		if "channel" in filter_set:
			self.report_warning("Skipping podcasts. If you really want EVERY EPISODE of EVERY RESULT, set your search filter to Podcasts only.")
		filter_set.discard("channel")

		if filter_set == {"future", "past"}:
			filter_str = ""
		else:
			filter_str = "|".join(filter_set)  # there should be only one filter now, so this should be the same as filter_set[0]
			# but if there's more than one, then we should at least try to pass it through as-is, in the hope that it works
			if len(filter_set) != 1:
				# but also kick up a stink about it so it's clear it probably won't
				self.report_warning("Your search has an unknown combination of filters, so this request will probably fail!")

		search_url = update_url_query("https://api.annex-cf.radiko.jp/v1/programs/legacy/perl/program/search", {
			**queries,
			"filter": filter_str,
			"uid": "".join(random.choices("0123456789abcdef", k=32)),
			"app_id": "pc",
			"row_limit": 50,  # higher row_limit = more results = less requests = more good
		})

		results = OnDemandPagedList(lambda idx: self._pagefunc(search_url, idx), 50)

		day = traverse_obj(queries, ("start_day", 0)) or "all"
		region = traverse_obj(queries, ("region_id", 0)) or traverse_obj(queries, ("area_id", 0))
		status_filter = filter_str or "all"

		playlist_id = join_nonempty(key, status_filter, day, region)

		return {
			"_type": "playlist",
			"title": key,
			"id": playlist_id,
			"entries": results,
		}


class RadikoShareIE(InfoExtractor):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/share/"

	def _real_extract(self, url):
		queries = parse_qs(url)
		station = traverse_obj(queries, ("sid", 0))
		time = traverse_obj(queries, ("t", 0))
		time = rtime.RadikoShareTime(time).timestring()
		return self.url_result(
			f"https://radiko.jp/#!/ts/{station}/{time}", RadikoTimeFreeIE,
			id=join_nonempty(station, time)
		)


class RadikoStationButtonIE(InfoExtractor):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/button-embed/live/"
	_EMBED_REGEX = [fr"<iframe[^>]+src=[\"'](?P<url>{_VALID_URL}[^\"']+)"]

	# supposedly it'll only allow a few stations from a few domains https://radiko.jp/res/app/external/web/playback_permission.json
	_TESTS = [{
		"url": "https://radiko.jp/button-embed/live/?layout=1&station_id=QRR&theme=0",
		"info_dict": {
			"ext": "m4a",
			'live_status': 'is_live',
			"id": "QRR",
		},
		'only_matching': True,
	}]

	_WEBPAGE_TESTS = [{
		"url": "https://cocolo.jp/",
		"info_dict": {
			"ext": "m4a",
			"live_status": "is_live",
			'id': 'CCL',
			"title": "re:^FM COCOLO.+$",
			'alt_title': 'FM COCOLO',
			'thumbnail': 'https://radiko.jp/v2/static/station/logo/CCL/lrtrim/688x160.png',

			'channel': 'FM COCOLO',
			'channel_id': 'CCL',
			'channel_url': 'https://cocolo.jp',
			'uploader': 'FM COCOLO',
			'uploader_id': 'CCL',
			'uploader_url': 'https://cocolo.jp',
		},
	}]

	def _real_extract(self, url):
		queries = parse_qs(url)
		station = traverse_obj(queries, ("station_id", 0))

		return self.url_result(f"https://radiko.jp/#!/live/{station}", RadikoLiveIE)


class RadikoPersonIE(InfoExtractor):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/persons/(?P<id>\d+)"
	_TESTS = [{
		"url": "https://radiko.jp/persons/11421",
		"playlist_mincount": 10,
		"info_dict": {
			"id": "person-11421",
		},
	},{
		"url": "https://radiko.jp/persons/11421",
		"params": {'extractor_args': {'rajiko': {'key_station_only': ['']}}},
		"playlist_mincount": 1,
		"info_dict": {
			"id": "person-11421",
		},
	}]

	def _real_extract(self, url):
		person_id = self._match_id(url)

		now = rtime.RadikoTime.now(tz=rtime.JST)

		min_start = (now - datetime.timedelta(days=30)).broadcast_day_start()
		# we set the earliest time as the earliest we can get (or at least, that it's possible to get),
		# so, the start of the broadcast day 30 days ago
		# that way we can get everything we can actually download, including stuff that aired at eg "26:00"

		person_api_url = update_url_query("https://api.radiko.jp/program/api/v1/programs", {
			"person_id": person_id,
			"start_at_gte": min_start.isoformat(),
			"start_at_lt": now.isoformat(),
		})
		person_api = self._download_json(person_api_url, person_id)

		def entries():
			key_station_only = len(self._configuration_arg("key_station_only", ie_key="rajiko")) > 0
			for episode in person_api.get("data"):

				station = episode.get("station_id")
				if key_station_only and episode.get("key_station_id") != station:
					continue

				start = episode.get("start_at")
				timestring = rtime.RadikoTime.fromisoformat(start).timestring()

				timefree_id = join_nonempty(station, timestring)
				timefree_url = f"https://radiko.jp/#!/ts/{station}/{timestring}"
				yield self.url_result(timefree_url, ie=RadikoTimeFreeIE, video_id=timefree_id)

		return self.playlist_result(entries(), playlist_id=join_nonempty("person", person_id))


class RadikoRSeasonsIE(InfoExtractor):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/(?:mobile/)?r_seasons/(?P<id>\d+$)"
	_TESTS = [{
		"url": "https://radiko.jp/r_seasons/10012302",
		"playlist_mincount": 4,
		"info_dict": {
			"id": '10012302',
			"title": '山下達郎の楽天カード サンデー・ソングブック',
			'thumbnail': 'https://program-static.cf.radiko.jp/935a87fc-4a52-48e5-9468-7b2ef9448d9f.jpeg',
		}
	}, {
		"url": "https://radiko.jp/r_seasons/10002831",
		"playlist_mincount": 4,
		"info_dict": {
			"id": "10002831",
			"title": "Tokyo Moon",
			'description': 'md5:3eef525003bbe96ccf33ec647c43d904',
			'thumbnail': 'https://program-static.cf.radiko.jp/0368ee85-5d5f-41c9-8ee1-6c1035d87b3f.jpeg',
		}
	}]

	def _real_extract(self, url):
		season_id = self._match_id(url)
		html = self._download_webpage(url, season_id)
		pageProps = self._search_nextjs_data(html, season_id)["props"]["pageProps"]
		season_id = traverse_obj(pageProps, ("rSeason", "id")) or season_id

		def entries():
			for episode in pageProps.get("pastPrograms"):
				station = traverse_obj(episode, ("stationId"))
				start = traverse_obj(episode, ("startAt", "seconds"))
				timestring = rtime.RadikoTime.fromtimestamp(start, tz=rtime.JST).timestring()

				timefree_id = join_nonempty(station, timestring)
				timefree_url = f"https://radiko.jp/#!/ts/{station}/{timestring}"

				yield self.url_result(timefree_url, ie=RadikoTimeFreeIE, video_id=timefree_id)

		return self.playlist_result(
			entries(),
			playlist_id=season_id,
			**traverse_obj(pageProps, ("rSeason", {
				"playlist_title": "rSeasonName",
				"thumbnail": "backgroundImageUrl",
				"description": ("summary", filter),
			})),
		)
