from flask import url_for, current_app
from flask_mail import Message
from chargingbooth import mail, service_ip,  db
from chargingbooth.models import Device_ID
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import os
from os import listdir
from os.path import isfile, join
import pandas as pd
import matplotlib.pyplot as plt
import secrets
import requests

# def send_reset_email(user, logged_in=False):
# 	token = user.get_reset_token()
# 	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
# 	if logged_in:
# 		msg.body = f'''To reset your password, visit the following link:

# {url_for('system_admin_account.change_token', token=token, _external=True)}

# If you did not make this request then simply ignore this email and no change will be made.
# '''
# 	else:
# 		msg.body = f'''To reset your password, visit the following link:

# {url_for('system_admin_account.reset_token', token=token, _external=True)}

# If you did not make this request then simply ignore this email and no change will be made.
# '''
# 	mail.send(msg)

def get_offset_dates_initiated(sessions, time_offset):
	fmt = '%b %d, %Y - %I:%M:%S %p'
	dates = []

	zone = timezone(time_offset)
	for session in sessions:
		# utc_time = pytz.utc.localize(session.date_initiated)
		date_initiated=datetime(
			year=session["date_initiated_year"],
			month=session["date_initiated_month"],
			day=session["date_initiated_day"], 
			hour=session["date_initiated_hour"], 
			minute=session["date_initiated_minute"],
			second=session["date_initiated_second"]
			)

		utc_time = pytz.utc.localize(date_initiated)
		local_time = utc_time.astimezone(zone)

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

	# Set the labels
	plt.title("Number of Sessions for each year", fontsize=20)
	plt.ylabel("Number of Sessions", fontsize=15)
	plt.xlabel("Year", fontsize=15)



def count_months(dates, year):
	# initialize the months
	months = {
		'Jan' : 0,
		'Feb' : 0,
		'Mar' : 0,
		'Apr' : 0,
		'May' : 0,
		'Jun' : 0,
		'Jul' : 0,
		'Aug' : 0,
		'Sep' : 0,
		'Oct' : 0,
		'Nov' : 0,
		'Dec' : 0
	}

	# Grab the sessions in each month
	for date in dates:
		date_list = date.split(" ")
		yr = date_list[2]

		if yr == year:
			mth = date_list[0]
			months[mth] += 1

	return months

def create_bar_months(months, year):
	mth = list(months.keys())
	vls = list(months.values())

	fig = plt.figure(figsize = (10, 5))

	# Create the bar plot
	plt.bar(mth, vls)

	# Set the labels
	plt.title("Number of Sessions for " + year, fontsize=20)
	plt.ylabel("Number of Sessions", fontsize=15)
	plt.xlabel("Month", fontsize=15)

def count_days(dates, year, month):
	# This is to get how many days each month has
	days_of_months = {
		'Jan' : 31,
		'Feb' : 29, # Because of leap year, it has 29
		'Mar' : 31,
		'Apr' : 30,
		'May' : 31,
		'Jun' : 30,
		'Jul' : 31,
		'Aug' : 31,
		'Sep' : 30,
		'Oct' : 31,
		'Nov' : 30,
		'Dec' : 31
	}

	# initialize days
	days = {}
	for d in range(days_of_months[month]):
		days[d+1] = 0

	# Grab the sessions for the month
	for date in dates:
		date_list = date.split(" ")
		yr = date_list[2]
		mth = date_list[0]

		if yr == year and mth == month:
			dy = int(date_list[1][:-1])
			days[dy] += 1


	return days

def create_bar_days(days, month, year):
	dys = list(days.keys())
	vls = list(days.values())

	fig = plt.figure(figsize = (10, 5))

	# Create the bar plot
	plt.bar(dys, vls)

	# Make sure all x ticks show
	plt.xticks(dys)

	# Set the labels
	plt.title("Number of Sessions for " + month + ", " + year, fontsize=20)
	plt.ylabel("Number of Sessions", fontsize=15)
	plt.xlabel("Day", fontsize=15)

def count_hours(dates, day, month, year):

	hours = {
		# Reversed AM and Pm so that the plot shows the right way
		'11PM' : 0,
		'10PM' : 0,
		'09PM' : 0,
		'08PM' : 0,
		'07PM' : 0,
		'06PM' : 0,
		'05PM' : 0,
		'04PM' : 0,
		'03PM' : 0,
		'02PM' : 0,
		'01PM' : 0,
		'12PM' : 0,
		
		'11AM' : 0,
		'10AM' : 0,
		'09AM' : 0,
		'08AM' : 0,
		'07AM' : 0,
		'06AM' : 0,
		'05AM' : 0,
		'04AM' : 0,
		'03AM' : 0,
		'02AM' : 0,
		'01AM' : 0,
		'12AM' : 0,
	}

	for date in dates:
		date_list = date.split(" ")
		yr = date_list[2]
		mth = date_list[0]
		dy = date_list[1][:-1]

		if yr == year and mth == month and dy == day:
			hr = date.split(" ")[4].split(":")[0]
			hrm = hr + date.split(" ")[5]
			hours[hrm] += 1

	return hours
	

def create_bar_hours(hours, day, month, year):
	hrs = list(hours.keys())
	vls = list(hours.values())

	fig = plt.figure(figsize = (10, 5))

	# Create the bar plot
	plt.barh(hrs, vls)

	# Set the labels
	plt.title("Number of Sessions for " + month + " " + day + ", " + year, fontsize=20)
	plt.ylabel("Hour", fontsize=15)
	plt.xlabel("Number of Sessions", fontsize=15)

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

# def get_min_sec(seconds):
# 	minutes = seconds // 60
# 	sec = seconds - (minutes * 60)
# 	return minutes, sec

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