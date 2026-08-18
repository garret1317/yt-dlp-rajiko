import datetime
import dataclasses
import random
import struct

from yt_dlp_plugins.extractor.radiko_dependencies import protobug

from yt_dlp.extractor.common import InfoExtractor
import yt_dlp_plugins.extractor.radiko_time as rtime

from yt_dlp.utils import (
	ExtractorError,
	clean_html,
	get_first,
	join_nonempty,
	make_archive_id,
	url_or_none,
	str_or_none,
	traverse_obj,
)

if protobug:
	from yt_dlp_plugins.extractor.radiko_protos import(
		BoolValue, Timestamp,
		SignInRequest, SignInResponse, SignUpRequest,
		GetRSeasonRequest, GetRSeasonResponse,
		SearchProgramsRequest, SearchProgramsResponse,
		GetActorRequest, GetActorResponse,
		GetPodcastEpisodeRequest, GetPodcastEpisodeResponse,
		GetPodcastChannelRequest, GetPodcastChannelResponse,
		ListPodcastEpisodesRequest, ListPodcastEpisodesResponse,
	)


class _RadikoGRPCBaseIE(InfoExtractor):
	def __add_grpc_header(self, protobuf_data):
		compression_flag = 0
		message_length = len(protobuf_data)
		header = struct.pack('>BI', compression_flag, message_length)
		return header + protobuf_data

	def __strip_grpc_response(self, response):
		# TODO: do this properly https://kreya.app/blog/grpc-web-deep-dive/#grpc-web-trailers-in-disguise
		return response[5:].rpartition(b"grpc-status:")[0]

	def _download_grpc(self, url_or_request, video_id, response_message, note="Downloading GRPC information", *args, **kwargs):
		#TODO: do this properly with __create_download_methods ?

		urlh = self._request_webpage(url_or_request, video_id,
			headers={
				'Content-Type': 'application/grpc-web+proto',
				'X-User-Agent': 'grpc-web-javascript/0.1',
				'X-Grpc-Web': '1',
				**(kwargs.pop("headers", None) or {})
			},
			data=self.__add_grpc_header(protobug.dumps(kwargs.pop('data'))), note=note,
			*args, **kwargs,
		)
		response = urlh.read()

		protobuf = self.__strip_grpc_response(response)
		if len(protobuf) > 0:
			return protobug.loads(protobuf, response_message)
		else:
			#TODO
			self.write_debug(response)
			self.write_debug(urlh.headers)
			if fatal:
				cause = urlh.headers["grpc-message"]
				raise ExtractorError(f"API returned {cause}")


	def sign_up(self):
		lsid = ''.join(random.choices('0123456789abcdef', k=32))

		signup = self._download_grpc("https://api.annex.radiko.jp/radiko.UserService/SignUp",
			"UserService", None, note="Registering ID", headers={'Origin': 'https://radiko.jp'},
			data=SignUpRequest(dataId=lsid),
		)
		# youre meant to only do the sign up ^ once and then keep your lsid for later
		# so that you can sign in and get the token for the API to work
		return lsid


	def sign_in(self, lsid):
		sign_in = self._download_grpc("https://api.annex.radiko.jp/radiko.UserService/SignIn",
			"UserService", SignInResponse, note="Getting auth token", headers={'Origin': 'https://radiko.jp'},
			data=SignInRequest(dataId=lsid, prefecture="JP13"),
		)
		return sign_in.jwtToken


	def auth_userservice(self):
		lsid = self.sign_up()
		jwt = self.sign_in(lsid)
		return jwt


	def _real_initialize(self):
		if not protobug:
			raise ExtractorError("The \"protobug\" library is required for this extractor.\nIf you installed yt-dlp-rajiko manually (with the .whl), use the .zip bundle instead. If you installed with pip, pip install protobug .", expected=True)

		self._jwt = self.auth_userservice()

	def _programs_entries(self, Programs):
		for episode in Programs:

			station = traverse_obj(episode, ("stationId"))
			start = traverse_obj(episode, ("startAt", "seconds"))
			timestring = rtime.RadikoTime.fromtimestamp(start, tz=rtime.JST).timestring()

			timefree_id = join_nonempty(station, timestring)
			timefree_url = f"https://radiko.jp/#!/ts/{station}/{timestring}"

			yield self.url_result(timefree_url, video_id=timefree_id)

	def _get_nextjs(self, html, key, video_id):
		return get_first(self._search_nextjs_v13_data(html, video_id), key)

	def _get_past_Programs(self, video_id, **kwargs):
		now = rtime.RadikoTime.now(tz=rtime.JST)
		min_start = (now - datetime.timedelta(days=30)).broadcast_day_start()
		return self._download_grpc(
			"https://api.annex.radiko.jp/radiko.ProgramService/SearchPrograms",
			video_id,
			SearchProgramsResponse,
			headers={'Authorization': f'Bearer {self._jwt}'},
			data=SearchProgramsRequest(
				isSearchEvent=BoolValue(value=True),
				startAtLt=Timestamp(seconds=int(now.timestamp())),
				startAtGte=Timestamp(seconds=int(min_start.timestamp())),
				sortKey="introduction_start_at",
				timefreeDays=30,
				limit=20,
				**kwargs
			),
		)



