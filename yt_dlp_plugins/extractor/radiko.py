import base64
import datetime
import random
import urllib.parse

import pkgutil

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	OnDemandPagedList,
	clean_html,
	int_or_none,
	join_nonempty,
	parse_qs,
	traverse_obj,
	url_or_none,
	update_url_query,
)

import yt_dlp_plugins.extractor.radiko_time as rtime


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

	_APP_VERSIONS = [f"8.0.{i}" for i in range(6+1)]

	_DELIVERED_ONDEMAND = ('radiko.jp',)
	_DOESNT_WORK_WITH_FFMPEG = ('tf-f-rpaa-radiko.smartstream.ne.jp', 'si-f-radiko.smartstream.ne.jp')

	_region = None
	_user = None

	def _index_regions(self):
		region_data = {}

		tree = self._download_xml("https://radiko.jp/v3/station/region/full.xml", None, note="Indexing regions")
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
		coords = f"{round(lat, 6)},{round(long, 6)},gps"
		self.write_debug(coords)
		return coords

	def _generate_random_info(self):
		return {
			"X-Radiko-App": "aSmartPhone8",
			"X-Radiko-App-Version": random.choice(self._APP_VERSIONS),
			"X-Radiko-Device": "android",
			"X-Radiko-User": ''.join(random.choices('0123456789abcdef', k=32)),
			"User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Mobile Safari/537.36"
			# ^this appears to be hardcoded - i have a sony xa2 on android 9, i still get this. grepping for it in libapp.so shows it is there in some capacity
		}

	def _get_station_region(self, station):
		regions = self.cache.load("rajiko", "region_index")
		if regions is None or station not in regions:
			self.write_debug(f"station {station} not found, re-indexing in case it's new")
			regions = self._index_regions()

		return regions[station]

	def _negotiate_token(self, station_region):
		device_info = self._generate_random_info()
		response, auth1_handle = self._download_webpage_handle("https://radiko.jp/v2/api/auth1", None,
			"Authenticating: step 1", headers=device_info)

		self.write_debug(response)

		auth1_response_headers = auth1_handle.headers
		auth_token = auth1_response_headers["X-Radiko-AuthToken"]

		key_length = int(auth1_response_headers["X-Radiko-KeyLength"])
		key_offset = int(auth1_response_headers["X-Radiko-KeyOffset"])
		self.write_debug(f"KeyLength: {key_length}")
		self.write_debug(f"KeyOffset: {key_offset}")

		raw_partial_key = self._FULL_KEY[key_offset:key_offset + key_length]
		partial_key = base64.b64encode(raw_partial_key).decode("ascii")
		self.write_debug(partial_key)

		coords = self._get_coords(station_region)
		auth2_headers = {
			**device_info,
			"X-Radiko-AuthToken": auth_token,
			"X-Radiko-Location": coords,
			"X-Radiko-Connection": random.choice(("wifi", "mobile",)),
			"X-Radiko-Partialkey": partial_key,
		}

		auth2 = self._download_webpage("https://radiko.jp/v2/api/auth2", station_region,
			"Authenticating: step 2", headers=auth2_headers)
		self.write_debug(auth2.strip())
		actual_region, region_kanji, region_english = auth2.split(",")

		region_mismatch = actual_region != station_region
		if region_mismatch:
			self.report_warning(f"Region mismatch: Expected {station_region}, got {actual_region}. Coords: {coords}.")
			self.report_warning("Please report this at https://github.com/garret1317/yt-dlp-rajiko/issues")
			self.report_warning(auth2.strip())
			self.report_warning(auth2_headers)

		token = {
			"X-Radiko-AreaId": actual_region,
			"X-Radiko-AuthToken": auth_token,
		}

		self._user = auth2_headers["X-Radiko-User"]
		if not region_mismatch:
			self.cache.store("rajiko", station_region, {
				"token": token,
				"user": self._user,
			})
		return token

	def _auth(self, station_region):
		cachedata = self.cache.load("rajiko", station_region)
		self.write_debug(cachedata)
		if cachedata is not None:
			token = cachedata.get("token")
			self._user = cachedata.get("user")
			response = self._download_webpage("https://radiko.jp/v2/api/auth_check", station_region, "Checking cached token",
				headers=token, expected_status=401)
			self.write_debug(response)
			if response == "OK":
				return token
		return self._negotiate_token(station_region)

	def _get_station_meta(self, region, station_id):
		cachedata = self.cache.load("rajiko", station_id)
		now = datetime.datetime.now()
		if cachedata is None or cachedata.get("expiry") < now.timestamp():
			region = self._download_xml(f"https://radiko.jp/v3/station/list/{region}.xml", station_id,
				note="Downloading station metadata")
			station = region.find(f'.//station/id[.="{station_id}"]/..')  # a <station> with an <id> of our station_id
			station_name = station.find("name").text
			station_url = url_or_none(station.find("href").text)
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

				"thumbnail": url_or_none(station.find("banner").text),
			}
			self.cache.store("rajiko", station_id, {
				"expiry": (now + datetime.timedelta(days=1)).timestamp(),
				"meta": meta
			})
			return meta
		else:
			self.to_screen(f"{station_id}: Using cached station metadata")
			return cachedata.get("meta")

	def _get_station_formats(self, station, timefree, auth_data, start_at=None, end_at=None):
		device = self._configuration_arg('device', ['aSmartPhone7a'], casesense=True, ie_key="rajiko")[0]  # aSmartPhone7a formats = always happy path
		url_data = self._download_xml(f"https://radiko.jp/v3/station/stream/{device}/{station}.xml",
			station, note=f"Downloading {device} stream information")

		seen_urls = []
		formats = []

		timefree_int = 1 if timefree else 0
		for element in url_data.findall(f".//url[@timefree='{timefree_int}'][@areafree='0']/playlist_create_url"):
		# find <url>s with matching timefree and no areafree, then get their <playlist_create_url>
			url = element.text
			if url in seen_urls:  # there are always dupes, even with ^ specific filtering
				continue

			seen_urls.append(url)
			playlist_url = update_url_query(url, {
					"station_id": station,
					"l": "15",  # l = length, ie how many seconds in the live m3u8 (max 300)
					"lsid": self._user,
					"type": "b",  # it is a mystery
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

			if domain in self._DOESNT_WORK_WITH_FFMPEG:
					self.write_debug(f"skipping {domain} (known not working)")
					continue
			elif domain in self._DELIVERED_ONDEMAND:
					# override the defaults for delivered as on-demand
					delivered_live = False
					preference = 1
					entry_protocol = None

			formats += self._extract_m3u8_formats(
				playlist_url, station, m3u8_id=domain, fatal=False, headers=auth_data,
				live=delivered_live, preference=preference, entry_protocol=entry_protocol,
				note=f"Downloading m3u8 information from {domain}")
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
			"thumbnail": "https://radiko.jp/res/banner/FMT/20220512162447.jpg",

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
			"thumbnail": "https://radiko.jp/res/banner/NORTHWAVE/20150731161543.png",

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
			"thumbnail": "https://radiko.jp/res/banner/RN1/20120802154152.png",

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
		formats = self._get_station_formats(station, False, auth_data)

		return {
			"is_live": True,
			"id": station,
			**station_meta,
			"formats": formats,
		}


class RadikoTimeFreeIE(_RadikoBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/#!/ts/(?P<station>[A-Z0-9-_]+)/(?P<id>\d+)"
	_TESTS = [{
		"url": "https://radiko.jp/#!/ts/INT/20240802230000",
		"info_dict": {
			"live_status": "was_live",
			"ext": "m4a",
			"id": "INT-20240802230000",

			"title": "TOKYO MOON",
			"series": "Tokyo Moon",
			"description": "md5:20e68d2f400a391fa34d4e7c8c702cb8",
			"chapters": "count:15",
			"thumbnail": "https://program-static.cf.radiko.jp/ehwtw6mcvy.jpg",

			"upload_date": "20240802",
			"timestamp": 1722607200.0,
			"release_date": "20240802",
			"release_timestamp": 1722610800.0,
			"duration": 3600,

			"channel": "interfm",
			"channel_id": "INT",
			"channel_url": "https://www.interfm.co.jp/",
			"uploader": "interfm",
			"uploader_id": "INT",
			"uploader_url": "https://www.interfm.co.jp/",

			"cast": ["松浦\u3000俊夫"],
			"tags": ["松浦俊夫"],
		},
	}, {
		# late-night/early-morning show to test broadcast day checking
		"url": "https://radiko.jp/#!/ts/TBS/20240803033000",
		"info_dict": {
			"live_status": "was_live",
			"ext": "m4a",
			"id": "TBS-20240803033000",

			"title": "CITY CHILL CLUB",
			"series": "CITY CHILL CLUB",
			"description": "md5:3fba2c1125059bed27247c0be90e58fa",
			"chapters": "count:24",
			"thumbnail": "https://program-static.cf.radiko.jp/ku7t4ztnaq.jpg",

			"upload_date": "20240802",
			"timestamp": 1722623400.0,
			"release_date": "20240802",
			"release_timestamp": 1722628800.0,
			"duration": 5400,

			"channel": "TBSラジオ",
			"channel_url": "https://www.tbsradio.jp/",
			"channel_id": "TBS",
			"uploader": "TBSラジオ",
			"uploader_url": "https://www.tbsradio.jp/",
			"uploader_id": "TBS",

			"tags": ["CCC905", "音楽との出会いが楽しめる", "人気アーティストトーク", "音楽プロデューサー出演", "ドライブ中におすすめ", "寝る前におすすめ", "学生におすすめ"],
			"cast": ["PES"],
		},
	}]

	def _get_programme_meta(self, station_id, url_time):
		day = url_time.broadcast_day_string()
		meta = self._download_json(f"https://radiko.jp/v4/program/station/date/{day}/{station_id}.json", station_id,
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
		data = self._download_json(api_url, video_id, note="Downloading tracklist").get("data")

		chapters = []
		for track in data:
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

		if end.broadcast_day_end() < now - datetime.timedelta(days=7):
			self.raise_no_formats("Programme is no longer available.", video_id=meta["id"], expected=True)
		elif start > now:
			self.raise_no_formats("Programme has not aired yet.", video_id=meta["id"], expected=True)
			live_status = "is_upcoming"
		elif start <= now < end:
			live_status = "is_upcoming"
			self.raise_no_formats("Programme has not finished airing yet.", video_id=meta["id"], expected=True)

		region = self._get_station_region(station)
		station_meta = self._get_station_meta(region, station)
		chapters = self._extract_chapters(station, start, end, video_id=meta["id"])
		auth_data = self._auth(region)
		formats = self._get_station_formats(station, True, auth_data, start_at=start, end_at=end)

		return {
			**station_meta,
			"alt_title": None,
			**meta,
			"chapters": chapters,
			"formats": formats,
			"live_status": live_status,
			"container": "m4a_dash",  # force fixup, AAC-only HLS
		}


class RadikoSearchIE(InfoExtractor):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/#!/search/(?:timeshift|live|history)\?"
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
	}]

	def _strip_date(self, date):
		return date.replace(" ", "").replace("-", "").replace(":", "")

	def _pagefunc(self, url, idx):
		url = update_url_query(url, {"page_idx": idx})
		data = self._download_json(url, None, note=f"Downloading page {idx+1}")

		return [self.url_result("https://radiko.jp/#!/ts/{station}/{time}".format(
				station = i.get("station_id"), time = self._strip_date(i.get("start_time"))))
			for i in data.get("data")]

	def _real_extract(self, url):
		url = url.replace("/#!/", "/!/", 1)
		# urllib.parse interprets the path as just one giant fragment because of the #, so we hack it away
		queries = parse_qs(url)

		search_url = update_url_query("https://radiko.jp/v3/api/program/search", {
			**queries,
			"uid": "".join(random.choices("0123456789abcdef", k=32)),
			"app_id": "pc",
			"row_limit": 50,  # higher row_limit = more results = less requests = more good
		})

		results = OnDemandPagedList(lambda idx: self._pagefunc(search_url, idx), 50)

		key = traverse_obj(queries, ("key", 0))
		day = traverse_obj(queries, ("start_day", 0)) or "all"
		region = traverse_obj(queries, ("region_id", 0)) or traverse_obj(queries, ("area_id", 0))
		status_filter = traverse_obj(queries, ("filter", 0)) or "all"

		playlist_id = join_nonempty(key, status_filter, day, region)

		return {
			"_type": "playlist",
			"title": traverse_obj(queries, ("key", 0)),
			"id": playlist_id,
			"entries": results,
		}

class RadikoShareIE(InfoExtractor):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/share/"
	_TESTS = [{
		# 29-hour time -> 24-hour time
		"url": "http://radiko.jp/share/?sid=FMT&t=20240802240000",
		"info_dict": {
			"live_status": "was_live",
			"ext": "m4a",
			"id": "FMT-20240803000000",  # the time given (24:00) works out to 00:00 the next day

			"title": "JET STREAM",
			"series": "JET STREAM",
			"description": "md5:c1a2172036ebb7a54eeafb47e0a08a50",
			"chapters": "count:9",
			"thumbnail": "https://program-static.cf.radiko.jp/greinlrspi.jpg",

			"upload_date": "20240802",
			"timestamp": 1722610800.0,
			"release_date": "20240802",
			"release_timestamp": 1722614100.0,
			"duration": 3300,

			"channel": "TOKYO FM",
			"channel_id": "FMT",
			"channel_url": "https://www.tfm.co.jp/",
			"uploader": "TOKYO FM",
			"uploader_id": "FMT",
			"uploader_url": "https://www.tfm.co.jp/",

			"cast": ["福山雅治"],
			"tags": ["福山雅治", "夜間飛行", "音楽との出会いが楽しめる", "朗読を楽しめる", "寝る前に聴きたい"],
		}
	}]

	def _real_extract(self, url):
		queries = parse_qs(url)
		station = traverse_obj(queries, ("sid", 0))
		time = traverse_obj(queries, ("t", 0))
		time = rtime.RadikoShareTime(time).timestring()
		return self.url_result(f"https://radiko.jp/#!/ts/{station}/{time}", RadikoTimeFreeIE)


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
			"title": "re:^文化放送.+$",
			'alt_title': 'JOQR BUNKA HOSO',
			'thumbnail': 'https://radiko.jp/res/banner/QRR/20240423144553.png',
			'channel': '文化放送',
			'channel_id': 'QRR',
			'channel_url': 'http://www.joqr.co.jp/',
			'uploader': '文化放送',
			'uploader_id': 'QRR',
			'uploader_url': 'http://www.joqr.co.jp/',

		}
	}]

	_WEBPAGE_TESTS = [{
		"url": "https://cocolo.jp/",
		"info_dict": {
			"ext": "m4a",
			"live_status": "is_live",
			'id': 'CCL',
			"title": "re:^FM COCOLO.+$",
			'alt_title': 'FM COCOLO',
			'thumbnail': 'https://radiko.jp/res/banner/CCL/20161014144826.png',

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
		"playlist_count": 1,
		"info_dict": {
			"id": "person-11421",
		},
	}]

	def _real_extract(self, url):
		person_id = self._match_id(url)

		now = rtime.RadikoTime.now(tz=rtime.JST)

		min_start = (now - datetime.timedelta(days=7)).broadcast_day_start()
		# we set the earliest time as the earliest we can get,
		# so, the start of the broadcast day 1 week ago
		# that way we can get everything we can actually download, including stuff that aired at eg "26:00"

		person_api_url = update_url_query("https://api.radiko.jp/program/api/v1/programs", {
			"person_id": person_id,
			"start_at_gte": min_start.isoformat(),
			"end_at_lt": now.isoformat(),
		})
		person_api = self._download_json(person_api_url, person_id)

		def entries():
			for episode in person_api.get("data"):
				if len(self._configuration_arg("key_station_only", ie_key="rajiko")) > 0:
					if episode.get("key_station_id") != episode.get("station_id"):
						continue

				share_url = traverse_obj(episode, ("radiko_url", ("pc", "sp", "android", "ios", "app"),
					{url_or_none}), get_all=False)
				# they're all identical share links at the moment (5th aug 2024) but they might not be in the future

				# predictions:
				# pc will probably stay the same
				# don't know what sp is, possibly "SmartPhone"?, anyway seems reasonably generic
				# android is easier for me to reverse-engineer than ios (no ithing)
				# i assume "app" would be some internal tell-it-to-do-something link, not a regular web link

				yield self.url_result(share_url, ie=RadikoShareIE, video_title=episode.get("title"))

		return self.playlist_result(entries(), playlist_id=join_nonempty("person", person_id))
