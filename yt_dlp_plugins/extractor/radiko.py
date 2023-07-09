import base64
import datetime
import random
import secrets
import urllib.parse
import yt_dlp_plugins.extractor.radiko_key as key

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	clean_html,
	join_nonempty,
	parse_qs,
	traverse_obj,
	unified_timestamp,
	url_or_none,
	update_url_query,
)


class _RadikoBaseIE(InfoExtractor):
	_FULL_KEY = key.FULLKEY

	_COORDINATES = {
		# source: https://github.com/jackyzy823/rajiko/blob/master/background.js
			# data source (capital of prefectures): https://www.benricho.org/chimei/latlng_data.html
			# data source :	jp.radiko.Player.V6FragmentAreaCheck.freeloc_init
		"JP1": [43.064615, 141.346807], "JP2": [40.824308, 140.739998],	"JP3": [39.703619, 141.152684],
		"JP4": [38.268837, 140.8721], "JP5": [39.718614, 140.102364], "JP6": [38.240436, 140.363633],
		"JP7": [37.750299, 140.467551], "JP8": [36.341811, 140.446793], "JP9": [36.565725, 139.883565],
		"JP10": [36.390668, 139.060406], "JP11": [35.856999, 139.648849], "JP12": [35.605057, 140.123306],
		"JP13": [35.689488, 139.691706], "JP14": [35.447507, 139.642345], "JP15": [37.902552, 139.023095],
		"JP16": [36.695291, 137.211338], "JP17": [36.594682, 136.625573], "JP18": [36.065178, 136.221527],
		"JP19": [35.664158, 138.568449], "JP20": [36.651299, 138.180956], "JP21": [35.391227, 136.722291],
		"JP22": [34.97712, 138.383084], "JP23": [35.180188, 136.906565], "JP24": [34.730283, 136.508588],
		"JP25": [35.004531, 135.86859], "JP26": [35.021247, 135.755597], "JP27": [34.686297, 135.519661],
		"JP28": [34.691269, 135.183071], "JP29": [34.685334, 135.832742], "JP30": [34.225987, 135.167509],
		"JP31": [35.503891, 134.237736], "JP32": [35.472295, 133.0505], "JP33": [34.661751, 133.934406],
		"JP34": [34.39656, 132.459622], "JP35": [34.185956, 131.470649], "JP36": [34.065718, 134.55936],
		"JP37": [34.340149, 134.043444], "JP38": [33.841624, 132.765681], "JP39": [33.559706, 133.531079],
		"JP40": [33.606576, 130.418297], "JP41": [33.249442, 130.299794], "JP42": [32.744839, 129.873756],
		"JP43": [32.789827, 130.741667], "JP44": [33.238172, 131.612619], "JP45": [31.911096, 131.423893],
		"JP46": [31.560146, 130.557978], "JP47": [26.2124, 127.680932],
	}

	_APP_VERSIONS = [f"8.0.{i}" for i in range(6+1)]

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
		return f"{round(lat, 6)},{round(long, 6)},gps"

	def _generate_random_info(self):
		info = {
			"X-Radiko-App": "aSmartPhone8",
			"X-Radiko-App-Version": random.choice(self._APP_VERSIONS),
			"X-Radiko-Device": "android",
			"X-Radiko-User": secrets.token_hex(16),
			"User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Mobile Safari/537.36"
			# ^this appears to be hardcoded - i have a sony xa2 on android 9, i still get this. grepping for it in libapp.so shows it is there in some capacity
		}
		return info

	def _get_station_region(self, station):
		regions = self.cache.load("rajiko", "region_index")
		if regions is None or station not in regions:
			regions = self._index_regions()

		return regions[station]

	def _negotiate_token(self, station_region):
		info = self._generate_random_info()
		response, auth1_handle = self._download_webpage_handle("https://radiko.jp/v2/api/auth1", None,
			"Authenticating: step 1", headers=self._generate_random_info())

		self.write_debug(response)

		auth1_header = auth1_handle.info()
		auth_token = auth1_header["X-Radiko-AuthToken"]
		key_length = int(auth1_header["X-Radiko-KeyLength"])
		key_offset = int(auth1_header["X-Radiko-KeyOffset"])

		raw_partial_key = self._FULL_KEY[key_offset:key_offset + key_length]
		partial_key = base64.b64encode(raw_partial_key)

		headers = {
			**info,
			"X-Radiko-AuthToken": auth_token,
			"X-Radiko-Location": self._get_coords(station_region),
			"X-Radiko-Connection": "wifi",
			"X-Radiko-Partialkey": partial_key,
		}

		auth2 = self._download_webpage("https://radiko.jp/v2/api/auth2", station_region,
			"Authenticating: step 2", headers=headers)

		self.write_debug(auth2.strip())
		actual_region, region_kanji, region_english = auth2.split(",")

		if actual_region != station_region:
			self.report_warning(f"Didn't get the right region: expected {station_region}, got {actual_region}. This should never happen, please report it by opening an issue on the plugin repo.")
			# this should never happen

		token = {
			"X-Radiko-AreaId": actual_region,
			"X-Radiko-AuthToken": auth_token,
		}

		self._user = headers["X-Radiko-User"]
		self.cache.store("rajiko", station_region, {"token": token, "user": self._user})
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
			if response != "OK":
				token = self._negotiate_token(station_region)
		else:
			token = self._negotiate_token(station_region)
		return token

	def _get_station_meta(self, region, station_id):
		region = self._download_xml(f"https://radiko.jp/v3/station/list/{region}.xml", region, note="Downloading station listings")
		station = region.find(f'.//station/id[.="{station_id}"]/..')  # a <station> with an <id> of our station_id
		station_name = station.find("name").text
		station_url = url_or_none(station.find("href").text)
		return {
			"title": station_name,
			"channel": station_name,
			"uploader": station_name,
			"channel_id": station_id,
			"channel_url": station_url,
			"thumbnail": url_or_none(station.find("banner").text),
			"alt_title": station.find("ascii_name").text,
			"uploader_url": station_url,
			"id": station_id,
		}

	def _int2bool(self, i):
		i = int(i)
		return True if i == 1 else False

	def _get_station_formats(self, station, timefree, auth_data, start_at=None, end_at=None):
		# smartphone formats api = always happy path
		url_data = self._download_xml(f"https://radiko.jp/v3/station/stream/aSmartPhone7a/{station}.xml",
			station, note="Downloading stream information")

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
					"l": "15",
					"lsid": self._user,
					"type": "b",
				})
			if timefree:
				playlist_url = update_url_query(playlist_url, {
					"start_at": start_at,
					"ft": start_at,
					"end_at": end_at,
					"to": end_at,
				})
			domain = urllib.parse.urlparse(playlist_url).netloc
			formats += self._extract_m3u8_formats(
				playlist_url, station, m3u8_id=domain, fatal=False, headers=auth_data,
				note=f"Downloading m3u8 information from {domain}",
			)
		return formats


