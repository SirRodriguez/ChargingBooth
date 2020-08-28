import string
import math
import random
from datetime import datetime
from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, logout_user
from chargingbooth import db, bcrypt, current_sessions
from chargingbooth.models import Session, Settings
from chargingbooth.kiosk_mode.forms import DataForm, RandomDataForm, SessionForm, ConfirmSessionForm
from chargingbooth.kiosk_mode.utils import start_route
from chargingbooth.models import PFI

kiosk_mode = Blueprint('kiosk_mode', __name__)


@kiosk_mode.route("/kiosk_mode", methods=['GET', 'POST'])
def home():
	start_route()

	pic_files = PFI()
	setting = Settings.query.first()

	return render_template('kiosk_mode_home.html', title='Kiosk Mode', current_sessions=current_sessions,
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

		current_sessions.add_session(amount_paid=setting.cents_per_second * setting.charge_time, location="No Location",
										port="1", increment_size=setting.charge_time, increments=1)
		flash('Session Added Successfully! You may start charging now.')

	return redirect(url_for('kiosk_mode.home'))

@kiosk_mode.route("/kiosk_mode/simulated_session")
def simulated_session():
	start_route()

	setting = Settings.query.first()
	return render_template('kiosk_mode_simulated_session.html', title='Simulate', setting=setting)

@kiosk_mode.route("/kiosk_mode/session", methods=['GET', 'POST'])
def session():
	start_route()

	setting = Settings.query.first()
	form = SessionForm()
	if form.validate_on_submit():
		amount_paid = setting.cents_per_second * setting.charge_time * form.num_of_sessions.data
		location = "current_location"
		port = "current_port"
		increment_size = setting.charge_time
		increments = form.num_of_sessions.data
		current_sessions.add_session(amount_paid, location, port, increment_size, increments)
		flash('You have created a session and you may now start charging.', 'success')
		return redirect(url_for('kiosk_mode.home'))

	return render_template('kiosk_mode_session.html', title='Session', form=form, setting=setting)

@kiosk_mode.route("/kiosk_mode/add_session", methods=['GET', 'POST'])
def add_session():
	start_route()

	form = DataForm()
	if form.validate_on_submit():
		session = Session(duration=form.duration.data, power_used=form.power_used.data, 
							amount_paid=form.amount_paid.data, location=form.location.data, port=form.port.data, 
							increment_size=form.increment_size.data, increments=form.increments.data)
		db.session.add(session)
		db.session.commit()
		flash('Session Added!', 'success')
		return redirect(url_for('kiosk_mode.add_session'))
	return render_template('kiosk_mode_add_session.html', title='Add', form=form)

@kiosk_mode.route("/kiosk_mode/add_rand_session", methods=['GET', 'POST'])
def add_rand_session():
	start_route()

	form = RandomDataForm()
	if form.validate_on_submit():

		if form.min_duration.data > form.max_duration.data:
			flash('Min Duration must be less than Max Duration', 'danger')
			return render_template('kiosk_mode_add_rand_session.html', form=form)

		elif form.min_power_used.data > form.max_power_used.data:
			flash('Min Power Used must be less than Max Power Used', 'danger')
			return render_template('kiosk_mode_add_rand_session.html', form=form)

		elif form.min_amount_paid.data > form.max_amount_paid.data:
			flash('Min Cents must be less than Max Cents', 'danger')
			return render_template('kiosk_mode_add_rand_session.html', form=form)

		elif form.min_port.data > form.max_port.data:
			flash('Min Port must be less than Max Port', 'danger')
			return render_template('kiosk_mode_add_rand_session.html', form=form)

		elif form.min_increment_size.data > form.max_increment_size.data:
			flash('Min Increment Size must be less than Max Increment Size', 'danger')
			return render_template('kiosk_mode_add_rand_session.html', form=form)

		else:
			for s in range(form.num_sessions.data):
				duration = random.randint(form.min_duration.data, form.max_duration.data)
				power_used = random.uniform(form.min_power_used.data, form.max_power_used.data)
				amount_paid = random.randint(form.min_amount_paid.data, form.max_amount_paid.data)
				
				location = ""
				if form.location.data is not "":
					location = form.location.data
				else:
					location = random.choice(string.ascii_letters)

				port = random.randint(form.min_port.data, form.max_port.data)
				increment_size = random.randint(form.min_increment_size.data, form.max_increment_size.data)
				increments = math.ceil(duration / increment_size)

				session = Session(duration=duration, power_used=power_used, amount_paid=amount_paid,
									location=location, port=port, increment_size=increment_size,
									increments=increments)

				db.session.add(session)
			db.session.commit()

			flash('Sessions Added!', 'success')
			return redirect(url_for('kiosk_mode.add_rand_session'))

	return render_template('kiosk_mode_add_rand_session.html', title='Random', form=form)