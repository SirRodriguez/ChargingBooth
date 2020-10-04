import string
import math
import random
from datetime import datetime
from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, logout_user
from chargingbooth import db, bcrypt, current_sessions, service_ip
from chargingbooth.models import Session, Settings
from chargingbooth.kiosk_mode.utils import (start_route, get_offset_dates_initiated, get_offset_dates_end,
											split_seconds, is_registered)
from chargingbooth.models import PFI, Device_ID
import requests

kiosk_mode = Blueprint('kiosk_mode', __name__)


@kiosk_mode.route("/kiosk_mode", methods=['GET', 'POST'])
def home():
	start_route()

	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	pic_files = PFI()

	# TODO: make settings obtainable form service

	devi_id_number = Device_ID.query.first().id_number

	# Grab settings from site
	try:
		payload = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	print(payload.json())

	# setting = Settings.query.first()
	setting = payload.json()

	sessions = current_sessions.local_sessions.values()
	# date_strings = get_offset_dates_initiated(sessions=sessions, time_offset=Settings.query.first().time_offset)
	# date_end_str = get_offset_dates_end(sessions=sessions, time_offset=Settings.query.first().time_offset)
	date_strings = get_offset_dates_initiated(sessions=sessions, time_offset=setting["time_offset"])
	date_end_str = get_offset_dates_end(sessions=sessions, time_offset=setting["time_offset"])

	sessions_and_dates = zip(sessions, date_strings, date_end_str)

	# Get the total hours, minutes, seconds for the session time
	# hours, minutes, seconds = split_seconds(setting.charge_time)
	hours, minutes, seconds = split_seconds(setting["charge_time"])

	# return render_template('kiosk_mode/home.html', title='Kiosk Mode', 
	# 						current_sessions=current_sessions,
	# 						sessions_and_dates=sessions_and_dates,
	# 						pic_files=pic_files.get_resized_copy(), setting=setting)

	return render_template('kiosk_mode/homeV2.html', title='Kiosk Mode', 
							current_sessions=current_sessions,
							sessions_and_dates=sessions_and_dates,
							pic_files=pic_files.get_resized_copy(), setting=setting, 
							hours=hours, minutes=minutes, seconds=seconds)


@kiosk_mode.route("/kiosk_mode/confirm_payment")
def confirm_payment():
	start_route()

	# This is where the payments will happen
	# Once they are passed, They will be redirected to make a session
	# If they fail, then they are redirected back to home
	# For now, it passes only

	# If there is already a session, Just add time to it
	# Else, Make a new session
	return redirect(url_for('kiosk_mode.make_session'))

@kiosk_mode.route("/kiosk_mode/make_session")
def make_session():
	start_route()

	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	# Only make a session if there is no session currently available
	if not current_sessions.has_sessions():
		devi_id_number = Device_ID.query.first().id_number
		
		try:
			payload = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		# setting = Settings.query.first()
		setting = payload.json()

		# current_sessions.add_session(amount_paid=setting.price, location=setting.location,
		# 								port="", increment_size=setting.charge_time, increments=1)
		current_sessions.add_session(amount_paid=setting["price"], location=setting["location"],
										port="", increment_size=setting["charge_time"], increments=1)
		flash('Session Added Successfully! You may start charging now.')

	return redirect(url_for('kiosk_mode.home'))