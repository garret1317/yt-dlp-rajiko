#!/usr/bin/env python3
import datetime

JST = datetime.timezone(datetime.timedelta(hours=9))

class RadikoTime():
	datetime = None

	def timestring(self):
		return self.datetime.strftime("%Y%m%d%H%M%S")

	def broadcast_day(self):
		# timetable api counts 05:00 -> 28:59 (04:59 next day) as all the same day
		# like the 30-hour day, 06:00 -> 29:59 (05:59)
		# https://en.wikipedia.org/wiki/Date_and_time_notation_in_Japan#Time
		# but ends earlier, presumably so the early morning programmes dont look like late night ones
		# this means we have to shift back by a day so we can get the right programme

		dt = self.datetime
		if dt.hour < 5:
			dt -= datetime.timedelta(days=1)
		return dt.strftime("%Y%m%d")

	def broadcast_day_end(self):
		dt = self.datetime
		if dt.hour < 5:
			dt -= datetime.timedelta(days=1)
		dt += datetime.timedelta(days=1)
		dt.replace(hour=5, minute=0, second=0)
		return dt

	def timestamp(self):
		return self.datetime.timestamp()
	def isoformat(self):
		return self.datetime.isoformat()

	def __str__(self):
		return str(self.datetime)
	def __eq__(self, other):
		return self.datetime == other
	def __ne__(self, other):
		return self.datetime != other
	def __lt__(self, other):
		return self.datetime < other
	def __gt__(self, other):
		return self.datetime > other
	def __le__(self, other):
		return self.datetime <= other
	def __ge__(self, other):
		return self.datetime >= other


class RadikoSiteTime(RadikoTime):

	def __init__(self, timestring):

		timestring = str(timestring)
		year = int(timestring[:4]); month = int(timestring[4:6]); day = int(timestring[6:8])
		hour = min(int(timestring[8:10]), 24)
		minute = min(int(timestring[10:12]), 59)
		second = timestring[12:14]

		# edge cases
		next_day = False  # hour is 24, meaning 00 the next day
		no_second = second == ""  # there's no second, meaning we have to -1 second for some reason

		if hour > 23:
			hour = hour - 24
			next_day = True
		if not no_second:
			second = min(int(second), 59)
		else:
			second = 0

		self.datetime = datetime.datetime(year, month, day, hour, minute, second, tzinfo = JST)

		if next_day:
			self.datetime += datetime.timedelta(days=1)
		if no_second:
			self.datetime -= datetime.timedelta(seconds=1)

if __name__ == "__main__":
	# normal
	assert RadikoSiteTime('20230823180000').timestring() == "20230823180000"
	# seconds (clamped to 59)
	assert RadikoSiteTime('20230819105563').timestring() == "20230819105559"
	# minutes (clamped to 59)
	assert RadikoSiteTime('20230819106200').timestring() == "20230819105900"
	# hours (clamped to 23)
	assert RadikoSiteTime('20230819240000').timestring() == "20230820000000"
	# cursed (no seconds) - seems to do -1s
	assert RadikoSiteTime('202308240100').timestring() == "20230824005959"
	# broadcast day starts at 05:00, ends at 04:59 (29:59)
	assert RadikoSiteTime('20230824030000').broadcast_day() == '20230823'
	# checking timezone
	assert RadikoSiteTime('20230823090000').datetime.timestamp() == 1692748800

class RadikoShareTime(RadikoTime):

	def __init__(self, timestring):

		timestring = str(timestring)
		year = int(timestring[:4]); month = int(timestring[4:6]); day = int(timestring[6:8])
		hour = int(timestring[8:10]); minute = int(timestring[10:12]); second = int(timestring[12:14])

		minutes_to_add = second // 60
		second = second % 60
		minute += minutes_to_add
		hours_to_add = minute // 60
		minute = minute % 60
		hour += hours_to_add

		days_to_add = hour // 24
		hour = hour % 24

		# XXX: doesnt handle day invalid for month (the site actually works with this)

		self.datetime = datetime.datetime(year, month, day, hour, minute, second, tzinfo = JST)
		self.datetime += datetime.timedelta(days=days_to_add)

if __name__ == "__main__":
	assert RadikoShareTime('20230630296200').timestring() == '20230701060200'
	assert RadikoShareTime('20230630235960').timestring() == '20230701000000'
