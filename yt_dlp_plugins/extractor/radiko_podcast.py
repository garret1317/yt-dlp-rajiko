from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	clean_html,
	traverse_obj,
	url_or_none,
	str_or_none,
)

# nice simple one for a change...
# the app uses a similar system to regular programmes, thankfully the site doesn't
# but it does need protobufs to get more than 20 items...

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
			"webpage_url": "https://radiko.jp/podcast/episodes/{id}".format(id=episode_info.get("id")),
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
		video_id = self._match_id(url)
		webpage = self._download_webpage(url, video_id)
		next_data = self._search_nextjs_data(webpage, video_id)["props"]["pageProps"]

		channel_info = next_data["podcastChannel"]
		episode_list_response = next_data["listPodcastEpisodesResponse"]


		def entries():
			for episode in episode_list_response["episodesList"]:
				yield self._extract_episode(episode)

		if traverse_obj(episode_list_response, "hasNextPage"):
			self.report_warning(f'Currently this extractor can only extract the latest {len(episode_list_response["episodesList"])} episodes')

		# TODO: GRPC/protobuf stuff to get the next page
		# https://api.annex.radiko.jp/radiko.PodcastService/ListPodcastEpisodes
		# see さらに表示 button on site


		return {
			"_type": "playlist",
			"id": video_id,
			**traverse_obj(channel_info, {
				"playlist_title": "title",
				"playlist_id": "id",
				"playlist_description": ("description", {clean_html}),
				"playlist_thumbnail": ("imageUrl", {url_or_none}),

			}),
			"entries": entries(),
		}
