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


# class Session(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	duration = db.Column(db.Integer) #Seconds
# 	power_used = db.Column(db.Float) #Watts per second
# 	amount_paid = db.Column(db.Integer) #Cents
# 	date_initiated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
# 	location = db.Column(db.String(100), default="No Location")
# 	port = db.Column(db.String(100), default="No Port")
# 	increment_size = db.Column(db.Integer) #Seconds
# 	increments = db.Column(db.Integer)

def create_csv_file_from_sessions(sessions):
	# Save Sessions to a csv file so pandas can read it
	file_name = "sessions.csv"
	file_path = os.path.join(current_app.root_path, 'static', 'data_files', file_name)
	file = open(file_path, 'w')

	# Session information from model above
	titles_line = "id,duration,power_used,amount_paid,date_initiated,location,port,increment_size,increments\n"
	file.write(titles_line)

	# For each session it will add lines to the file depending on the data
	for session in sessions:
		data_line = str(session.id)
		data_line += ","
		data_line += str(session.duration)
		data_line += ","
		data_line += str(session.power_used)
		data_line += ","
		data_line += str(session.amount_paid)
		data_line += ","
		data_line += str(session.date_initiated.strftime("%Y-%m-%d %H:%M:%S")) # Maybe format this to yyyy-mm-dd hh:mm:ss
		data_line += ","
		data_line += str(session.location)
		data_line += ","
		data_line += str(session.port)
		data_line += ","
		data_line += str(session.increment_size)
		data_line += ","
		data_line += str(session.increments)
		data_line += "\n"

		file.write(data_line)

	return file_path

def create_plot(df, x_label, y_label):
	x = df[x_label]
	y = df[y_label]
	f, ax = plt.subplots(1,1, figsize=(10,5))

	plt.xlabel(x_label)
	plt.ylabel(y_label)

	plt.xticks(rotation=90)
	plt.gcf().subplots_adjust(bottom=0.40)

	ax.plot(x, y, color='black', alpha=0.75)

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