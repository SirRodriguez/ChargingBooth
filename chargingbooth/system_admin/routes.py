from flask import render_template, Blueprint, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from chargingbooth import db, bcrypt, current_sessions
from chargingbooth.models import User, Session, Settings, PFI
from chargingbooth.system_admin.forms import (LoginForm, RegistrationForm, UpdateAccountForm,
												RequestRestForm, RequestRestForm, 
												ResetPasswordForm, SettingsForm, 
												SlideShowPicsForm, RemovePictureForm)
from chargingbooth.system_admin.utils import (send_reset_email, get_offset_dates_initiated, 
												create_csv_file_from_sessions, create_plot, 
												get_min_sec, save_figure, remove_png, count_years, 
												create_bar_years)
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os


system_admin = Blueprint('system_admin', __name__)

@system_admin.route("/system_admin")
def home():
	return redirect(url_for('system_admin.login'))

@system_admin.route("/system_admin/login", methods=['GET', 'POST'])
def login():
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
	return render_template('system_admin/main.html', title='System Admin Main')

# This is needed to be removed after production
# This is only used to adjust the database for an admin user
@system_admin.route("/system_admin/register", methods=['GET', 'POST'])
def register():
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
	form = SettingsForm()
	if form.validate_on_submit():
		Settings.query.first().toggle_pay = form.toggle_pay.data
		Settings.query.first().price = form.price.data
		# Settings.query.first().charge_time = form.charge_time.data
		minutes = form.charge_time_min.data
		seconds = form.charge_time_sec.data
		Settings.query.first().charge_time = minutes*60 + seconds;
		Settings.query.first().time_offset = form.time_zone.data
		Settings.query.first().location = form.location.data

		# Check if aspect ration is different so that it can resize all images
		resize = False
		if Settings.query.first().aspect_ratio_width != float(form.aspect_ratio.data.split(":")[0]) and \
			Settings.query.first().aspect_ratio_height != float(form.aspect_ratio.data.split(":")[1]):
			resize = True

		Settings.query.first().aspect_ratio_width = float(form.aspect_ratio.data.split(":")[0])
		Settings.query.first().aspect_ratio_height = float(form.aspect_ratio.data.split(":")[1])

		if resize:
			pic_files = PFI()
			pic_files.resize_all(Settings.query.first().aspect_ratio_width, Settings.query.first().aspect_ratio_height)

		db.session.commit()
		flash('Settings have been updated!', 'success')
		return redirect(url_for('system_admin.settings'))
	elif request.method == 'GET':
		form.toggle_pay.data = Settings.query.first().toggle_pay
		form.price.data = Settings.query.first().price
		# form.charge_time.data = Settings.query.first().charge_time
		minutes, seconds = get_min_sec(seconds=Settings.query.first().charge_time)
		form.charge_time_min.data = minutes
		form.charge_time_sec.data = seconds
		form.time_zone.data = Settings.query.first().time_offset
		form.location.data = Settings.query.first().location
		form.aspect_ratio.data = str(Settings.query.first().aspect_ratio_width) + ":" + str(Settings.query.first().aspect_ratio_height)

	return render_template('system_admin/settings.html', title='Settings', form=form)

@system_admin.route("/system_admin/data")
@login_required
def data():
	return render_template("system_admin/data.html", title="Data")

@system_admin.route("/system_admin/list_data")
@login_required
def view_data():
	page = request.args.get('page', 1, type=int)

	sessions = Session.query.order_by(Session.date_initiated.desc()).paginate(page=page, per_page=10)
	date_strings = get_offset_dates_initiated(sessions=sessions.items,
									time_offset=Settings.query.first().time_offset)

	sessions_and_dates = zip(sessions.items, date_strings) # Pack them together to iterate simultaniously
	return render_template("system_admin/list_data.html", title="List Data", sessions=sessions, sessions_and_dates=sessions_and_dates)

@system_admin.route("/system_admin/graph_data")
@login_required
def graph_data():
	return render_template("system_admin/graph_data.html", title="Graph Data")

@system_admin.route("/system_admin/graph_data/all_years")
@login_required
def graph_all_years():
	# Sessions come with these variable:
	# {id, duration, power_used, amount_paid, date_initiated, location, port, increment_size, increments}
	# variable that have numerical values that only work with graph are:
	# {id, duration, power_used, amount_paid, date_initiated, increment_size, increments}

	

	# Delete old pic files
	remove_png()

	# Grab the sessions
	sessions = Session.query.all()

	# This is what will be used for the bar graph
	date_strings = get_offset_dates_initiated(sessions=sessions,
									time_offset=Settings.query.first().time_offset)

	# For every year, count how many sessions occured
	# Returns a dictionary
	years = count_years(date_strings)

	create_bar_years(years)


	# CSV file comes out ready with session data inside of it.
	# csv_file = create_csv_file_from_sessions(sessions=sessions)

	# # Create the panda file
	# df = pd.read_csv(csv_file, delimiter=',')

	# Create the plot
	# create_plot(df, x_label="date_initiated", y_label="duration")
	
	# Create the pic file to show
	pic_name = save_figure()

	return render_template("system_admin/graph_data_all_years.html", title="Years", pic_name=pic_name)

@system_admin.route("/system_admin/graph_data/year")
@login_required
def graph_year():
	return render_template("system_admin/graph_data_year.html", title="Year")

@system_admin.route("/system_admin/graph_data/month")
@login_required
def graph_month():
	return render_template("system_admin/graph_data_month.html", title="Year")

@system_admin.route("/system_admin/graph_data/day")
@login_required
def graph_day():
	return render_template("system_admin/graph_data_day.html", title="Year")

@system_admin.route("/system_admin/local_data")
@login_required
def view_local_data():
	sessions = current_sessions.local_sessions.values()
	date_strings = get_offset_dates_initiated(sessions=sessions, time_offset=Settings.query.first().time_offset)

	sessions_and_dates = zip(sessions, date_strings)
	return render_template("system_admin/local_data.html", title="Local Data", 
							current_sessions=current_sessions, sessions_and_dates=sessions_and_dates)

@system_admin.route("/system_admin/slide_show_pics", methods=['GET', 'POST'])
@login_required
def slide_show_pics():

	remove_pic_form = RemovePictureForm()
	if remove_pic_form.validate_on_submit() and remove_pic_form.removals.data != "":
		flash('Picture Files have been removed', 'success')

	return render_template("system_admin/slide_show_pics.html", title="Slide Show Pictures")

@system_admin.route("/system_admin/add_slides", methods=['GET', 'POST'])
@login_required
def upload_image():
	pic_files = PFI()

	form = SlideShowPicsForm()
	if form.validate_on_submit():
		for file in form.picture.data:
			pic_files.save_file(file, Settings.query.first().aspect_ratio_width,
								Settings.query.first().aspect_ratio_height)

		flash('Pictures has been uploaded', 'success')
		return redirect(url_for('system_admin.upload_image'))

	return render_template("system_admin/upload_image.html", title="Upload Image", form=form,
							pic_files=pic_files.get_resized_copy())

@system_admin.route("/system_admin/remove_slides", methods=['GET', 'POST'])
@login_required
def remove_image():
	pic_files = PFI()
	pic_files_length = pic_files.get_length()

	form = RemovePictureForm()
	if form.validate_on_submit():
		pic_files.remove_images(form.removals.data)
		flash("Images have been deleted!", 'success')
		return redirect(url_for('system_admin.remove_image'))

	return render_template("system_admin/remove_image.html", title="Remove Images", form=form,
							pic_files=pic_files.get_resized_copy(), pic_files_length=pic_files_length)