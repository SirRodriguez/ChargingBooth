import string
import math
import random
import secrets
import os
from datetime import datetime
from flask import render_template, Blueprint, redirect, url_for, flash, request, jsonify
from flask_login import current_user, logout_user
from chargingbooth import db, bcrypt, current_sessions, service_ip, cardTerminal, startCardSessionFlag
from chargingbooth.kiosk_mode.utils import (start_route, get_offset_dates_initiated, get_offset_dates_end,
											split_seconds, is_registered, get_min_sec)
from chargingbooth.models import PFI, Device_ID
import requests
from requests.auth import HTTPBasicAuth

kiosk_mode = Blueprint('kiosk_mode', __name__)

@kiosk_mode.route("/kiosk_mode", methods=['GET', 'POST'])
def home():
	start_route()

	# Rest the card session flag
	startCardSessionFlag.resetFlag()

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

@kiosk_mode.route("/kiosk_mode/enable_payment")
def enablePayment():
	startCardSessionFlag.setFlag()
	return redirect(url_for('kiosk_mode.confirm_payment'))


@kiosk_mode.route("/kiosk_mode/confirm_payment")
def confirm_payment():
	start_route()

	if(startCardSessionFlag.getFlag() == False):
		return redirect(url_for('kiosk_mode.home'))

	# Rest the card session flag
	startCardSessionFlag.resetFlag()

	# This is where the payments will happen
	# Once they are passed, They will be redirected to make a session
	# If they fail, then they are redirected back to home
	# For now, it passes only

	devi_id_number = Device_ID.query.first().id_number

	# Grab the settings
	try:
		payload = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))

	setting = payload.json()

	# Check if registered
	if not setting["registered"]:
		return redirect(url_for('register.home'))

	toggle_pay = setting["toggle_pay"]
	price = setting["price"]
	minutes, seconds = get_min_sec(seconds=setting["charge_time"])
	charge_time_min = minutes
	charge_time_sec = seconds
	time_zone = setting["time_offset"]
	location = setting["location"]
	aspect_ratio = str( int(setting["aspect_ratio_width"]) if (setting["aspect_ratio_width"]).is_integer() else setting["aspect_ratio_width"] ) \
								+ ":" + str( int(setting["aspect_ratio_height"]) if (setting["aspect_ratio_height"]).is_integer() else setting["aspect_ratio_height"] ) 

	# Check to see if toggle pay is on
	if toggle_pay:
		# Start the web socket to make get a payment
		cardTerminal.startPayment(price)

		return render_template('kiosk_mode/confirm_payment.html', 
								title='Confirm Payment', 
								service_ip=service_ip,
								devi_id_number=devi_id_number,
								toggle_pay=toggle_pay,
								price=price,
								minutes=minutes,
								seconds=seconds,
								charge_time_min=charge_time_min,
								charge_time_sec=charge_time_sec,
								time_zone=time_zone,
								location=location,
								aspect_ratio=aspect_ratio)
	else:
		return redirect(url_for('kiosk_mode.make_session'))

@kiosk_mode.route("/kiosk_mode/make_session")
def make_session():
	start_route()

	# Rest the card session flag
	startCardSessionFlag.resetFlag()

	# Only make a session if there is no session currently available
	if not current_sessions.has_sessions() and cardTerminal.checkPaymentSuccess():
		cardTerminal.confirmPaymentSuccess()

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

		# img_count = pl_json["image_count"]
		setting = pl_json["settings"]
		
		current_sessions.add_session(amount_paid=setting["price"], location=setting["location"],
										port="", increment_size=setting["charge_time"], increments=1)
		flash('Session Added Successfully! You may start charging now.')

	return redirect(url_for('kiosk_mode.home'))

@kiosk_mode.route("/kiosk_mode/transaction_timeout")
def transaction_timeout():
	start_route()

	# Rest the card session flag
	startCardSessionFlag.resetFlag()

	cardTerminal.confirmTransactionTimedOut()

	return redirect(url_for('kiosk_mode.home'))

@kiosk_mode.route("/kiosk_mode/cancel_transaction")
def cancleTransaction():
	start_route()

	# Rest the card session flag
	startCardSessionFlag.resetFlag()

	cardTerminal.cancelTransaction()

	return redirect(url_for('kiosk_mode.home'))

@kiosk_mode.route("/kiosk_mode/payment_declined")
def payment_declined():
	start_route()

	# Rest the card session flag
	startCardSessionFlag.resetFlag()

	cardTerminal.confirmPaymentDeclined()

	flash('Sorry your card was declined')
	return redirect(url_for('kiosk_mode.home'))

@kiosk_mode.route("/kiosk_mode/payment_error")
def payment_error():
	start_route()

	# Rest the card session flag
	startCardSessionFlag.resetFlag()

	cardTerminal.confirmPaymentError()

	flash('Sorry there was an error with the payment')
	return redirect(url_for('kiosk_mode.home'))

@kiosk_mode.route("/kiosk_mode/checkPaymentStatus")
def checkPaymentStatus():
	payload = {
		'paymentSuccess': cardTerminal.checkPaymentSuccess(),
		'paymentTimedOut': cardTerminal.checkTransactionTimedOut(),
		'paymentDeclined': cardTerminal.checkPaymentDeclined(),
		'paymentError': cardTerminal.checkPaymentError(),
		'cardNeedsInserted': cardTerminal.checkCardNeedsInsert(),
		'pleaseWait': cardTerminal.checkPleaseWait(),
		'cardDetected': cardTerminal.checkCardDetected(),
		'processingCard': cardTerminal.checkProcessingCard(),
		'goingOnline': cardTerminal.checkGoingOnline(),
		'removeCard': cardTerminal.checkRemoveCard()
	}

	# print('--paymentSuccess: ', payload['paymentSuccess'])
	# print('--paymentTimedOut: ', payload['paymentTimedOut'])
	# print('--paymentDeclined: ', payload['paymentDeclined'])
	# print('--paymentError: ', payload['paymentError'])
	# print('--cardNeedsInserted:', payload['cardNeedsInserted'])
	# print('--pleaseWait:', payload['pleaseWait'])
	# print('--cardDetected:', payload['cardDetected'])
	# print('--processingCard:', payload['processingCard'])
	# print('--goingOnline:', payload['goingOnline'])
	# print('--removeCard:', payload['removeCard'])

	resp = jsonify(payload)
	resp.status_code = 200
	return resp

# This function only works for one session at a time functionality
@kiosk_mode.route("/kiosk_mode/get_session_time_remaining")
def get_session_time_remaining():
	payload = {}

	# If there are no sessions
	if not current_sessions.has_sessions():
		payload['has_sessions'] = False

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	payload['has_sessions'] = True

	time_list = current_sessions.get_sessions_remaining_time()

	payload['time_remaining'] = time_list[0]

	resp = jsonify(payload)
	resp.status_code = 200
	return resp