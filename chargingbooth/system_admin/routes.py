from flask import render_template, Blueprint, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from chargingbooth import db, bcrypt, current_sessions, service_ip
from chargingbooth.models import User, Session, Settings, PFI, Device_ID
from chargingbooth.system_admin.forms import (LoginForm, RegistrationForm, UpdateAccountForm,
												RequestRestForm, RequestRestForm, 
												ResetPasswordForm, SettingsForm, 
												SlideShowPicsForm, RemovePictureForm,
												YearForm, MonthForm, DayForm)
from chargingbooth.system_admin.utils import (send_reset_email, get_offset_dates_initiated,
												get_min_sec, save_figure, remove_png, count_years, 
												create_bar_years, count_months, create_bar_months,
												count_days, create_bar_days, count_hours, create_bar_hours,
												is_registered)
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import secrets
import requests

system_admin = Blueprint('system_admin', __name__)

@system_admin.route("/system_admin")
def home():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	return redirect(url_for('system_admin.login'))

@system_admin.route("/system_admin/login", methods=['GET', 'POST'])
def login():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	if current_user.is_authenticated:
		return redirect(url_for('system_admin.main'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next')
			return redirect(url_for('system_admin.main'))
		else:
			flash('Loging Unsuccessful. Please check username and password', 'danger')
	return render_template('system_admin/login.html', title='System Admin Login', form=form)

@system_admin.route("/system_admin/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('system_admin.home'))


@system_admin.route("/system_admin/main")
@login_required
def main():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	return render_template('system_admin/main.html', title='System Admin Main')

# This is needed to be removed after production
# This is only used to adjust the database for an admin user
@system_admin.route("/system_admin/register", methods=['GET', 'POST'])
def register():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	if current_user.is_authenticated:
		return redirect(url_for('system_admin.main'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('system_admin.login'))
	return render_template('system_admin/register.html', title='Register', form=form)


@system_admin.route("/system_admin/account", methods=['GET', 'POST'])
@login_required
def account():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('system_admin.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('system_admin/account.html', title='Account', form=form)


# When logged out and forgot password
@system_admin.route("/system_admin/reset_password", methods=['GET', 'POST'])
def reset_request():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	if current_user.is_authenticated:
		return redirect(url_for('system_admin.home'))
	form = RequestRestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user, logged_in=False)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('system_admin.login'))
	return render_template('system_admin/reset_request.html', title='Reset Password', form=form)

@system_admin.route("/system_admin/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('system_admin.home'))

	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('system_admin.reset_request'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! You are now able to log in.', 'success')
		return redirect(url_for('system_admin.login'))
	return render_template('system_admin/reset_token.html', title='Reset Password', form=form)



#When logged in and changing password
@system_admin.route("/system_admin/change_password", methods=['GET', 'POST'])
@login_required
def change_request():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))
		
	user = User.query.filter_by(email=current_user.email).first()
	send_reset_email(user, logged_in=True)
	flash('An email has been sent with instructions to reset your password.', 'info')
	return redirect(url_for('system_admin.account'))

@system_admin.route("/system_admin/change_password/<token>", methods=['GET', 'POST'])
@login_required 
def change_token(token):
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('system_admin.reset_request'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated!', 'success')
		return redirect(url_for('system_admin.login'))
	return render_template('system_admin/reset_token.html', title='Reset Password', form=form)


@system_admin.route("/system_admin/settings", methods=['GET', 'POST'])
@login_required
def settings():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	devi_id_number = Device_ID.query.first().id_number
	# Grab settings from site
	try:
		payload = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	# setting = Settings.query.first()
	setting = payload.json()

	form = SettingsForm()
	if form.validate_on_submit():
		pl_send = {}

		pl_send["toggle_pay"] = form.toggle_pay.data
		pl_send["price"] = form.price.data
		# Settings.query.first().charge_time = form.charge_time.data
		minutes = form.charge_time_min.data
		seconds = form.charge_time_sec.data
		pl_send["charge_time"] = minutes*60 + seconds;
		pl_send["time_offset"] = form.time_zone.data
		pl_send["location"] = form.location.data

		# Check if aspect ration is different so that it can resize all images
		# resize = False
		# if setting["aspect_ratio_width"] != float(form.aspect_ratio.data.split(":")[0]) or \
		# 	setting["aspect_ratio_height"] != float(form.aspect_ratio.data.split(":")[1]):
		# 	resize = True

		pl_send["aspect_ratio_width"] = float(form.aspect_ratio.data.split(":")[0])
		pl_send["aspect_ratio_height"] = float(form.aspect_ratio.data.split(":")[1])

		# if resize:
		# 	pic_files = PFI()
		# 	pic_files.resize_all(pl_send["aspect_ratio_width"], pl_send["aspect_ratio_height"])


		response = requests.put(service_ip + '/device/update_setting/' + devi_id_number, json=pl_send)

		if response.status_code == 204 or response.status_code == 200:
			flash('Settings have been updated!', 'success')
		elif response.status_code == 400:
			flash('Server could not find device!', 'danger')
		else:
			flash('Something happened and settings were not updated.', 'danger')

		# db.session.commit()
		# flash('Settings have been updated!', 'success')
		return redirect(url_for('system_admin.settings'))
	elif request.method == 'GET':
		form.toggle_pay.data = setting["toggle_pay"]
		form.price.data = setting["price"]
		# form.charge_time.data = Settings.query.first().charge_time
		minutes, seconds = get_min_sec(seconds=setting["charge_time"])
		form.charge_time_min.data = minutes
		form.charge_time_sec.data = seconds
		form.time_zone.data = setting["time_offset"]
		form.location.data = setting["location"]
		# form.aspect_ratio.data = str(setting["aspect_ratio_width"]) + ":" + str(setting["aspect_ratio_height"])
		form.aspect_ratio.data = str( int(setting["aspect_ratio_width"]) if (setting["aspect_ratio_width"]).is_integer() else setting["aspect_ratio_width"] ) \
									+ ":" + str( int(setting["aspect_ratio_height"]) if (setting["aspect_ratio_height"]).is_integer() else setting["aspect_ratio_height"] ) 

	return render_template('system_admin/settings.html', title='Settings', form=form)

@system_admin.route("/system_admin/data")
@login_required
def data():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	return render_template("system_admin/data.html", title="Data")

@system_admin.route("/system_admin/list_data")
@login_required
def view_data():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	devi_id_number = Device_ID.query.first().id_number

	page = request.args.get('page', 1, type=int)

	# sessions = Session.query.order_by(Session.date_initiated.desc()).paginate(page=page, per_page=10)

	try:
		payload = requests.get(service_ip + '/device/sessions/' + devi_id_number + '/' + str(page))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	# Later combine the two requests to speed up
	try:
		payload_sett = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	pl_json = payload.json()
	sess_list = pl_json["sessions"]
	iter_pages = pl_json["iter_pages"]

	# Get the settings
	settings = payload_sett.json()

	# print(sess_map)
	# print(iter_pages)


	# date_strings = get_offset_dates_initiated(sessions=sessions.items,
	# 								time_offset=Settings.query.first().time_offset)
	date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

	sessions_and_dates = zip(sess_list, date_strings) # Pack them together to iterate simultaniously
	return render_template("system_admin/list_data.html", title="List Data", iter_pages=iter_pages, 
							page=page, sessions_and_dates=sessions_and_dates)

@system_admin.route("/system_admin/graph_data")
@login_required
def graph_data():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	return render_template("system_admin/graph_data.html", title="Graph Data")

@system_admin.route("/system_admin/graph_data/all_years")
@login_required
def graph_all_years():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	# Sessions come with these variable:
	# {id, duration, power_used, amount_paid, date_initiated, location, port, increment_size, increments}
	# variable that have numerical values that only work with graph are:
	# {id, duration, power_used, amount_paid, date_initiated, increment_size, increments}

	

	devi_id_number = Device_ID.query.first().id_number

	# Grab the sessions
	# sessions = Session.query.all()
	try:
		payload = requests.get(service_ip + '/device/all_sessions/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	# Later combine the two requests to speed up
	try:
		payload_sett = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	
	# Get the sessions
	sess_list = payload.json()["sessions"]

	# Get the settings
	settings = payload_sett.json()

	# Delete old pic files
	remove_png()

	# This is what will be used for the bar graph
	date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

	# For every year, count how many sessions occured
	# Returns a dictionary
	years = count_years(dates=date_strings)

	create_bar_years(years=years)
	
	# Create the pic file to show
	pic_name = save_figure()

	return render_template("system_admin/graph_data_all_years.html", title="Years", pic_name=pic_name)

@system_admin.route("/system_admin/graph_data/year", methods=['GET', 'POST'])
@login_required
def graph_year():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	form = YearForm()
	if form.validate_on_submit():

		devi_id_number = Device_ID.query.first().id_number

		# Grab the sessions
		# sessions = Session.query.all()
		try:
			payload = requests.get(service_ip + '/device/all_sessions/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		# Later combine the two requests to speed up
		try:
			payload_sett = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		
		# Get the sessions
		sess_list = payload.json()["sessions"]

		# Get the settings
		settings = payload_sett.json()


		# Delete old pic files
		remove_png()

		# This is what will be used for the bar graph
		date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

		# For every month in the given year, count how many sessions occured
		# returns a dictionary
		months = count_months(dates=date_strings, year=form.year.data)

		create_bar_months(months=months, year=form.year.data)

		# Create the pic file to show
		pic_name = save_figure()

		return render_template("system_admin/graph_data_year.html", title="Year", form=form, pic_name=pic_name)

	return render_template("system_admin/graph_data_year.html", title="Year", form=form)

@system_admin.route("/system_admin/graph_data/month", methods=['GET', 'POST'])
@login_required
def graph_month():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	form = MonthForm()
	if form.validate_on_submit():

		devi_id_number = Device_ID.query.first().id_number

		# Grab the sessions
		# sessions = Session.query.all()
		try:
			payload = requests.get(service_ip + '/device/all_sessions/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		# Later combine the two requests to speed up
		try:
			payload_sett = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		
		# Get the sessions
		sess_list = payload.json()["sessions"]

		# Get the settings
		settings = payload_sett.json()


		# Delete old pic files
		remove_png()

		# This is what will be used for the bar graph
		date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

		# For every day in a given month of a given year, count how many sessions occured
		# Returns a dictionary
		days = count_days(dates=date_strings, year=form.year.data, month=form.month.data)

		create_bar_days(days=days, month=form.month.data, year=form.year.data)

		# Create the pic file to show
		pic_name = save_figure()

		return render_template("system_admin/graph_data_month.html", title="Month", form=form, pic_name=pic_name)
	
	return render_template("system_admin/graph_data_month.html", title="Month", form=form)

@system_admin.route("/system_admin/graph_data/day", methods=['GET', 'POST'])
@login_required
def graph_day():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	form = DayForm()
	if form.validate_on_submit():

		devi_id_number = Device_ID.query.first().id_number

		# Grab the sessions
		# sessions = Session.query.all()
		try:
			payload = requests.get(service_ip + '/device/all_sessions/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		# Later combine the two requests to speed up
		try:
			payload_sett = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		
		# Get the sessions
		sess_list = payload.json()["sessions"]

		# Get the settings
		settings = payload_sett.json()

		# Delete old pic files
		remove_png()

		# This is what will be used for the bar graph
		date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])


		# fix form.day.data (ex from 4 to 04)
		if int(form.day.data) < 10:
			form.day.data = '0' + str(int(form.day.data))

		# For every hour in a given day of a given month of a given year, count the sessions
		# Returns a dictionary
		hours = count_hours(dates=date_strings, day=form.day.data, month=form.month.data, year=form.year.data)

		create_bar_hours(hours=hours, day=form.day.data, month=form.month.data, year=form.year.data)

		# Create the pic file to show
		pic_name = save_figure()

		return render_template("system_admin/graph_data_day.html", title="Day", form=form, pic_name=pic_name)

	return render_template("system_admin/graph_data_day.html", title="Day", form=form)

@system_admin.route("/system_admin/local_data")
@login_required
def view_local_data():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	sessions = current_sessions.local_sessions.values()
	date_strings = get_offset_dates_initiated(sessions=sessions, time_offset=Settings.query.first().time_offset)

	sessions_and_dates = zip(sessions, date_strings)
	return render_template("system_admin/local_data.html", title="Local Data", 
							current_sessions=current_sessions, sessions_and_dates=sessions_and_dates)

@system_admin.route("/system_admin/slide_show_pics", methods=['GET', 'POST'])
@login_required
def slide_show_pics():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	return render_template("system_admin/slide_show_pics.html", title="Slide Show Pictures")

@system_admin.route("/system_admin/add_slides", methods=['GET', 'POST'])
@login_required
def upload_image():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	# pic_files = PFI()

	devi_id_number = Device_ID.query.first().id_number

	form = SlideShowPicsForm()
	if form.validate_on_submit():
		# for file in form.picture.data:
		# 	pic_files.save_file(file, Settings.query.first().aspect_ratio_width,
		# 						Settings.query.first().aspect_ratio_height)


		image_files = []
		for file in form.picture.data:
			image_files.append(('image', ( file.filename, file.read() )  ))

		# Do the post here
		response = requests.post(service_ip + '/device/images/upload/' + devi_id_number, files=image_files)

		flash('Pictures has been uploaded', 'success')
		return redirect(url_for('system_admin.upload_image'))

	

	# Grab the number of images the service has
	try:
		payload = requests.get(service_ip + '/device/img_count/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	img_count = payload.json()["image_count"]

	random_hex = secrets.token_hex(8)

	return render_template("system_admin/upload_image.html", 
							title="Upload Image", 
							form=form,
							service_ip=service_ip,
							devi_id_number=devi_id_number,
							img_count=img_count,
							random_hex=random_hex)
							# pic_files=pic_files.get_resized_copy())

@system_admin.route("/system_admin/remove_slides", methods=['GET', 'POST'])
@login_required
def remove_image():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	devi_id_number = Device_ID.query.first().id_number

	pic_files = PFI()
	pic_files_length = pic_files.get_length()

	form = RemovePictureForm()
	if form.validate_on_submit():
		# pic_files.remove_images(form.removals.data)
		try:
			response = requests.delete(service_ip + '/device/remove_images/' + devi_id_number + '/' + form.removals.data)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('main.error'))

		if response.status_code == 204:
			flash('Images have been successfuly removed!', 'success')
		elif response.status_code == 400:
			flash('Image was not found in the server!', 'danger')
		else:
			flash("Oops! Something happened and the images were not deleted.", "danger")

		# flash("Images have been deleted!", 'success')
		# return redirect(url_for('system_admin.remove_image'))


	# Grab the number of images the service has
	try:
		payload = requests.get(service_ip + '/device/img_count/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	img_count = payload.json()["image_count"]

	random_hex = secrets.token_hex(8)


	return render_template("system_admin/remove_image.html", 
							title="Remove Images", 
							form=form,
							service_ip=service_ip,
							devi_id_number=devi_id_number,
							img_count=img_count,
							random_hex=random_hex,
							pic_files=pic_files.get_resized_copy(), 
							pic_files_length=pic_files_length)