import datetime
import re

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	join_nonempty,
	update_url_query,
	traverse_obj,
)

# "hacks" as in great jank/schizo shit that works anyway

def _generate_as_live_fragments(self, playlist_base_url, start_at, end_at, domain, headers={}, first_chunk=None):
	playlist = []
	chunk_length = 300  # max the api allows

	duration = int(end_at.timestamp() - start_at.timestamp())
	cursor = 0
	chunk_num = 1
	while cursor < duration:
		chunk_length = min(chunk_length, duration - cursor)

		chunk_start = start_at + datetime.timedelta(seconds=cursor)
		chunk_url = update_url_query(playlist_base_url, {
			"seek": chunk_start.timestring(),
			"l": chunk_length,
		})

		chunk_fragments, real_chunk_length = _get_chunk_playlist(self, chunk_url, domain, chunk_num, headers, first_chunk)

		cursor += round(real_chunk_length)
		chunk_num += 1
		first_chunk = None

		for frag in chunk_fragments:
			yield frag


def _get_chunk_playlist(self, chunk_url, src_id, chunk_num, headers={}, first_chunk=None):
	EXTINF_duration = re.compile(r"^#EXTINF:([\d.]+),", flags=re.MULTILINE)

	playlist = ""
	chunk_id = join_nonempty(src_id, chunk_num)

	if first_chunk:
		m3u8_url = first_chunk
	else:
		self.write_debug(f"Preparing {src_id} chunk {chunk_num}")
		base_formats = self._extract_m3u8_formats(
			chunk_url, chunk_id, fatal=False, headers=headers,
	#		note=f"Preparing {src_id} chunk {chunk_num}"
			note=False,
			errnote=f"Failed to get {src_id} chunk {chunk_num} base format",
		)
		m3u8_url = traverse_obj(base_formats, (..., "url",), get_all=False)

	self.write_debug(f"Getting {src_id} chunk {chunk_num} playlist")
	playlist = self._download_webpage(m3u8_url, chunk_id, note=False, errnote=f"Failed to get {src_id} chunk {chunk_num} playlist")
	#note=f"Getting {src_id} chunk {chunk_num} fragments")

	return _parse_hls(playlist)

def _parse_hls(m3u8_doc):
	fragments = []

	# playlists can sometimes be longer than they should
	# e.g. wowza stream does some strange things
	# it goes along fine with every fragment 5s long as normal
	# and then during the ad break it does one with a different length (eg 2s)
	# i assume so they have a clean split to do ad insertion in? idk

	# but anyway now the chunks aren't always a clean 5mins long
	# and we get a repeated fragment going into the next chunk

	# so to work around this, we track the real duration from the #EXTINF tags

	playlist_duration = 0
	fragment_duration = None
	for line in m3u8_doc.splitlines():
		if line.startswith("#EXTINF:"):
			fragment_duration = float(line[len('#EXTINF:'):].split(',')[0])  # from common._parse_m3u8_vod_duration
			continue
		elif line.startswith("#"):
			continue

		fragments.append({"url": line, "duration": fragment_duration})
		playlist_duration += fragment_duration or 0
		fragment_duration = None

	return fragments, playlist_duration
