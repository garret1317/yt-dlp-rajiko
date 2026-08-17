from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	get_first,
	traverse_obj,
	join_nonempty,
)
import yt_dlp_plugins.extractor.radiko_time as rtime
import protobug
import struct
import random

class _RadikoMobileWebBaseIE(InfoExtractor):

	def _programs_entries(self, Programs):
		for episode in Programs:

#			if traverse_obj(episode, ("keyStationId")) != traverse_obj(episode, ("stationId")):
#				continue
			station = traverse_obj(episode, ("stationId"))
			start = traverse_obj(episode, ("startAt", "seconds"))
			timestring = rtime.RadikoTime.fromtimestamp(start, tz=rtime.JST).timestring()

			timefree_id = join_nonempty(station, timestring)
			timefree_url = f"https://radiko.jp/#!/ts/{station}/{timestring}"

			yield self.url_result(timefree_url, video_id=timefree_id)

	def _get_nextjs(self, html, key, video_id):
		return get_first(self._search_nextjs_v13_data(html, video_id), key)


	def __add_grpc_header(self, protobuf_data):
		compression_flag = 0
		message_length = len(protobuf_data)
		header = struct.pack('>BI', compression_flag, message_length)
		return header + protobuf_data

	def __strip_grpc_response(self, response):
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
			print(response)
			print(urlh.headers)

	from yt_dlp_plugins.extractor.protos import (
		SignUpRequest,
		SignInRequest,
		SignInResponse,
	)

	def sign_up(self):
		from yt_dlp_plugins.extractor.protos import (
			SignUpRequest,
			SignInRequest,
			SignInResponse,
		)

		lsid = ''.join(random.choices('0123456789abcdef', k=32))

		signup = self._download_grpc("https://api.annex.radiko.jp/radiko.UserService/SignUp",
			"UserService", None, note="Registering ID", headers={'Origin': 'https://radiko.jp'},
			data=SignUpRequest(dataId=lsid),
		)
		# youre meant to only do the sign up ^ once and then keep your lsid for later
		# so that you can sign in and get the token for the API to work
		return lsid


	def sign_in(self, lsid):
		from yt_dlp_plugins.extractor.protos import (
			SignUpRequest,
			SignInRequest,
			SignInResponse,
		)

		sign_in = self._download_grpc("https://api.annex.radiko.jp/radiko.UserService/SignIn",
			"UserService", SignInResponse, note="Getting auth token", headers={'Origin': 'https://radiko.jp'},
			data=SignInRequest(dataId=lsid, prefecture="JP13"),
		)
		return sign_in.jwtToken


	def auth_userservice(self):
		cachedata = self.cache.load("rajiko", "UserService")
		if cachedata is not None:
			lsid = cachedata.get("lsid")
		else:
			lsid = self.sign_up()
			self.cache.store("rajiko", "UserService", {"lsid": lsid})
		jwt = self.sign_in(lsid)
		return jwt
