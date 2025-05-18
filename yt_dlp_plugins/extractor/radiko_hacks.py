import datetime
import re

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	join_nonempty,
	update_url_query,
	traverse_obj,
)

# "hacks" as in great jank/schizo shit that works anyway

def _generate_as_live_playlist(self, playlist_url, start_at, end_at, domain, headers={}):
	playlist = ""
	chunk_length = 300  # max the api allows

	duration = int(end_at.timestamp() - start_at.timestamp())
	cursor = 0
	chunk_num = 1
	while cursor < duration:
		chunk_length = min(chunk_length, duration - cursor)

		chunk_start = start_at + datetime.timedelta(seconds=cursor)
		chunk_url = update_url_query(playlist_url, {
			"seek": chunk_start.timestring(),
			"l": chunk_length,
		})

		chunk_playlist, real_chunk_length = _get_chunk_playlist(self, chunk_url, domain, chunk_num, headers)

		playlist += chunk_playlist
		cursor += real_chunk_length
		chunk_num += 1

	return playlist

def _get_chunk_playlist(self, chunk_url, src_id, chunk_num, headers={}):
	EXTINF_duration = re.compile("^#EXTINF:([\d.]+),", flags=re.MULTILINE)

	playlist = ""
	chunk_id = join_nonempty(src_id, chunk_num)
	base_format = self._extract_m3u8_formats(
		chunk_url, chunk_id, fatal=False, headers=headers,
		note=f"Preparing {src_id} chunk {chunk_num}"
	)
	m3u8_url = traverse_obj(base_format, (..., "url",), get_all=False)
	playlist = self._download_webpage(m3u8_url, chunk_id, note=f"Getting {src_id} chunk {chunk_num} fragments")

	real_duration = 0
	for i in EXTINF_duration.findall(playlist):
		real_duration += float(i)
	real_duration = round(real_duration)

	# playlists can sometimes be longer than they should
	# wowza stream does some strange things
	# it goes along fine with every fragment 5s long as normal
	# and then during the ad break it does one with a different length (2s here)
	# i assume so they have a clean split to do ad insertion in? idk

	# but anyway now the chunks aren't always a clean 5mins long
	# and we get a repeated fragment going into the next chunk

	# so to work around this, we track the real duration from the #EXTINF tags

	return playlist, real_duration
