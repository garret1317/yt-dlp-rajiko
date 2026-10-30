from yt_dlp.postprocessor.common import PostProcessor

# by request of https://egg.5ch.io/test/read.cgi/software/1781899780/183
class RemoveUntitledChapterPP(PostProcessor):
	def run(self, info):
		chapters = info.get('chapters') or []
		if chapters and isinstance(chapters[0], dict):
			if chapters[0].get('title') == '<Untitled Chapter 1>':
				info['chapters'] = chapters[1:]
		return [], info
