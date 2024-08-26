#!/usr/bin/env python3
import email.utils
import feedgenerator

def parse_changelog(lines):
	got_version = False
	got_date = False
	got_url = False
	done_remarks = False
	releases = []
	release = {}
	release_remarks = []
	release_changes = []
	current_change = ""

	for idx, line in enumerate(lines):
		line = line.rstrip()

		if not got_version:
			got_version = True
			release["version"] = line
			continue

		if not got_date:
			release["date"] = email.utils.parsedate_to_datetime(line)
			got_date = True
			continue

		key, sep, val = line.partition(": ")
		if key in ["url", "sha256", "released"] and val != "":
			release[key] = val
			continue

		if not done_remarks:
			if line == "":
				done_remarks = True
				release["remarks"] = release_remarks
				release_remarks = []
				continue
			else:
				release_remarks.append(line)
				continue

		if line != "":
			release_changes.append(line.rstrip())

			if idx + 1 != len(lines):
				continue

		release["changes"] = release_changes
		if release.get("released") != "no":
			releases.append(release)

		got_version = False
		got_date = False
		done_remarks = False
		release = {}
		release_changes = []

	return releases

def generate_rss_feed(releases):
	feed = feedgenerator.Rss201rev2Feed(
		title="yt-dlp-rajiko changelog",
		description="Notifications for new yt-dlp-rajiko releases, with changelogs",
		link="https://427738.xyz/yt-dlp-rajiko/",
		language="en-GB",
		ttl=180,  # 3 hours
	)

	for release in releases:
		title = "yt-dlp-rajiko " + release["version"] + " has been released"
		description = ""
		description += "<p>"
		for remark in release["remarks"]:
			description += remark
			description += "<br/>"
		description += "</p>"
		description += "<p>This release:</p>\n"
		description += "<ul>"
		for change in release["changes"]:
			description += "<li>"
			description += change
			description += "</li>\n"
		description += "</ul></p>"

		if release.get("url"):
			if release["version"] != "1.0":
				description += "\n<p>If you use pip, you should be able to upgrade with <code>pip install yt-dlp-rajiko --upgrade --extra-index-url https://427738.xyz/yt-dlp-rajiko/pip/</code>.<br>"
				description += "If you installed manually, you can download the updated <code>.whl</code> from this post's link."
				if release.get("sha256"):
					description += " The SHA256 checksum should be <code>"
					description += release.get("sha256")
					description += "</code>."
				description += "</p>"
			else:
				description += '\n<p>Please see <a href="https://427738.xyz/yt-dlp-rajiko/#install">the homepage</a> for initial installation instructions.</p>'

		feed.add_item(
			title=title,
			description=description,
			link=release.get("url"),
			pubdate=release["date"]
		)
	return feed

if __name__ == "__main__":
	with open("CHANGELOG") as f:
		releases = parse_changelog(f.readlines())

	feed = generate_rss_feed(releases)
	feed_contents = feed.writeString("utf-8")
	feed_contents = feed_contents.replace("<rss", '<?xml-stylesheet href="rss-style.xsl" type="text/xsl"?>\n<rss')

	with open('CHANGELOG.xml', 'w') as fp:
		fp.write(feed_contents)
