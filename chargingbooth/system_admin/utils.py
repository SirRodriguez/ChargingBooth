from flask import url_for, current_app
from flask_mail import Message
from chargingbooth import mail
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import os
from os import listdir
from os.path import isfile, join
import pandas as pd
import matplotlib.pyplot as plt
import secrets

def send_reset_email(user, logged_in=False):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
	if logged_in:
		msg.body = f'''To reset your password, visit the following link:

{url_for('system_admin.change_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
'''
	else:
		msg.body = f'''To reset your password, visit the following link:

{url_for('system_admin.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
'''
	mail.send(msg)

def get_offset_dates_initiated(sessions, time_offset):
	fmt = '%b %d, %Y - %I:%M:%S %p'
	dates = []

	zone = timezone(time_offset)
	for session in sessions:
		utc_time = pytz.utc.localize(session.date_initiated)
		local_time = utc_time.astimezone(zone)

		# print(zone)
		# print(local_time.strftime(fmt))

		dates.append(local_time.strftime(fmt))

	return dates

def count_years(dates):
	years = {}

	for date in dates:
		yr = date.split(" ")[2]
		years[yr] = years.get(yr, 0) + 1


	return years

def create_bar_years(years):
	yrs = list(years.keys())
	vls = list(years.values())

	fig = plt.figure(figsize = (10, 5))

	# Create the bar plot
	plt.bar(yrs, vls)



def save_figure():
	fig_name = secrets.token_hex(8) + ".png"
	pic_path = os.path.join(current_app.root_path, 'static', 'data_files', fig_name)
	plt.savefig(pic_path)

	return fig_name

def remove_png():
	files_path = os.path.join(current_app.root_path, 'static', 'data_files')
	files = [f for f in listdir(files_path) if isfile(join(files_path, f))]
	for file in files:
		f_name, f_ext = os.path.splitext(file)
		if f_ext == ".png":
			full_path = os.path.join(current_app.root_path, 'static', 'data_files', file)
			os.remove(full_path)

def get_min_sec(seconds):
	minutes = seconds // 60
	sec = seconds - (minutes * 60)
	return minutes, sec