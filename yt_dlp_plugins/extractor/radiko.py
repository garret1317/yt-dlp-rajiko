import base64
import datetime
import random
import urllib.parse

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
	# TODO: replace with importlib.resources when yt-dlp minimum python version is new enough
	# https://setuptools.pypa.io/en/latest/userguide/datafiles.html
	_FULL_KEY = base64.b64decode("""
	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
	""")

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

	_MODELS = [
	# Samsung galaxy s7+
	"SC-02H", "SCV33", "SM-G935F", "SM-G935X", "SM-G935W8", "SM-G935K", "SM-G935L", "SM-G935S", "SAMSUNG-SM-G935A", "SM-G935VC", "SM-G9350", "SM-G935P", "SM-G935T", "SM-G935U", "SM-G935R4", "SM-G935V", "SC-02J", "SCV36", "SM-G950F", "SM-G950N", "SM-G950W", "SM-G9500", "SM-G9508", "SM-G950U", "SM-G950U1", "SM-G892A", "SM-G892U", "SC-03J", "SCV35", "SM-G955F", "SM-G955N", "SM-G955W", "SM-G9550", "SM-G955U", "SM-G955U1", "SM-G960F", "SM-G960N", "SM-G9600", "SM-G9608", "SM-G960W", "SM-G960U", "SM-G960U1", "SM-G965F", "SM-G965N", "SM-G9650", "SM-G965W", "SM-G965U", "SM-G965U1",
	# samsung galaxy note
	"SC-01J", "SCV34", "SM-N930F", "SM-N930X", "SM-N930K", "SM-N930L", "SM-N930S", "SM-N930R7", "SAMSUNG-SM-N930A", "SM-N930W8", "SM-N9300", "SGH-N037", "SM-N930R6", "SM-N930P", "SM-N930VL", "SM-N930T", "SM-N930U", "SM-N930R4", "SM-N930V", "SC-01K", "SCV37", "SM-N950F", "SM-N950N", "SM-N950XN", "SM-N950U", "SM-N9500", "SM-N9508", "SM-N950W", "SM-N950U1",
	# KYOCERA
	"WX06K", "404KC", "503KC", "602KC", "KYV32", "E6782", "KYL22", "WX04K", "KYV36", "KYL21", "302KC", "KYV36", "KYV42", "KYV37", "C5155", "SKT01", "KYY24", "KYV35", "KYV41", "E6715", "KYY21", "KYY22", "KYY23", "KYV31", "KYV34", "KYV38", "WX10K", "KYL23", "KYV39", "KYV40",
	# sony xperia z series
	"C6902", "C6903", "C6906", "C6916", "C6943", "L39h", "L39t", "L39u", "SO-01F", "SOL23", "D5503", "M51w", "SO-02F", "D6502", "D6503", "D6543", "SO-03F", "SGP511", "SGP512", "SGP521", "SGP551", "SGP561", "SO-05F", "SOT21", "D6563", "401SO", "D6603", "D6616", "D6643", "D6646", "D6653", "SO-01G", "SOL26", "D6603", "D5803", "D5833", "SO-02G", "D5803", "D6633", "D6683", "SGP611", "SGP612", "SGP621", "SGP641", "E6553", "E6533", "D6708", "402SO", "SO-03G", "SOV31", "SGP712", "SGP771", "SO-05G", "SOT31", "E6508", "501SO", "E6603", "E6653", "SO-01H", "SOV32", "E5803", "E5823", "SO-02H", "E6853", "E6883", "SO-03H", "E6833", "E6633", "E6683", "C6502", "C6503", "C6506", "L35h", "SOL25", "C5306", "C5502", "C5503", "601SO", "F8331", "F8332", "SO-01J", "SOV34", "G8141", "G8142", "G8188", "SO-04J", "701SO", "G8341", "G8342", "G8343", "SO-01K", "SOV36", "G8441", "SO-02K", "602SO", "G8231", "G8232", "SO-03J", "SOV35",
	# sharp
	"605SH", "SH-03J", "SHV39", "701SH", "SH-M06",
	# fujitsu arrows
	"101F", "201F", "202F", "301F", "IS12F", "F-03D", "F-03E", "M01", "M305", "M357", "M555", "M555", "F-11D", "F-06E", "EM01F", "F-05E", "FJT21", "F-01D", "FAR70B", "FAR7", "F-04E", "F-02E", "F-10D", "F-05D", "FJL22", "ISW11F", "ISW13F", "FJL21", "F-074", "F-07D",
]

	# range detail :http://www.gsi.go.jp/KOKUJYOHO/CENTER/zenken.htm

	# build number :https://www.androidpolice.com/android-build-number-date-calculator/
	# https://source.android.com/setup/build-numbers
	_ANDROID_VERSIONS = [
		# According to https://radiko.jp/#!/info/2558, apparently - link doesnt seem to exist any more
		{"version": "7.0.0", "sdk": "24", "builds": ["NBD92Q", "NBD92N", "NBD92G", "NBD92F", "NBD92E", "NBD92D", "NBD91Z", "NBD91Y", "NBD91X", "NBD91U", "N5D91L", "NBD91P", "NRD91K", "NRD91N", "NBD90Z", "NBD90X", "NBD90W", "NRD91D", "NRD90U", "NRD90T", "NRD90S", "NRD90R", "NRD90M"]},
		{"version": "7.1.0", "sdk": "25", "builds": ["NDE63X", "NDE63V", "NDE63U", "NDE63P", "NDE63L", "NDE63H"]},
		{"version": "7.1.1", "sdk": "25", "builds": ["N9F27M", "NGI77B", "N6F27M", "N4F27P", "N9F27L", "NGI55D", "N4F27O", "N8I11B", "N9F27H", "N6F27I", "N4F27K", "N9F27F", "N6F27H", "N4F27I", "N9F27C", "N6F27E", "N4F27E", "N6F27C", "N4F27B", "N6F26Y", "NOF27D", "N4F26X", "N4F26U", "N6F26U", "NUF26N", "NOF27C", "NOF27B", "N4F26T", "NMF27D", "NMF26X", "NOF26W", "NOF26V", "N6F26R", "NUF26K", "N4F26Q", "N4F26O", "N6F26Q", "N4F26M", "N4F26J", "N4F26I", "NMF26V", "NMF26U", "NMF26R", "NMF26Q", "NMF26O", "NMF26J", "NMF26H", "NMF26F"]},
		{"version": "7.1.2", "sdk": "25", "builds": ["N2G48H", "NZH54D", "NKG47S", "NHG47Q", "NJH47F", "N2G48C", "NZH54B", "NKG47M", "NJH47D", "NHG47O", "N2G48B", "N2G47Z", "NJH47B", "NJH34C", "NKG47L", "NHG47N", "N2G47X", "N2G47W", "NHG47L", "N2G47T", "N2G47R", "N2G47O", "NHG47K", "N2G47J", "N2G47H", "N2G47F", "N2G47E", "N2G47D"]},
		{"version": "8.0.0", "sdk": "26", "builds": ["5650811", "5796467", "5948681", "6107732", "6127070"]},
		{"version": "8.1.0", "sdk": "27", "builds": ["5794017", "6107733", "6037697"]},
		{"version": "9.0.0", "sdk": "28", "builds": ["5948683", "5794013", "6127072"]},
		{"version": "10.0.0", "sdk": "29", "builds": ["5933585", "6969601", "7023426", "7070703"]},
		{"version": "11.0.0", "sdk": "30", "builds": ["RP1A.201005.006", "RQ1A.201205.011", "RQ1A.210105.002"]},
		{"version": "12.0.0", "sdk": "31", "builds": ["SD1A.210817.015.A4", "SD1A.210817.019.B1", "SD1A.210817.037", "SQ1D.220105.007"]},
	]

	_APP_VERSIONS = ["7.5.0", "7.4.17", "7.4.16", "7.4.15", "7.4.14", "7.4.13", "7.4.12", "7.4.11", "7.4.10", "7.4.9", "7.4.8", "7.4.7", "7.4.6", "7.4.5", "7.4.4", "7.4.3", "7.4.2", "7.4.1", "7.4.0", "7.3.8", "7.3.7", "7.3.6", "7.3.1", "7.3.0", "7.2.11", "7.2.10"]

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
		version_info = random.choice(self._ANDROID_VERSIONS)
		android_version = version_info["version"]
		sdk = version_info["sdk"]
		build = random.choice(version_info["builds"])
		model = random.choice(self._MODELS)

		info = {
			"X-Radiko-App": "aSmartPhone7a",
			"X-Radiko-App-Version": random.choice(self._APP_VERSIONS),
			"X-Radiko-Device": f"{sdk}.{model}",
			"X-Radiko-User": ''.join(random.choices('0123456789abcdef', k=32)),
			"User-Agent": f"Dalvik/2.1.0 (Linux; U; Android {android_version};{model}/{build})",
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

		coords = self._get_coords(station_region)
		headers = {
			**info,
			"X-Radiko-AuthToken": auth_token,
			"X-Radiko-Location": coords,
			"X-Radiko-Connection": "wifi",
			"X-Radiko-Partialkey": partial_key,
		}

		auth2 = self._download_webpage("https://radiko.jp/v2/api/auth2", station_region,
			"Authenticating: step 2", headers=headers)
		self.write_debug(auth2.strip())
		actual_region, region_kanji, region_english = auth2.split(",")

		region_mismatch = actual_region != station_region
		if region_mismatch:
			self.report_warning(f"Region mismatch: Expected {station_region}, got {actual_region}. Coords: {coords}.")
			self.report_warning("Please report this at https://github.com/garret1317/yt-dlp-rajiko/issues")
			self.report_warning(auth2.strip())
			self.report_warning(headers)

		token = {
			"X-Radiko-AreaId": actual_region,
			"X-Radiko-AuthToken": auth_token,
		}

		self._user = headers["X-Radiko-User"]
		if not region_mismatch:
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
			"uploader": "TOKYO FM",
		},
	}, {
		# JP1 (Hokkaido) - shorthand
		"url": "https://radiko.jp/#NORTHWAVE",
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
			'uploader': "FM NORTH WAVE",
		},
	}, {
		# ALL (all prefectures)
		# api still specifies a prefecture though, in this case JP13 (Tokyo), so that's what it auths as
		"url": "https://radiko.jp/#!/live/RN1",
		"info_dict": {
			"id": "RN1",
			"ext": "m4a",
			"title": "re:^ラジオNIKKEI第1.+$",
			'uploader_url': 'http://www.radionikkei.jp/',
			'thumbnail': 'https://radiko.jp/res/banner/RN1/20120802154152.png',
			'live_status': 'is_live',
			'channel_id': 'RN1',
			'alt_title': 'RADIONIKKEI',
			'uploader': 'ラジオNIKKEI第1',
			'channel': 'ラジオNIKKEI第1',
			'channel_url': 'http://www.radionikkei.jp/',
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
			"uid": ''.join(random.choices('0123456789abcdef', k=32)),
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
