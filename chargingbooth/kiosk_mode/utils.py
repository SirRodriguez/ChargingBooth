from flask_login import current_user, logout_user
from chargingbooth import service_ip,  db
from chargingbooth.models import Device_ID
import requests
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

		dates.append(local_time.strftime(fmt))

	return dates

def split_seconds(secs):
	hours = secs // 3600
	remaining_seconds = secs - ( hours * 3600 )
	minutes = remaining_seconds // 60;
	remaining_seconds = remaining_seconds - ( minutes * 60 )
	seconds = remaining_seconds

	return hours, minutes, seconds

def is_registered():
	devi_id = Device_ID.query.first()

	if devi_id == None:
		# return redirect(url_for('register.home'))
		return False
	else:
		if devi_id.id_number == None:
			# return redirect(url_for('register.home'))
			return False
		else:
			# Check here if id number is correct
			payload = requests.get(service_ip + '/device/is_registered/' + devi_id.id_number)		

			if payload.json()["registered"]:
				# return redirect(url_for('kiosk_mode.home'))
				return True
			else:
				# return redirect(url_for('register.home'))
				return False