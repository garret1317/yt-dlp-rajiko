#!/usr/bin/env python3
import unittest

from yt_dlp_plugins.extractor import radiko
from yt_dlp import YoutubeDL


class test_tokens(unittest.TestCase):

	def setUp(self):
		self.ie = radiko._RadikoBaseIE()
		ydl = YoutubeDL(auto_init=False)
		self.ie.set_downloader(ydl)

	def test_area(self):
		# check areas etc work
		for i in range(1, 48):
			area = "JP" + str(i)
			with self.subTest(f"Negotiating token for {area}", area=area):
				token = self.ie._negotiate_token(area)
				self.assertEqual(token.get("X-Radiko-AreaId"), area)


if __name__ == '__main__':
	unittest.main()
	# may wish to set failfast=True