class RadikoRSeasonsIE(_RadikoGRPCBaseIE):
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
		# issues with extracting nextjs data
		"url": "https://radiko.jp/r_seasons/10012174",
		"playlist_mincount": 4,
		"info_dict": {
			"id": "10012174",
			"title": "日向坂46の「ひ」",
			"description": "md5:5701c7fa92c41233c0c988a1d079a6ee",
			'thumbnail': 'https://program-static.cf.radiko.jp/b244348d-daab-42ef-876f-243a4475ebd4.jpeg',
		}
	}]

	def _real_extract(self, url):
		season_id = self._match_id(url)

		rSeason = self._download_grpc(
			"https://api.annex.radiko.jp/radiko.RSeasonService/GetRSeason",
			season_id,
			GetRSeasonResponse,
			data=GetRSeasonRequest(rSeasonId=season_id),
		)

		rSeason = dataclasses.asdict(rSeason)["rSeason"]
		season_id = traverse_obj(rSeason, "id") or season_id
		programs = self._get_past_Programs(season_id, rSeasonId=season_id)

		return self.playlist_result(
			self._programs_entries(dataclasses.asdict(programs)["programs"]),
			playlist_id=season_id,
			**traverse_obj(rSeason, {
				"playlist_title": "rSeasonName",
				"thumbnail": "backgroundImageUrl",
				"description": ("summary", filter),
			}),
		)

class RadikoPersonIE(_RadikoGRPCBaseIE):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/persons/(?P<id>\d+)"
	_TESTS = [{
		"url": "https://radiko.jp/persons/11421",
		"playlist_mincount": 1,
		"info_dict": {
			"id": "11421",
			'title': '森山良子',
			'description': 'md5:bbf061fc22c6a740927cfa7186d984d2',
			'_old_archive_ids': ['radikoperson person-11421'],
		},
	}, {
		# issues with next.js
		"url": "https://radiko.jp/persons/33901",
		"playlist_mincount": 1,
		"info_dict": {
			"id": "33901",
			'title': '大友良英',
			'_old_archive_ids': ['radikoperson person-33901'],
		},
	}]

	def _real_extract(self, url):
		person_id = self._match_id(url)

		person_metadata = dataclasses.asdict(self._download_grpc("https://actor-and-article.annex.radiko.jp/radiko.ActorService/GetActor",
			person_id, GetActorResponse, note="Downloading person metadata", data=GetActorRequest(actorKey=person_id),
		))["actor"]
		programs = dataclasses.asdict(self._get_past_Programs(person_id, actorId=person_id))["programs"]

		return self.playlist_result(
			self._programs_entries(programs),
			playlist_id=person_id,
			**traverse_obj(person_metadata, {
				"playlist_title": "name",
				"description": "description",
			}),
			_old_archive_ids=[make_archive_id(self, join_nonempty("person", person_id))]
		)


