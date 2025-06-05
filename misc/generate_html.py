#!/usr/bin/env python3
import os
import hashlib
import re

pip_index = open("index.html", "w")

pip_index.write("""<!DOCTYPE HTML>
<html lang="en-GB">
<head>
	<title>yt-dlp-rajiko pip index</title>
	<link rel="canonical" href="https://427738.xyz/yt-dlp-rajiko/pip/yt-dlp-rajiko/">
</head>
<body>

<ul>
""")

site_sha256 = []

tarballs = []
wheels = []

for item in sorted(os.listdir()):#, key=lambda x: x.name):
	if os.path.islink(item):
		continue

	if item.endswith(".tar.gz"):
		tarballs.append(item)
	elif item.endswith(".whl"):
		wheels.append(item)
	else:
		continue

	pip_index.write("\t<li>")
	pip_index.write('<a href="')
	pip_index.write(item)

	with open(item, "rb") as f:
		checksum = hashlib.sha256(f.read()).hexdigest()

	pip_index.write("#sha256=")
	pip_index.write(checksum)
	pip_index.write('">')
	pip_index.write(item)
	pip_index.write("</a>\n")

	site_string = checksum + "&nbsp;&nbsp;" + '<a href="dl/' + item + '">' + item + "</a><br>"
	site_sha256.append(site_string)

pip_index.write("""</ul>

</body>
</html>""")

latest_tarball = tarballs[-1]
latest_wheel = wheels[-1]
print(latest_tarball, latest_wheel)

os.remove("yt_dlp_rajiko-latest.tar.gz")
os.symlink(latest_tarball, "yt_dlp_rajiko-latest.tar.gz")

os.remove("yt_dlp_rajiko-latest.whl")
os.symlink(latest_wheel, "yt_dlp_rajiko-latest.whl")

site_sha256.reverse()

latest_list = site_sha256[:2]
previous_list = site_sha256[2:]

latest = "\n".join(["<!-- LATEST SHA256 START -->", "<code>", "\n".join(latest_list), "</code>", "<!-- LATEST SHA256 END -->"])

previous = "\n".join(["<!-- PREVIOUS SHA256 START -->", "<code>", "\n".join(previous_list), "</code>", "<!-- PREVIOUS SHA256 END -->"])

for i in ["../../index.html", "../../index.ja.html"]:
	with open(i, "r+") as f:
		page = f.read()

		page = re.sub(r"<!-- LATEST SHA256 START -->.+<!-- LATEST SHA256 END -->", latest, page, flags=re.DOTALL)
		page = re.sub(r"<!-- PREVIOUS SHA256 START -->.+<!-- PREVIOUS SHA256 END -->", previous, page, flags=re.DOTALL)

		f.seek(0)
		f.truncate(0)
		f.write(page)
