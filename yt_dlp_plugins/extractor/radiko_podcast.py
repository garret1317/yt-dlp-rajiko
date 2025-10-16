from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	clean_html,
	OnDemandPagedList,
	parse_qs,
	traverse_obj,
	update_url_query,
	url_or_none,
	str_or_none,
)

import dataclasses
import random

from yt_dlp_plugins.extractor.radiko_dependencies import protobug
if protobug:
	import yt_dlp_plugins.extractor.radiko_protobufs as pb


class _RadikoPodcastBaseIE(InfoExtractor):

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
		webpage = self._download_webpage(url, video_id)
		next_data = self._search_nextjs_data(webpage, video_id)["props"]["pageProps"]

		episode_info = next_data["podcastEpisode"]

		return self._extract_episode(episode_info)


class RadikoPodcastChannelIE(_RadikoPodcastBaseIE):
	_VALID_URL = r"https?://radiko\.jp/podcast/channels/(?P<id>[a-f0-9-]+)"

	_TESTS = [{
		"url": "https://radiko.jp/podcast/channels/09f27a48-ae04-4ce7-a024-572460e46eb7",
		"info_dict": {
			"id": "09f27a48-ae04-4ce7-a024-572460e46eb7"
		},
		'playlist_mincount': 20,
		'expected_warnings': ['Currently this extractor can only extract the latest 20 episodes'],
	}]

	def _real_extract(self, url):
		channel_id = self._match_id(url)
		webpage = self._download_webpage(url, channel_id)
		next_data = self._search_nextjs_data(webpage, channel_id)["props"]["pageProps"]

		channel_info = next_data["podcastChannel"]
		episode_list_response = next_data["listPodcastEpisodesResponse"]


		def entries():
			has_next_page = episode_list_response.get("hasNextPage")
			for episode in episode_list_response["episodesList"]:
				cursor = episode.get("id")
				yield self._extract_episode(episode)

			if has_next_page:
				if protobug:
					userservice_token = pb.auth_userservice(self)
					while has_next_page:
						page = pb.get_podcast_episodes(self, channel_id, userservice_token, cursor)
						has_next_page = page.hasNextPage
						for episode in page.episodes:
							cursor = episode.id
							yield self._extract_episode(dataclasses.asdict(episode))
				else:
					self.report_warning(f'protobug is required to extract more than the latest {len(episode_list_response["episodesList"])} episodes.\nIf you installed yt-dlp-rajiko manually (with the .whl), use the .zip bundle instead. If you installed with pip, pip install protobug .')

		return {
			"_type": "playlist",
			"id": channel_id,
			**traverse_obj(channel_info, {
				"playlist_title": "title",
				"playlist_id": "id",
				"playlist_description": ("description", {clean_html}),
				"playlist_thumbnail": ("imageUrl", {url_or_none}),

			}),
			"entries": entries(),
		}


class RadikoPodcastSearchIE(InfoExtractor):
	_VALID_URL = r"https?://(?:www\.)?radiko\.jp/#!/search/podcast/(?:timeshift|live)\?"
	_TESTS = [{
		"url": "https://radiko.jp/#!/search/podcast/live?key=ドラマ",
		"playlist_mincount": 51,
		"info_dict": {
			"id": "ドラマ",
			"title": "ドラマ",
		},
	}]

	def _pagefunc(self, url, idx):
		url = update_url_query(url, {"pageIdx": idx})
		data = self._download_json(url, None, note=f"Downloading page {idx+1}")

		results = []
		for channel in data.get("channels"):
			results.append(
				self.url_result(
					channel.get("channelUrl"),
					id=channel.get("id"),
					ie=RadikoPodcastChannelIE,
				)
			)
		return results


	def _real_extract(self, url):
		# hack away the # so urllib.parse will work (same as normal RadikoSearchIE)
		url = url.replace("/#!/", "/!/", 1)
		queries = parse_qs(url)

		keywords = traverse_obj(queries, ("key", 0))
		search_url = update_url_query("https://api.annex-cf.radiko.jp/v1/podcasts/channels/search_with_keywords_by_offset", {
			"keywords": keywords,
			"uid": "".join(random.choices("0123456789abcdef", k=32)),
			"limit": 50,  # result limit. the actual limit before the api errors is 5000, but that seems a bit rude so i'll leave as 50 like the radio one
		})

		return self.playlist_result(
			OnDemandPagedList(lambda idx: self._pagefunc(search_url, idx), 50),
			title=keywords,
			id=keywords,  # i have to put some kind of id or the tests fail
		)
