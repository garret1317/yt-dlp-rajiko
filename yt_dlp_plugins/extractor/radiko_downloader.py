import datetime
import math

import yt_dlp.downloader
from yt_dlp.downloader.common import FileDownloader
from yt_dlp.downloader.fragment import FragmentFD, HttpQuietDownloader
from yt_dlp.downloader.hls import HlsFD
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	traverse_obj,
	update_url_query,
)


class RadikoChunkedFD(FragmentFD):

	FD_NAME = "radiko_chunked"

	def _parse_hls(self, ctx, m3u8_doc, frag_index, station_id=None):
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
		ads_flagged = False
		for line in m3u8_doc.splitlines():
			if line.startswith("#EXTINF:"):
				fragment_duration = float(line[len('#EXTINF:'):].split(',')[0])  # from common._parse_m3u8_vod_duration
				continue
			elif line.startswith("#"):
				continue

			fragments.append({"url": line, "frag_index": frag_index, 'fragment_count': ctx['fragment_count']})
			playlist_duration += fragment_duration or 0
			fragment_duration = None
			frag_index += 1

			if station_id and f"/{station_id}/" not in line and not ads_flagged:
				self.report_warning("Possible ad insertion detected. Please report this at https://github.com/garret1317/yt-dlp-rajiko/issues")
				ads_flagged = True

		return fragments, playlist_duration, frag_index

	def _get_chunk_playlist(self, ctx, chunk_url, chunk_num, frag_index, headers={}, station_id=None):
		playlist = ""

		self.write_debug(f"Preparing chunk {chunk_num}")

		ie = InfoExtractor(self.ydl)
		base_formats = ie._extract_m3u8_formats(
			chunk_url, chunk_num, fatal=True, headers=headers,
			note=False,
			errnote=f"Failed to get chunk {chunk_num} base format",
		)
		m3u8_url = traverse_obj(base_formats, (..., "url",), get_all=False)

		self.write_debug(f"Getting chunk {chunk_num} playlist")
		playlist = ie._download_webpage(m3u8_url, chunk_num, note=False, errnote=f"Failed to get chunk {chunk_num} playlist")

		return self._parse_hls(ctx, playlist, frag_index, station_id)



	def real_download(self, filename, info_dict):
		downloader_options = info_dict["downloader_options"]

		playlist_base_url = info_dict["url"]

		start_at = downloader_options["start_at"]
		end_at = downloader_options["end_at"]
		station_id = downloader_options["station_id"]
		auth_headers = downloader_options["auth_headers"]

		duration = int(end_at.timestamp() - start_at.timestamp())

		estimated_fragment_count = math.ceil(duration / 5)

		ctx = {
			'filename': filename,
			'total_frags': estimated_fragment_count,
			"fragment_count": estimated_fragment_count,
		}

		# we estimate a total fragment count, but sometimes chunks have more fragments than they "should"
		# for instance if a 5s section is split into 2s and 3s, that would be an extra fragment

		# ideally, i want the displayed total fragment count to increase when extra fragments are discovered
		# ie it would go from (xx/720) to (xx/721)
		# we can do this by setting "live": "is_from_start", then we can update fragment_count as we go along
		# BUT, then we don't get the % progress indicator

		# if we set total_frags to a falsy value, then the indicator will use fragment_count
		# but if we aren't live, then total_frags has to be a number. so the only value we can use is 0
		# which does make the fragment counter work, but it breaks the percentage %,
		# because we immediately get to 100% of the 0 fragments it needs

		self._prepare_and_start_frag_download(ctx, info_dict)


		# XXX !!!!!!!!! MASSIVE HACK !!!!!!!!! XXX

		# download_and_append_fragments is exactly what we want, _except_ that it finalises the download at the end
		# we want to keep going onto the next chunk once the previous one has finished, so we need to keep it un-finalised
		# apart from that the function is good, cba to reimplement/override allat
		# SO we just override the finalisation function to make it a no-op. then we can finalise after all chunks are done.

		real_finish_frag_download = self._finish_frag_download
		def fake_finish_frag_download(ctx, info_dict):
			return True
		self._finish_frag_download = fake_finish_frag_download

		# XXX !!!!!!!!! MASSIVE HACK !!!!!!!!! XXX


		chunk_length = 300  # max the api allows
		cursor = 0
		chunk_idx = 1
		frag_index = 1
		while cursor < duration:
			chunk_length = min(chunk_length, duration - cursor)

			chunk_start = start_at + datetime.timedelta(seconds=cursor)
			chunk_url = update_url_query(playlist_base_url, {
				"seek": chunk_start.timestring(),
				"l": chunk_length,
			})

			expected_chunk_fragments = math.ceil(chunk_length / 5)
			chunk_fragments, real_chunk_length, frag_index = self._get_chunk_playlist(ctx, chunk_url, chunk_idx, frag_index, auth_headers, station_id)

			excess_fragments = max(0, len(chunk_fragments) - expected_chunk_fragments)
			ctx['fragment_count'] += excess_fragments

			cursor += round(real_chunk_length)
			chunk_idx += 1

			self.download_and_append_fragments(ctx, chunk_fragments, info_dict)

		# XXX !!!!!!!!! MASSIVE HACK !!!!!!!!! XXX
		self._finish_frag_download = real_finish_frag_download
		return self._finish_frag_download(ctx, info_dict)
		# XXX !!!!!!!!! MASSIVE HACK !!!!!!!!! XXX

yt_dlp.downloader.PROTOCOL_MAP['radiko_chunked'] = RadikoChunkedFD
