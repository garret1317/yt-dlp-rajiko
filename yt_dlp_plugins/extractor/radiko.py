import base64
import datetime
import random
import secrets
import urllib.parse
import yt_dlp_plugins.extractor.radiko_key as key

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
			self.write_debug(f"station {station} not found, re-indexing in case it's new")
			regions = self._index_regions()

		return regions[station]

	def _negotiate_token(self, station_region):
		info = self._generate_random_info()
		response, auth1_handle = self._download_webpage_handle("https://radiko.jp/v2/api/auth1", None,
			"Authenticating: step 1", headers=info)

		self.write_debug(response)

		auth1_header = auth1_handle.headers
		auth_token = auth1_header["X-Radiko-AuthToken"]
		key_length = int(auth1_header["X-Radiko-KeyLength"])
		key_offset = int(auth1_header["X-Radiko-KeyOffset"])

		self.write_debug(f"KeyLength: {key_length}")
		self.write_debug(f"KeyOffset: {key_offset}")

		raw_partial_key = self._FULL_KEY[key_offset:key_offset + key_length]
		partial_key = base64.b64encode(raw_partial_key).decode("ascii")

		self.write_debug(partial_key)

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
			self.cache.store("rajiko", station_id, {
				"expiry": (now + datetime.timedelta(days=1)).timestamp(), "meta": meta})
			return meta
		else:
			self.to_screen(f"{station_id}: Using cached station metadata")
			return cachedata.get("meta")

	def _get_station_formats(self, station, timefree, auth_data, start_at=None, end_at=None):
		device = self._configuration_arg('device', ['aSmartPhone7a'], casesense=True)[0]  # aSmartPhone7a formats = always happy path
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
					"l": "15",
					"lsid": self._user,
					"type": "b",
				})
			if timefree:
				playlist_url = update_url_query(playlist_url, {
					"start_at": start_at.timestring(),
					"ft": start_at.timestring(),
					"end_at": end_at.timestring(),
					"to": end_at.timestring(),
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
		"url": "https://radiko.jp/#!/ts/INT/20230818230000",
		"info_dict": {
			"id": "INT-20230818230000",
			"title": "TOKYO MOON",
			"ext": "m4a",
			'tags': ['松浦俊夫'],
			'cast': ['松浦\u3000俊夫'],
			'channel_url': 'https://www.interfm.co.jp/',
			'channel_id': 'INT',
			'description': 'md5:804d83142a1ef1dfde48c44fb531482a',
			'upload_date': '20230818',
			'thumbnail': 'https://radiko.jp/res/program/DEFAULT_IMAGE/INT/72b3a65f-c3ee-4892-a327-adec52076d51.jpeg',
			'chapters': 'count:16',
			'release_timestamp': 1692370800,
			'live_status': 'was_live',
			'series': 'Tokyo Moon',
			'timestamp': 1692367200,
			'uploader_url': 'https://www.interfm.co.jp/',
			'uploader': 'interfm',
			'channel': 'interfm',
			'duration': 3600,
			'release_date': '20230818',
		},
	}, {
		"url": "https://radiko.jp/#!/ts/NORTHWAVE/20230820173000",
		"info_dict": {
			"id": "NORTHWAVE-20230820173000",
			"title": "角松敏生 My BLUES LIFE",
			"ext": "m4a",
			'cast': ['角松\u3000敏生'],
			'tags': ['ノースウェーブ', '角松敏生', '人気アーティストトーク'],
			'channel_id': 'NORTHWAVE',
			'series': '角松敏生 My BLUES LIFE',
			'uploader_url': 'https://www.fmnorth.co.jp/',
			'upload_date': '20230820',
			'channel_url': 'https://www.fmnorth.co.jp/',
			'release_timestamp': 1692522000,
			'channel': 'FM NORTH WAVE',
			'uploader': 'FM NORTH WAVE',
			'thumbnail': 'https://radiko.jp/res/program/DEFAULT_IMAGE/NORTHWAVE/cwqcdppldk.jpg',
			'chapters': 'count:5',
			'duration': 1800,
			'release_date': '20230820',
			'live_status': 'was_live',
			'description': 'md5:027860a5731c04779b6720047c7b8b59',
			'timestamp': 1692520200,
		},
	}, {
		# late-night show, see comment in _unfuck_day
		"url": "https://radiko.jp/#!/ts/TBS/20230824030000",
		"info_dict": {
			"id": "TBS-20230824030000",
			"title": "CITY CHILL CLUB",
			"ext": "m4a",
			'series': 'CITY CHILL CLUB',
			'timestamp': 1692813600,
			'description': 'md5:09327f9bfe9cfd3a4d4d20d86c15031f',
			'duration': 7200,
			'channel_url': 'https://www.tbsradio.jp/',
			'cast': ['tonun'],
			'upload_date': '20230823',
			'release_date': '20230823',
			'live_status': 'was_live',
			'chapters': 'count:28',
			'uploader': 'TBSラジオ',
			'release_timestamp': 1692820800,
			'thumbnail': 'https://radiko.jp/res/program/DEFAULT_IMAGE/TBS/ev6ru67jz8.jpg',
			'uploader_url': 'https://www.tbsradio.jp/',
			'channel_id': 'TBS',
			'tags': ['CCC905', '音楽との出会いが楽しめる', '人気アーティストトーク', '音楽プロデューサー出演', 'ドライブ中におすすめ', '寝る前におすすめ', '学生におすすめ'],
			'channel': 'TBSラジオ',
		},
	}, {
		# early-morning show, same reason
		"url": "https://radiko.jp/#!/ts/TBS/20230824050000",
		"info_dict": {
			"id": "TBS-20230824050000",
			"title": "生島ヒロシのおはよう定食・一直線",
			"ext": "m4a",
			'uploader_url': 'https://www.tbsradio.jp/',
			'channel_id': 'TBS',
			'channel_url': 'https://www.tbsradio.jp/',
			'tags': ['生島ヒロシ', '健康', '檀れい', '朝のニュースを効率良く'],
			'release_timestamp': 1692826200,
			'release_date': '20230823',
			'cast': ['生島\u3000ヒロシ'],
			'description': 'md5:1548ed6495813baebf579d6a4d210665',
			'upload_date': '20230823',
			'chapters': 'count:2',
			'timestamp': 1692820800,
			'uploader': 'TBSラジオ',
			'live_status': 'was_live',
			'thumbnail': 'https://radiko.jp/res/program/DEFAULT_IMAGE/TBS/ch3vcvtc5e.jpg',
			'channel': 'TBSラジオ',
			'series': '生島ヒロシのおはよう定食・一直線',
			'duration': 5400,

		},
	}]

	def _get_programme_meta(self, station_id, url_time):
		day = url_time.broadcast_day()
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
		start_str = urllib.parse.quote(start.isoformat())
		end_str = urllib.parse.quote(end.isoformat())
		data = self._download_json(f"https://api.radiko.jp/music/api/v1/noas/{station}?start_time_gte={start_str}&end_time_lt={end_str}",
			video_id, note="Downloading tracklist").get("data")

		chapters = []
		for track in data:
			artist = traverse_obj(track, ("artist", "name")) or track.get("artist_name")
			chapters.append({
				"title": join_nonempty(artist, track.get("title"), delim=" - "),
				"start_time": (datetime.datetime.fromisoformat(track.get("displayed_start_time")) - start.datetime).total_seconds(),
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
		end_day = end.broadcast_day_end()

		now = datetime.datetime.now(tz=rtime.JST)

		if end_day < now - datetime.timedelta(days=7):
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


class RadikoSearchIE(_RadikoBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/#!/search/(?:timeshift|live|history)\?"
	_TESTS = [{
		# timefree, specific area
		'url': 'https://radiko.jp/#!/search/live?key=city%20chill%20club&filter=past&start_day=&end_day=&region_id=&area_id=JP13&cul_area_id=JP13&page_idx=0',
		'playlist_mincount': 4,
		'info_dict': {
			'id': "city chill club-past-all-JP13",
			'title': "city chill club",
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
			"uid": secrets.token_hex(16),
			"app_id": "pc",
			"row_limit": 50,  # higher row_limit = more results = less requests = more good
		})

		results = OnDemandPagedList(lambda idx: self._pagefunc(search_url, idx), 50)

		key = traverse_obj(queries, ("key", 0))
		day = traverse_obj(queries, ('start_day', 0)) or "all"
		region = traverse_obj(queries, ("region_id", 0)) or traverse_obj(queries, ("area_id", 0))
		status_filter = traverse_obj(queries, ("filter", 0)) or "all"

		playlist_id = join_nonempty(key, status_filter, day, region)

		return {
			"_type": "playlist",
			"title": traverse_obj(queries, ("key", 0)),
			"id": playlist_id,
			"entries": results,
		}

class RadikoShareIE(_RadikoBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/share/"
	_TESTS = [{
		# 29-hour time -> 24-hour time
		"url": "http://radiko.jp/share/?sid=FMT&t=20230822240000",
		"info_dict": {
			"ext": "m4a",
			"id": "FMT-20230823000000",
			"title": "JET STREAM",
			'chapters': list,
			'uploader': 'TOKYO FM',
			'release_date': '20230822',
			'tags': ['福山雅治', '夜間飛行', '音楽との出会いが楽しめる', '朗読を楽しめる', '寝る前に聴きたい'],
			'release_timestamp': 1692719700.0,
			'upload_date': '20230822',
			'thumbnail': 'https://radiko.jp/res/program/DEFAULT_IMAGE/FMT/greinlrspi.jpg',
			'cast': ['福山\u3000雅治'],
			'series': 'JET STREAM',
			'live_status': 'was_live',
			'uploader_url': 'https://www.tfm.co.jp/',
			'description': 'md5:d41232c4f216103f4e825ccb2d883c3b',
			'channel_id': 'FMT',
			'timestamp': 1692716400.0,
			'duration': 3300,
			'channel': 'TOKYO FM',
			'channel_url': 'https://www.tfm.co.jp/',
		}
	}]

	def _real_extract(self, url):
		queries = parse_qs(url)
		station = traverse_obj(queries, ("sid", 0))
		time = traverse_obj(queries, ("t", 0))
		time = rtime.RadikoShareTime(time).timestring()
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
