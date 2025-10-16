#!/usr/bin/env python3
import struct
import random

from yt_dlp_plugins.extractor.radiko_dependencies import protobug

if protobug:  # i suppose it works lmao


	def add_grpc_header(protobuf_data):
		compression_flag = 0
		message_length = len(protobuf_data)
		header = struct.pack('>BI', compression_flag, message_length)
		return header + protobuf_data

	def strip_grpc_response(response):
		return response[5:].rpartition(b"grpc-status:")[0]

	def _download_grpc(self, url_or_request, video_id, response_message, note="Downloading GRPC information", *args, **kwargs):
		urlh = self._request_webpage(url_or_request, video_id,
			headers={
				'Content-Type': 'application/grpc-web+proto',
				'X-User-Agent': 'grpc-web-javascript/0.1',
				'X-Grpc-Web': '1',
				**kwargs.pop('headers')
			},
			data=add_grpc_header(protobug.dumps(kwargs.pop('data'))), note=note,
			*args, **kwargs,
		)
		response = urlh.read()

		protobuf = strip_grpc_response(response)
		if len(protobuf) > 0:
			return protobug.loads(protobuf, response_message)


	@protobug.message
	class SignUpRequest:
		lsid: protobug.String = protobug.field(1)

	def sign_up(self):
		lsid = ''.join(random.choices('0123456789abcdef', k=32))

		signup = _download_grpc(self, "https://api.annex.radiko.jp/radiko.UserService/SignUp",
			"UserService", None, note="Registering ID", headers={'Origin': 'https://radiko.jp'},
			data=SignUpRequest(lsid=lsid),
		)
		# youre meant to only do the sign up ^ once and then keep your lsid for later
		# so that you can sign in and get the token for the API to work
		return lsid


	@protobug.message
	class SignInRequest:
		lsid: protobug.String = protobug.field(2)
		area: protobug.String = protobug.field(3)

	@protobug.message
	class SignInResponse:
		jwt: protobug.String = protobug.field(1)


	def sign_in(self, lsid):
		sign_in = _download_grpc(self, "https://api.annex.radiko.jp/radiko.UserService/SignIn",
			"UserService", SignInResponse, note="Getting auth token", headers={'Origin': 'https://radiko.jp'},
			data=SignInRequest(lsid=lsid, area="JP13"),
		)
		return sign_in.jwt


	def auth_userservice(self):
		cachedata = self.cache.load("rajiko", "UserService")
		if cachedata is not None:
			lsid = cachedata.get("lsid")
		else:
			lsid = sign_up(self)
			self.cache.store("rajiko", "UserService", {"lsid": lsid})
		jwt = sign_in(self, lsid)
		return jwt


	@protobug.message
	class ListPodcastEpisodesRequest:
		channel_id: protobug.String = protobug.field(1)
		sort_by_latest: protobug.Bool = protobug.field(2)
		page_length: protobug.Int32 = protobug.field(4)
		cursor: protobug.String = protobug.field(5, default=None)


	@protobug.message
	class Audio:
		revision: protobug.Int32 = protobug.field(1)
		url: protobug.String = protobug.field(2)
		fileSize: protobug.Int64 = protobug.field(3)
		durationSec: protobug.Int64 = protobug.field(4)
		transcoded: protobug.Bool = protobug.field(5)

	@protobug.message
	class EpisodeStartAt:
		seconds: protobug.UInt64 = protobug.field(1)
		nanos: protobug.UInt64 = protobug.field(2, default=0)


	@protobug.message
	class PodcastEpisode:
		id: protobug.String = protobug.field(1)
		workspaceId: protobug.String = protobug.field(2)
		channelId: protobug.String = protobug.field(3)
		title: protobug.String = protobug.field(4)
		description: protobug.String = protobug.field(5)

		audio: Audio = protobug.field(8)
		channelImageUrl: protobug.String = protobug.field(16)
		channelTitle: protobug.String = protobug.field(17)
		channelStationName: protobug.String = protobug.field(18)
		channelAuthor: protobug.String = protobug.field(19)

		channelThumbnailImageUrl: protobug.String = protobug.field(21)
		channelStationType: protobug.UInt32 = protobug.field(22)
		startAt: EpisodeStartAt = protobug.field(27)
		isEnabled: protobug.Bool = protobug.field(29)
		hasTranscription: protobug.Bool = protobug.field(32)

		imageUrl: protobug.String = protobug.field(7, default=None)
		thumbnailImageUrl: protobug.String = protobug.field(20, default=None)

	@protobug.message
	class ListPodcastEpisodesResponse:
		episodes: list[PodcastEpisode] = protobug.field(1)
		hasNextPage: protobug.Bool = protobug.field(2, default=False)


	def get_podcast_episodes(self, channel_id, jwt, cursor, page_length=20):
		# site uses 20 items
		# cursor is the id of the last episode you've seen in the list

		return _download_grpc(self, 'https://api.annex.radiko.jp/radiko.PodcastService/ListPodcastEpisodes',
			channel_id, ListPodcastEpisodesResponse, note="Downloading episode listings",
			headers={'Authorization': f'Bearer {jwt}'},
			data=ListPodcastEpisodesRequest(
				channel_id=channel_id,
				sort_by_latest=True,
				page_length=page_length,
				cursor=cursor,
			)
		)
