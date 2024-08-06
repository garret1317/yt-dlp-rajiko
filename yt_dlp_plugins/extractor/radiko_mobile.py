import re

from yt_dlp.utils import (
	clean_html,
	join_nonempty,
	traverse_obj,
	update_url_query
)
import yt_dlp_plugins.extractor.radiko_time as rtime
from yt_dlp_plugins.extractor.radiko import _RadikoBaseIE, RadikoTimeFreeIE


class _RadikoMobileBaseIE(_RadikoBaseIE):
	_MOBILE_USER_AGENT = 'Mozilla/5.0 (Linux; Android 10; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Mobile Safari/537.36'

	def _get_nextjs_data(self, url, video_id):
		html = self._download_webpage(url, video_id, headers={"User-Agent": self._MOBILE_USER_AGENT})
		data = self._search_nextjs_data(html, video_id)
		return traverse_obj(data, ("props", "pageProps")), data

	def _get_station_region(self, station):
		api_url = update_url_query("https://radiko.jp/api/stations/batchGetStations", {"stationId": station})
		data = self._download_json(api_url, station, note="Getting station regions")
		return traverse_obj(data, ("stationList", lambda _, v: v["id"] == station, "prefecturesList"), get_all=False)

	_extract_chapters = RadikoTimeFreeIE._extract_chapters

	def _get_programme_meta(self, program, actors=None):
		if actors is not None:
			cast = []
			for actor_id in program.get("actorIdsList"):
				cast.append(traverse_obj(actors, ("actorsList", lambda _, v: v["key"] == actor_id, "name"), get_all=None))
		else:
			cast = traverse_obj(program, (
				'performer', {lambda x: re.split(r'[/／、　,，]', x)}, ..., {str.strip})) or None

		start = traverse_obj(program, ("startAt", "seconds"))
		end = traverse_obj(program, ("endAt", "seconds"))
		old_timestring = rtime.RadikoTime.fromtimestamp(start, tz=rtime.JST).timestring()

		return {
			**traverse_obj(program, {
				"id": "id",
				"title": "title",
				"series": "rSeasonName",
				"tags": "tagsList",
				"thumbnail": "imageUrl",

				"channel": "stationName",
				"channel_id": "stationId",
				"uploader": "stationName",
				"uploader_id": "stationId",
			}),
			"description": clean_html(join_nonempty("summary", "description", from_dict=program, delim="\n")),
			"cast": cast,
			"timestamp": start,
			"release_timestamp": end,
			"duration": end - start,
			"_old_archive_ids": [join_nonempty(program.get("stationId"), old_timestring)],
		}

	def _extract_episode(self, program, actors=None):
		meta = self._get_programme_meta(program, actors)
		station = meta.get("channel_id")
		start = rtime.RadikoTime.fromtimestamp(meta.get("timestamp"), tz=rtime.JST)
		end = rtime.RadikoTime.fromtimestamp(meta.get("release_timestamp"), tz=rtime.JST)

		chapters = self._extract_chapters(station, start, end, video_id=meta["id"])
		area = self._get_station_region(station)[0]
		auth_data = self._auth(area)
		formats = self._get_station_formats(station, True, auth_data, start_at=start, end_at=end)

		return {
			**meta,
			"chapters": chapters,
			"formats": formats,
			"live_status": "was_live",
			"container": "m4a_dash",  # force fixup, AAC-only HLS
		}


class RadikoMobileEventIE(_RadikoMobileBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/mobile/events/(?P<id>[0-9-]+$)"
	_TESTS = [{
		"url": "https://radiko.jp/mobile/events/10282949",
		"info_dict": {
			"live_status": "was_live",
			"ext": "m4a",
			"id": "10282949",
			"_old_archive_ids": ["INT-20240802230000"],

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
			"uploader": "interfm",
			"uploader_id": "INT",

			"cast": ["松浦俊夫"],
			"tags": ["松浦俊夫"],
		},
	}]

	def _real_extract(self, url):
		event_id = self._match_id(url)
		pageProps, data = self._get_nextjs_data(url, event_id)
		return self._extract_episode(pageProps.get("program"), pageProps.get("actors"))


class RadikoMobileSeasonsIE(_RadikoMobileBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/(?:mobile/)?r_seasons/(?P<id>\d+$)"

	def _real_extract(self, url):
		season_id = self._match_id(url)
		pageProps, data = self._get_nextjs_data(url, season_id)

		def entries():
			for episode in pageProps.get("pastPrograms"):
				yield self._extract_episode(episode, pageProps.get("actors"))

		return self.playlist_result(entries(), playlist_id=season_id, playlist_count=len(pageProps.get("pastPrograms")))
