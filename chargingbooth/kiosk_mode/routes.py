import string
import math
import random
from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import current_user, logout_user
from chargingbooth import db, bcrypt
from chargingbooth.models import Session, Settings
from chargingbooth.kiosk_mode.forms import DataForm, RandomDataForm
from chargingbooth.kiosk_mode.utils import start_route

kiosk_mode = Blueprint('kiosk_mode', __name__)


@kiosk_mode.route("/kiosk_mode")
def home():
	start_route()

	return render_template('kiosk_mode_home.html', title='Kiosk Mode')

@kiosk_mode.route("/kiosk_mode/simulated_session")
def simulated_session():
	start_route()

	setting = Settings.query.first()
	return render_template('kiosk_mode_simulated_session.html', title='Simulate', setting=setting)

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