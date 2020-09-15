import string
import math
import random
from datetime import datetime
from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, logout_user
from chargingbooth import db, bcrypt, current_sessions
from chargingbooth.models import Session, Settings
# from chargingbooth.kiosk_mode.forms import
from chargingbooth.kiosk_mode.utils import start_route, get_offset_dates_initiated, get_offset_dates_end
from chargingbooth.models import PFI

kiosk_mode = Blueprint('kiosk_mode', __name__)


@kiosk_mode.route("/kiosk_mode", methods=['GET', 'POST'])
def home():
	start_route()

	pic_files = PFI()
	setting = Settings.query.first()

	sessions = current_sessions.local_sessions.values()
	date_strings = get_offset_dates_initiated(sessions=sessions, time_offset=Settings.query.first().time_offset)
	date_end_str = get_offset_dates_end(sessions=sessions, time_offset=Settings.query.first().time_offset)

	# print(date_end_str)

	sessions_and_dates = zip(sessions, date_strings, date_end_str)

	# return render_template('kiosk_mode/home.html', title='Kiosk Mode', 
	# 						current_sessions=current_sessions,
	# 						sessions_and_dates=sessions_and_dates,
	# 						pic_files=pic_files.get_copy(), setting=setting)

	return render_template('kiosk_mode/homeV2.html', title='Kiosk Mode', 
							current_sessions=current_sessions,
							sessions_and_dates=sessions_and_dates,
							pic_files=pic_files.get_copy(), setting=setting)


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
		setting = Settings.query.first()

		current_sessions.add_session(amount_paid=setting.cents_per_second * setting.charge_time, location=setting.location,
										port="1", increment_size=setting.charge_time, increments=1)
		flash('Session Added Successfully! You may start charging now.')

	return redirect(url_for('kiosk_mode.home'))