class _RadikoPodcastBaseIE(_RadikoGRPCBaseIE):

	def _extract_episode(self, episode_info):
		return {
			**traverse_obj(episode_info, {
				"id": ("id", {str_or_none}),
				"url": ("audio", "url"),
				"duration": ("audio", "durationSec"),

				"title": "title",
				"description": ("description", {clean_html}),
				"timestamp": ("startAt", "seconds"),

				"series": "channelTitle",
				"series_id": "channelId",
				"channel": "channelStationName",
				"uploader": "channelStationName",
			}),
			"thumbnail": traverse_obj(episode_info, ("imageUrl", {url_or_none}))
				or traverse_obj(episode_info, ("channelImageUrl", {url_or_none})),

			# so that --download-archive still works if you download from the playlist page
			"webpage_url": "https://radiko.jp/podcast/episodes/{id}".format(id=traverse_obj(episode_info, "id")),
			'extractor_key': RadikoPodcastEpisodeIE.ie_key(),
			'extractor': 'RadikoPodcastEpisode',
		}

class RadikoPodcastEpisodeIE(_RadikoPodcastBaseIE):
	_VALID_URL = r"https?://radiko\.jp/podcast/episodes/(?P<id>[a-f0-9-]+)"

	_TESTS = [{
		"url": "https://radiko.jp/podcast/episodes/cc8cf709-a50b-4846-aa0e-91ab10cf8bff",
		"info_dict": {
			"id": "cc8cf709-a50b-4846-aa0e-91ab10cf8bff",
			"ext": "mp3",
			'title': '2025.6.26 おしゃべり技術くん',
			'description': 'md5:1c4048025f68d6da053dd879a5d62304',
			'duration': 717,
			'thumbnail': 'https://podcast-static.cf.radiko.jp/09f27a48-ae04-4ce7-a024-572460e46eb7-20240214160012.png',
			'series': 'おしゃべり技術くん',
			'series_id': '09f27a48-ae04-4ce7-a024-572460e46eb7',
			'timestamp': 1751554800,
			'upload_date': '20250703',
			'uploader': 'IBCラジオ',
			'channel': 'IBCラジオ',
		},
	}]

	def _real_extract(self, url):
		video_id = self._match_id(url)
		episode_info = dataclasses.asdict(self._download_grpc("https://api.annex.radiko.jp/radiko.PodcastService/GetPodcastEpisode",
			video_id, GetPodcastEpisodeResponse, data=GetPodcastEpisodeRequest(id=video_id)))["episode"]
		return self._extract_episode(episode_info)


class RadikoPodcastChannelIE(_RadikoPodcastBaseIE):
	_VALID_URL = r"https?://radiko\.jp/podcast/channels/(?P<id>[a-f0-9-]+)"

	_TESTS = [{
		"url": "https://radiko.jp/podcast/channels/09f27a48-ae04-4ce7-a024-572460e46eb7",
		"info_dict": {
			"id": "09f27a48-ae04-4ce7-a024-572460e46eb7"
		},
		'playlist_mincount': 21,
	}]

	def _real_extract(self, url):
		channel_id = self._match_id(url)

		channel_info = dataclasses.asdict(self._download_grpc("https://api.annex.radiko.jp/radiko.PodcastService/GetPodcastChannel",
			channel_id, GetPodcastChannelResponse, data=GetPodcastChannelRequest(id=channel_id)))["channel"]

		def entries():
			has_next_page = True
			cursor = None
			while has_next_page:
				episode_list_response = self._download_grpc('https://api.annex.radiko.jp/radiko.PodcastService/ListPodcastEpisodes',
					channel_id, ListPodcastEpisodesResponse, note="Downloading episode listings",
					headers={'Authorization': f'Bearer {self._jwt}'},
					data=ListPodcastEpisodesRequest(
						channelId=channel_id,
						order=1,
						lastEpisodeId=cursor,
				))

				for episode in episode_list_response.episodes:
					episode = dataclasses.asdict(episode)
					cursor = episode.get("id")
					yield self._extract_episode(episode)

				has_next_page= episode_list_response.hasNextPage

		return {
			"_type": "playlist",
			"id": channel_id,
			**traverse_obj(channel_info, {
				"title": "title",
				"id": "id",
				"description": ("description", {clean_html}),
				"thumbnail": ("imageUrl", {url_or_none}),
			}),
			"entries": entries(),
		}
