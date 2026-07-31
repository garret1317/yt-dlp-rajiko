from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
	get_first,
	traverse_obj,
)

class _RadikoNextJSBaseIE(InfoExtractor):
	def _get_nextjs(self, html, key, video_id):
		return get_first(self._search_nextjs_v13_data(html, video_id), key)
