from flask_login import current_user, logout_user
from datetime import datetime, timedelta
from pytz import timezone
import pytz

def start_route():
	if current_user.is_authenticated:
		logout_user()


def get_offset_dates_initiated(sessions, time_offset):
	fmt = '%I:%M:%S %p'
	dates = []

	zone = timezone(time_offset)
	for session in sessions:
		utc_time = pytz.utc.localize(session.date_initiated)
		local_time = utc_time.astimezone(zone)

		# print(zone)
		# print(local_time.strftime(fmt))

		dates.append(local_time.strftime(fmt))

	return dates

def get_offset_dates_end(sessions, time_offset):
	fmt = '%I:%M:%S %p'
	dates = []

	zone = timezone(time_offset)
	for session in sessions:
		utc_time = pytz.utc.localize(session.date_initiated)
		local_time = utc_time.astimezone(zone)
		add_seconds = timedelta(seconds=session.total_seconds())
		local_time += add_seconds

		print(local_time)

		# print(zone)
		# print(local_time.strftime(fmt))

		dates.append(local_time.strftime(fmt))

	return dates