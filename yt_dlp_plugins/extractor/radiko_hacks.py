import datetime

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	join_nonempty,
	update_url_query,
	traverse_obj,
)

# "hacks" as in great jank/schizo shit that works anyway

def _generate_as_live_chunks(playlist_url, start_at, end_at):
	chunks = []
	chunk_length = 300  # max the api allows

	duration = int(end_at.timestamp() - start_at.timestamp())
	cursor = 0
	while cursor < duration:
		chunk_length = min(chunk_length, duration - cursor)
		chunk_start = start_at + datetime.timedelta(seconds=cursor)
		chunk_url = update_url_query(playlist_url, {
			"seek": chunk_start.timestring(),
			"l": chunk_length,
		})
		chunks.append(chunk_url)
		cursor += chunk_length

	return chunks

def _playlist_from_chunks(self, chunks, src_id, headers={}):
	playlist = ""
	for i, chunk in enumerate(chunks):
		i +=1 # for more friendly cli output, it gets reset each loop so it shouldnt effect anything
		chunk_id = join_nonempty(src_id, i)
		base_format = self._extract_m3u8_formats(
			chunk, chunk_id, fatal=False, headers=headers,
			note=f"Preparing {src_id} chunk {i}"
		)
		m3u8_url = traverse_obj(base_format, (..., "url",), get_all=False)
		playlist += self._download_webpage(m3u8_url, chunk_id, note=f"Getting {src_id} chunk {i} fragments")
	return playlist
