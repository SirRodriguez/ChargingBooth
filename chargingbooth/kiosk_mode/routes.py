import string
import math
import random
import secrets
import os
from datetime import datetime
from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, logout_user
from chargingbooth import db, bcrypt, current_sessions, service_ip, settings_cache
from chargingbooth.kiosk_mode.utils import (start_route, get_offset_dates_initiated, get_offset_dates_end,
											split_seconds, is_registered)
from chargingbooth.models import PFI, Device_ID
import requests
from requests.auth import HTTPBasicAuth

kiosk_mode = Blueprint('kiosk_mode', __name__)

## Test routes


@kiosk_mode.route("/setup")
def setup():
	return render_template("paypal/setup.html")

@kiosk_mode.route("/paypal_test")
def paypal():
	# Authenticate token
	try:
		# url
		url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
		# header
		headers = {
			"Accept": "application/json",
			"Accept-Language": "en_US"
		}
		# Basic Auth
		Client_ID = os.environ.get('CLIENT_ID')
		SECRET = os.environ.get('SECRET')
		auth = HTTPBasicAuth(Client_ID, SECRET)
		# Data
		data = {
			"grant_type": "client_credentials"
		}
		# POST
		payload = requests.post(url, headers=headers, auth=auth, data=data)
		access_token = payload.json()['access_token']
	except Exception as e:
		print("In Exception")
		print(e)

	# generate token
	try:
		url = "https://api-m.sandbox.paypal.com/v1/identity/generate-token"
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer " + access_token,
			"Accept-Language": "en_US"
		}
		payload = requests.post(url, headers=headers)
		client_token = payload.json()["client_token"]
	except Exception as e:
		print("In Exception")
		print(e)


	return render_template("paypal/Checkout.html", client_ID=os.environ.get('CLIENT_ID'), client_token=client_token)

## End test routes

@kiosk_mode.route("/kiosk_mode", methods=['GET', 'POST'])
def home():
	start_route()

	devi_id_number = Device_ID.query.first().id_number

	# Grab the number of images the service has, also settings
	try:
		payload = requests.get(service_ip + '/device/img_count/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))

	pl_json = payload.json()

	# Check if registered
	if not pl_json["registered"]:
		return redirect(url_for('register.home'))

	img_count = pl_json["image_count"]
	setting = pl_json["settings"]

	# Place Settings in the cache
	settings_cache.set_values(
		toggle_pay=setting["toggle_pay"],
		price=setting["price"],
		charge_time=setting["charge_time"],
		time_offset=setting["time_offset"],
		location=setting["location"],
		aspect_ratio_width=setting["aspect_ratio_width"],
		aspect_ratio_height=setting["aspect_ratio_height"]
	)

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
							service_ip=service_ip,
							devi_id_number=devi_id_number,
							img_count=img_count,
							random_hex=random_hex,
							setting=setting, 
							hours=hours, minutes=minutes, seconds=seconds)

# This is used when a user creats a session. It is much faster as the settings and image
# count are cached and passed through. It avoids the delayed timer showing on the UI.
@kiosk_mode.route("/kiosk_mode/<int:image_count>", methods=['GET', 'POST'])
def home_fast(image_count):
	start_route()

	devi_id_number = Device_ID.query.first().id_number

	sessions = current_sessions.local_sessions.values()

	# Grab the settings from cache
	# It is put in a map because the html page access it that way
	setting = {}
	setting["toggle_pay"] = settings_cache.get_toggle_pay()
	setting["price"] = settings_cache.get_price()
	setting["charge_time"] = settings_cache.get_charge_time()
	setting["time_offset"] = settings_cache.get_time_offset()
	setting["location"] = settings_cache.get_location()
	setting["aspect_ratio_width"] = settings_cache.get_aspect_ratio_width()
	setting["aspect_ratio_height"] = settings_cache.get_aspect_ratio_height()

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
							service_ip=service_ip,
							devi_id_number=devi_id_number,
							img_count=image_count,
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

	# Only make a session if there is no session currently available
	if not current_sessions.has_sessions():
		devi_id_number = Device_ID.query.first().id_number

		# Grab the number of images the service has, also settings
		try:
			payload = requests.get(service_ip + '/device/img_count/' + devi_id_number)
		except Exception as e:
			print(e)
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.register'))

		pl_json = payload.json()

		# Check if registered
		if not pl_json["registered"]:
			return redirect(url_for('register.home'))

		img_count = pl_json["image_count"]
		setting = pl_json["settings"]

		# Place Settings in the cache
		settings_cache.set_values(
			toggle_pay=setting["toggle_pay"],
			price=setting["price"],
			charge_time=setting["charge_time"],
			time_offset=setting["time_offset"],
			location=setting["location"],
			aspect_ratio_width=setting["aspect_ratio_width"],
			aspect_ratio_height=setting["aspect_ratio_height"]
		)

		current_sessions.add_session(amount_paid=setting["price"], location=setting["location"],
										port="", increment_size=setting["charge_time"], increments=1)
		flash('Session Added Successfully! You may start charging now.')

	# return redirect(url_for('kiosk_mode.home_fast', image_count=img_count))
	return redirect(url_for('kiosk_mode.home', image_count=img_count))