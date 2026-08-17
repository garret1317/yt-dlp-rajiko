import datetime
import dataclasses
import random
import struct

from yt_dlp_plugins.extractor.radiko_dependencies import protobug

from yt_dlp.extractor.common import InfoExtractor
import yt_dlp_plugins.extractor.radiko_time as rtime

from yt_dlp.utils import (
	ExtractorError,
	get_first,
	join_nonempty,
	make_archive_id,
	traverse_obj,
)

if protobug:
	from yt_dlp_plugins.extractor.protos import(
		BoolValue, Timestamp,
		SignInRequest, SignInResponse, SignUpRequest,
		GetRSeasonRequest, GetRSeasonResponse,
		SearchProgramsRequest, SearchProgramsResponse,
		GetActorRequest, GetActorResponse,
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
			print(response)
			print(urlh.headers)

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
		# TODO: to cache or not to cache
		cachedata = self.cache.load("rajiko", "UserService")
		if cachedata is not None:
			lsid = cachedata.get("lsid")
		else:
			lsid = self.sign_up()
			self.cache.store("rajiko", "UserService", {"lsid": lsid})
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
