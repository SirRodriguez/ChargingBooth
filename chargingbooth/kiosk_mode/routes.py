import string
import math
import random
import secrets
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

	devi_id_number = Device_ID.query.first().id_number

	# Grab settings from site
	try:
		payload = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	setting = payload.json()

	# Grab the number of images the service has
	try:
		payload = requests.get(service_ip + '/device/img_count/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	img_count = payload.json()["image_count"]

	sessions = current_sessions.local_sessions.values()

	date_strings = get_offset_dates_initiated(sessions=sessions, time_offset=setting["time_offset"])
	date_end_str = get_offset_dates_end(sessions=sessions, time_offset=setting["time_offset"])

	sessions_and_dates = zip(sessions, date_strings, date_end_str)

	# Get the total hours, minutes, seconds for the session time
	# hours, minutes, seconds = split_seconds(setting.charge_time)
	hours, minutes, seconds = split_seconds(setting["charge_time"])

	# Random hex, used in the url of the images in order to reset the cache of the browser
	random_hex = secrets.token_hex(8)

	return render_template('kiosk_mode/homeV2.html', 
							title='Kiosk Mode', 
							current_sessions=current_sessions,
							sessions_and_dates=sessions_and_dates,
							pic_files=pic_files.get_resized_copy(),
							service_ip=service_ip,
							devi_id_number=devi_id_number,
							img_count=img_count,
							random_hex=random_hex,
							setting=setting, 
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

		setting = payload.json()

		current_sessions.add_session(amount_paid=setting["price"], location=setting["location"],
										port="", increment_size=setting["charge_time"], increments=1)
		flash('Session Added Successfully! You may start charging now.')

	return redirect(url_for('kiosk_mode.home'))