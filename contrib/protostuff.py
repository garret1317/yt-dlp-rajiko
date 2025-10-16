#!/usr/bin/env python3

import protobug
import base64
import struct

import random
import requests

@protobug.message
class SignInRequest:
	lsid: protobug.String = protobug.field(2)
	area: protobug.String = protobug.field(3)

@protobug.message
class SignInResponse:
	jwt: protobug.String = protobug.field(1)



@protobug.message
class ListPodcastEpisodesRequest:
	channel_id: protobug.String = protobug.field(1)
	dontknow: protobug.Int32 = protobug.field(2)
	page_length: protobug.Int32 = protobug.field(4)
	cursor: protobug.String = protobug.field(5, default=None)

def add_grpc_header(protobuf_data):
	compression_flag = 0
	message_length = len(protobuf_data)
	header = struct.pack('>BI', compression_flag, message_length)
	return header + protobuf_data

def strip_grpc_response(response):
	return response[5:].rpartition(b"grpc-status:")[0]

print("SIGNUP")
# why do they have to make it so bloody complicated

lsid = ''.join(random.choices('0123456789abcdef', k=32))
big_funny = ("\n " + lsid).encode()

signup = requests.post("https://api.annex.radiko.jp/radiko.UserService/SignUp", headers={
	'Origin': 'https://radiko.jp',
	'Content-Type': 'application/grpc-web+proto',
	'X-User-Agent': 'grpc-web-javascript/0.1',
	'X-Grpc-Web': '1',
	}, data=( add_grpc_header(big_funny)),
)

print(signup.content)

# youre meant to only do the sign up ^ once and then keep your id for later
# so that you can V sign in and get the token for the API to work

print("SIGNIN")

si=add_grpc_header(protobug.dumps(SignInRequest(
	lsid=lsid,
	area="JP13",
)))

print(si)
print(base64.b64encode(si))

signin = requests.post("https://api.annex.radiko.jp/radiko.UserService/SignIn", headers={
	'Origin': 'https://radiko.jp',
	'Content-Type': 'application/grpc-web+proto',
	'X-User-Agent': 'grpc-web-javascript/0.1',
	'X-Grpc-Web': '1',
}, data=si)

print(signin.content)

signin_result = protobug.loads(strip_grpc_response(signin.content), SignInResponse)


headers = {
    'Origin': 'https://radiko.jp',
    'Authorization': f'Bearer {signin_result.jwt}',
    'x-annex-proto-version': '1.0.0',
    'Content-Type': 'application/grpc-web+proto',
    'X-User-Agent': 'grpc-web-javascript/0.1',
    'X-Grpc-Web': '1',
}

response = requests.post('https://api.annex.radiko.jp/radiko.PodcastService/ListPodcastEpisodes', headers=headers,
	data=add_grpc_header(protobug.dumps(ListPodcastEpisodesRequest(
		channel_id="0ce1d2d7-5e07-4ec5-901a-d0eacdacc332",
		dontknow=1,
		page_length=200,  # site uses 20
#		cursor="ef693874-0ad2-48cc-8c52-ac4de31cbf54"  # here you put the id of the last episode you've seen in the list
	)))
)

print(response)

episodes = strip_grpc_response(response.content)


with open("ListPodcastEpisodes.bin", "wb") as f:
	f.write(episodes)


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


episodes_response = protobug.loads(episodes, ListPodcastEpisodesResponse)

print(episodes_response)

for e in episodes_response.episodes:
	print(e.title, e.id)
print(episodes_response.hasNextPage)