class RadikoLiveIE(_RadikoBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/#!/live/(?P<id>[A-Z0-9-_]+)"
	_TESTS = [{
		# JP13 (Tokyo)
		"url": "https://radiko.jp/#!/live/FMT",
		"info_dict": {
			"id": "FMT",
			"ext": "m4a",
			"live_status": "is_live",
			"alt_title": "TOKYO FM",
			"title": "re:^TOKYO FM.+$",
			"thumbnail": "https://radiko.jp/res/banner/FMT/20220512162447.jpg",
			"uploader_url": "https://www.tfm.co.jp/",
			"channel_url": "https://www.tfm.co.jp/",
			"channel": "TOKYO FM",
			"channel_id": "FMT",

		},
	}, {
		# JP1 (Hokkaido)
		"url": "https://radiko.jp/#!/live/NORTHWAVE",
		"info_dict": {
			"id": "NORTHWAVE",
			"ext": "m4a",
			"uploader_url": "https://www.fmnorth.co.jp/",
			"alt_title": "FM NORTH WAVE",
			"title": "re:^FM NORTH WAVE.+$",
			"live_status": "is_live",
			"thumbnail": "https://radiko.jp/res/banner/NORTHWAVE/20150731161543.png",
			"channel": "FM NORTH WAVE",
			"channel_url": "https://www.fmnorth.co.jp/",
			"channel_id": "NORTHWAVE",
		},
	}, {
		# ALL (all prefectures)
		# api still specifies a prefecture though, in this case JP12 (Chiba), so that"s what it auths as
		"url": "https://radiko.jp/#!/live/HOUSOU-DAIGAKU",
		"info_dict": {
			"id": "HOUSOU-DAIGAKU",
			"ext": "m4a",
			"title": "re:^放送大学.+$",
			"live_status": "is_live",
			"uploader_url": "https://www.ouj.ac.jp/",
			"alt_title": "HOUSOU-DAIGAKU",
			"thumbnail": "https://radiko.jp/res/banner/HOUSOU-DAIGAKU/20150805145127.png",
			"channel": "放送大学",
			"channel_url": "https://www.ouj.ac.jp/",
			"channel_id": "HOUSOU-DAIGAKU",
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
		"url": "https://radiko.jp/#!/ts/INT/20230616230000",
		"info_dict": {
			"title": "TOKYO MOON",
			"ext": "m4a",
			"id": "INT-20230616230000",
			"live_status": "was_live",
			"tags": ["松浦俊夫"],
			"description": "md5:804d83142a1ef1dfde48c44fb531482a",
			"duration": 3600,
			"thumbnail": "https://radiko.jp/res/program/DEFAULT_IMAGE/INT/72b3a65f-c3ee-4892-a327-adec52076d51.jpeg",
			"cast": ["松浦\u3000俊夫"],
			"series": "Tokyo Moon",
			"channel_id": "INT",
			"uploader_url": "https://www.interfm.co.jp/",
			"channel": "interfm",
			"channel_url": "https://www.interfm.co.jp/",
			"timestamp": 1686924000,
			"upload_date": "20230616",
			"release_date": "20230616",
			"release_timestamp": 1686927600,

		},
	}, {
		"url": "https://radiko.jp/#!/ts/NORTHWAVE/20230618173000",
		"info_dict": {
			"title": "角松敏生 My BLUES LIFE",
			"id": "NORTHWAVE-20230618173000",
			"ext": "m4a",
			"channel_id": "NORTHWAVE",
			"thumbnail": "https://radiko.jp/res/program/DEFAULT_IMAGE/NORTHWAVE/cwqcdppldk.jpg",
			"uploader_url": "https://www.fmnorth.co.jp/",
			"duration": 1800,
			"channel": "FM NORTH WAVE",
			"channel_url": "https://www.fmnorth.co.jp/",
			"live_status": "was_live",
			"tags": ["ノースウェーブ", "角松敏生", "人気アーティストトーク"],
			"cast": ["角松\u3000敏生"],
			"series": "角松敏生 My BLUES LIFE",
			"description": "md5:027860a5731c04779b6720047c7b8b59",
			"upload_date": "20230618",
			"release_timestamp": 1687078800,
			"timestamp": 1687077000,
			"release_date": "20230618",
		},
	}, {
		# late-night show, see comment in _unfuck_day
		"url": "https://radiko.jp/#!/ts/TBS/20230617030000",
		"info_dict": {
			"id": "TBS-20230617030000",
			"ext": "m4a",
			"title": "CITY CHILL CLUB",
			"cast": ["Mississippi Khaki Hair"],
			"thumbnail": "https://radiko.jp/res/program/DEFAULT_IMAGE/TBS/xxeimdxszs.jpg",
			"description": "md5:6b0401e5587c56abfabb695313db7057",
			"tags": ["CCC905", "音楽との出会いが楽しめる", "人気アーティストトーク", "音楽プロデューサー出演", "ドライブ中におすすめ", "寝る前におすすめ", "学生におすすめ"],
			"channel": "TBSラジオ",
			"uploader_url": "https://www.tbsradio.jp/",
			"channel_id": "TBS",
			"channel_url": "https://www.tbsradio.jp/",
			"duration": 7200,
			"series": "CITY CHILL CLUB",
			"live_status": "was_live",
			"timestamp": 1686938400,
			"upload_date": "20230616",
			"release_timestamp": 1686945600,
			"release_date": "20230616",
		},
	}, {
		# early-morning show, same reason
		"url": "https://radiko.jp/#!/ts/TBS/20230619050000",
		"info_dict": {
			"title": "生島ヒロシのおはよう定食・一直線",
			"id": "TBS-20230619050000",
			"ext": "m4a",
			"cast": ["生島\u3000ヒロシ"],
			"channel": "TBSラジオ",
			"thumbnail": "https://radiko.jp/res/program/DEFAULT_IMAGE/TBS/ch3vcvtc5e.jpg",
			"description": "md5:6cb392cb140261acd8a2f7c63314c9e8",
			"series": "生島ヒロシのおはよう定食・一直線",
			"tags": ["生島ヒロシ", "健康", "檀れい", "朝のニュースを効率良く"],
			"channel_url": "https://www.tbsradio.jp/",
			"uploader_url": "https://www.tbsradio.jp/",
			"channel_id": "TBS",
			"duration": 5400,
			"live_status": "was_live",
			"release_timestamp": 1687123800,
			"release_date": "20230618",
			"upload_date": "20230618",
			"timestamp": 1687118400,
		},
	}]

	_JST = datetime.timezone(datetime.timedelta(hours=9))

	def _timestring_to_datetime(self, time):
		return datetime.datetime(int(time[:4]), int(time[4:6]), int(time[6:8]),
				hour=int(time[8:10]), minute=int(time[10:12]), second=int(time[12:14]), tzinfo=self._JST)

	def _unfuck_day(self, time):
		# api counts 05:00 -> 28:59 (04:59 next day) as all the same day
		# like the 30-hour day, 06:00 -> 29:59 (05:59)
		# https://en.wikipedia.org/wiki/Date_and_time_notation_in_Japan#Time
		# but ends earlier, presumably so the early morning programmes dont look like late night ones
		# this means we have to shift back by a day so we can use the right api
		hour_mins = int(time[8:])
		if hour_mins < 50000:  # 050000 - 5AM
			date = self._timestring_to_datetime(time)
			date -= datetime.timedelta(days=1)
			time = date.strftime("%Y%m%d")

			return time
		return time[:8]

	def _get_programme_meta(self, station_id, start_time):
		day = self._unfuck_day(start_time)
		meta = self._download_json(f"https://radiko.jp/v4/program/station/date/{day}/{station_id}.json", station_id,
			note="Downloading programme data")
		programmes = traverse_obj(meta, ("stations", lambda _, v: v["station_id"] == station_id,
			"programs", "program"), get_all=False)

		for prog in programmes:
			if prog["ft"] <= start_time < prog["to"]:
				actual_start = prog["ft"]
				if len(prog.get("person")) > 0:
					cast = [person.get("name") for person in prog.get("person")]
				else:
					cast = [prog.get("performer")]

				return {
					"id": join_nonempty(station_id, actual_start),
					"timestamp": unified_timestamp(f"{actual_start}+0900"),  # hack to account for timezone
					"release_timestamp": unified_timestamp(f"{prog['to']}+0900"),
					"cast": cast,
					"description": clean_html(join_nonempty("summary", "description", from_dict=prog, delim="\n")),
					**traverse_obj(prog, {
							"title": "title",
							"duration": "dur",
							"thumbnail": "img",
							"series": "season_name",
							"tags": "tag",
						}
					)}, (prog.get("ft"), prog.get("to"))

	def _extract_chapters(self, station, start, end, video_id=None):
		start_str = urllib.parse.quote(start.isoformat())
		end_str = urllib.parse.quote(end.isoformat())
		data = self._download_json(f"https://api.radiko.jp/music/api/v1/noas/{station}?start_time_gte={start_str}&end_time_lt={end_str}",
			video_id, note="Downloading tracklist").get("data")

		chapters = []
		for track in data:
			artist = traverse_obj(track, ("artist", "name")) or track.get("artist_name")
			chapters.append({
				"title": join_nonempty(artist, track.get("title"), delim=" - "),
				"start_time": (datetime.datetime.fromisoformat(track.get("displayed_start_time")) - start).total_seconds(),
			})

		return chapters

	def _real_extract(self, url):
		station, start_time = self._match_valid_url(url).group("station", "id")
		meta, times = self._get_programme_meta(station, start_time)

		noformats_expected = False
		noformats_msg = "No video formats found!"
		noformats_force = False
		live_status = "was_live"

		start_datetime = self._timestring_to_datetime(times[0])
		end_datetime = self._timestring_to_datetime(times[1])

		now = datetime.datetime.now(tz=self._JST)

		if end_datetime < now - datetime.timedelta(days=7):
			noformats_expected = True
			noformats_msg = "Programme is no longer available."
		elif start_datetime > now:
			noformats_expected = True
			noformats_msg = "Programme has not aired yet."
			live_status = "is_upcoming"
		elif start_datetime <= now < end_datetime:
			live_status = "is_upcoming"
			noformats_expected = True
			noformats_msg = "Programme has not finished airing yet."
			noformats_force = True

		region = self._get_station_region(station)
		station_meta = self._get_station_meta(region, station)
		chapters = self._extract_chapters(station, start_datetime, end_datetime, video_id=meta["id"])
		auth_data = self._auth(region)
		formats = self._get_station_formats(station, True, auth_data, start_at=times[0], end_at=times[1])

		if len(formats) == 0 or noformats_force:
			self.raise_no_formats(noformats_msg, video_id=meta["id"], expected=noformats_expected)
			formats = []

		return {
			**station_meta,
			"alt_title": None,
			**meta,
			"chapters": chapters,
			"formats": formats,
			"live_status": live_status,
			"container": "m4a_dash",  # force fixup, AAC-only HLS
		}


class RadikoSearchIE(_RadikoBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/#!/search/(?:timeshift|live|history)\?"
	_TESTS = [{
		# past, specific area
		'url': 'https://radiko.jp/#!/search/live?key=city%20chill%20club&filter=past&start_day=&end_day=&region_id=&area_id=JP13&cul_area_id=JP13&page_idx=0',
		'playlist_mincount': 4,
		'info_dict': {
			'id': "city chill club-past-all-JP13",
			'title': "city chill club",
		}
	}, {
		# all, specific day
		"url": "https://radiko.jp/#!/search/live?key=CIAO%20765(7%E6%99%82%E5%8F%B0)&filter=&start_day=2023-06-12&end_day=2023-06-12&region_id=all&area_id=JP13&cul_area_id=JP13&page_idx=0",
		"playlist_mincount": 1,
		"info_dict": {
			"id": "CIAO 765(7時台)-all-2023-06-12-all",
			"title": "CIAO 765(7時台)",
		}
	}, {
		# all, live/future
		"url": "https://radiko.jp/#!/search/live?key=%EF%BC%AE%EF%BC%A8%EF%BC%AB%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9&filter=future&start_day=&end_day=&region_id=all&area_id=JP13&cul_area_id=JP13&page_idx=0",
		"playlist_mincount": 8,
		"info_dict": {
			"id": "ＮＨＫニュース-future-all-all",
			"title": "ＮＨＫニュース",
		},
	}]

	def _strip_date(self, date):
		return date.replace(" ", "").replace("-", "").replace(":", "")

	def _real_extract(self, url):
		url = url.replace("/#!/", "/!/", 1)
		# urllib.parse interprets the path as just one giant fragment because of the #, so we hack it away
		queries = parse_qs(url)

		search_url = update_url_query("https://radiko.jp/v3/api/program/search", {
			**queries,
			"uid": secrets.token_hex(16),
			"app_id": "pc",
		})
		data = self._download_json(search_url, None)
		results = [(i.get("station_id"), self._strip_date(i.get("start_time"))) for i in data.get("data")]

		key = traverse_obj(queries, ("key", 0))
		day = traverse_obj(queries, ('start_day', 0)) or "all"
		region = traverse_obj(queries, ("region_id", 0)) or traverse_obj(queries, ("area_id", 0))
		status_filter = traverse_obj(queries, ("filter", 0)) or "all"

		playlist_id = join_nonempty(key, status_filter, day, region)

		return {
			"_type": "playlist",
			"title": traverse_obj(queries, ("key", 0)),
			"id": playlist_id,
			"entries": [self.url_result(f"https://radiko.jp/#!/ts/{station}/{time}", RadikoTimeFreeIE)
				for station, time in results]
		}

class RadikoShareIE(_RadikoBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/share/"
	_TESTS = [{
		# 29-hour time -> 24-hour time
		"url": "http://radiko.jp/share/?sid=FMT&t=20230612240000",
		"info_dict": {
			"ext": "m4a",
			"id": "FMT-20230613000000",
			"title": "JET STREAM",
			'channel_url': 'https://www.tfm.co.jp/',
			'duration': 3300,
			'timestamp': 1686582000,
			'channel_id': 'FMT',
			'cast': ['福山\u3000雅治'],
			'channel': 'TOKYO FM',
			'thumbnail': 'md5:e7b291ff01e2ffdf634851ec9a04cd3e',
			'series': 'JET STREAM',
			'uploader_url': 'https://www.tfm.co.jp/',
			'release_date': '20230612',
			'release_timestamp': 1686585300,
			'description': 'md5:bae47b6fb24d96a75b20db8a986b9cfc',
			'upload_date': '20230612',
			'tags': ['福山雅治', '夜間飛行', '音楽との出会いが楽しめる', '朗読を楽しめる', '寝る前に聴きたい'],
			'live_status': 'was_live',
		}
	}]

	def _real_extract(self, url):
		queries = parse_qs(url)
		station = traverse_obj(queries, ("sid", 0))
		time = traverse_obj(queries, ("t", 0))

		hour = int(time[8:10])
		if hour >= 24: # 29-hour time is valid here, see _unfuck_day in RadikoTimeFreeIE
			hour = hour - 24 # move back by a day

			date = datetime.datetime(int(time[:4]), int(time[4:6]), int(time[6:8]),
				hour=hour, minute=int(time[10:12]), second=int(time[12:14]))

			date += datetime.timedelta(days=1) # move forward a day in datetime to compensate
			time = date.strftime("%Y%m%d%H%M%S")

		return self.url_result(f"https://radiko.jp/#!/ts/{station}/{time}", RadikoTimeFreeIE)


class RadikoStationButtonIE(_RadikoBaseIE):
	_VALID_URL = r"https://radiko\.jp/button-embed/live/"
	_EMBED_REGEX = [fr"<iframe[^>]+src=[\"'](?P<url>{_VALID_URL}[^\"']+)"]

	_TESTS = [{
		"url": "https://radiko.jp/button-embed/live/?layout=1&station_id=QRR&theme=0",
		"info_dict": {
			"id": "QRR",
			"title": "re:^文化放送.+$",
			"ext": "m4a",
			'live_status': 'is_live',
			'channel_id': 'QRR',
			'alt_title': 'JOQR BUNKA HOSO',
			'channel': '文化放送',
			'uploader_url': 'http://www.joqr.co.jp/',
			'channel_url': 'http://www.joqr.co.jp/',
			'thumbnail': 'https://radiko.jp/res/banner/QRR/20201007125706.png',
		}
	}]

	_WEBPAGE_TESTS = [{
		"url": "https://www.tbsradio.jp/",
		"info_dict": {
			"id": "TBS",
			"title": "re:^TBSラジオ.+$",
			"ext": "m4a",
			'uploader_url': 'https://www.tbsradio.jp/',
			'thumbnail': 'https://radiko.jp/res/banner/TBS/20200331114320.jpg',
			'alt_title': 'TBS RADIO',
			'channel_url': 'https://www.tbsradio.jp/',
			'channel': 'TBSラジオ',
			'channel_id': 'TBS',
			'live_status': 'is_live',
		}
	}, {
		"url": "https://cocolo.jp/",
		"info_dict": {
			"id": "CCL",
			"title": "re:^FM COCOLO.+$",
			"ext": "m4a",
			'thumbnail': 'https://radiko.jp/res/banner/CCL/20161014144826.png',
			'channel': 'FM COCOLO',
			'uploader_url': 'https://cocolo.jp',
			'channel_id': 'CCL',
			'live_status': 'is_live',
			'channel_url': 'https://cocolo.jp',
			'alt_title': 'FM COCOLO',
		}
	}, {
		"url": "https://www.joqr.co.jp/qr/dailyprogram/",
		"info_dict": {
			"id": "QRR",
			"title": "re:^文化放送.+$",
			"ext": "m4a",
			'live_status': 'is_live',
			'channel_id': 'QRR',
			'alt_title': 'JOQR BUNKA HOSO',
			'channel': '文化放送',
			'uploader_url': 'http://www.joqr.co.jp/',
			'channel_url': 'http://www.joqr.co.jp/',
			'thumbnail': 'https://radiko.jp/res/banner/QRR/20201007125706.png',
		}
	}]

	def _real_extract(self, url):
		queries = parse_qs(url)
		station = traverse_obj(queries, ("station_id", 0))

		return self.url_result(f"https://radiko.jp/#!/live/{station}", RadikoLiveIE)
