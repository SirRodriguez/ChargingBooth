from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from chargingbooth import service_ip, current_sessions
from chargingbooth.utils import is_registered
from chargingbooth.models import Device_ID
from chargingbooth.system_admin.data.forms import YearForm, MonthForm, DayForm
from chargingbooth.system_admin.data.utils import (get_offset_dates_initiated, remove_png, save_figure,
													count_years, create_bar_years, count_months, 
													create_bar_months, count_days, create_bar_days,
													count_hours, create_bar_hours)
import requests

system_admin_data = Blueprint('system_admin_data', __name__)


@system_admin_data.route("/system_admin/data")
@login_required
def data():
	return render_template("system_admin/data/data.html", title="Data")

@system_admin_data.route("/system_admin/list_data")
@login_required
def view_data():

	devi_id_number = Device_ID.query.first().id_number

	page = request.args.get('page', 1, type=int)

	try:
		payload = requests.get(service_ip + '/device/sessions/' + devi_id_number + '/' + str(page))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	pl_json = payload.json()

	# Check if registered
	if not pl_json["registered"]:
		return redirect(url_for('register.home'))

	sess_list = pl_json["sessions"]
	iter_pages = pl_json["iter_pages"]
	settings = pl_json["settings"]

	date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

	sessions_and_dates = zip(sess_list, date_strings) # Pack them together to iterate simultaniously
	return render_template("system_admin/data/list_data.html", title="List Data", iter_pages=iter_pages, 
							page=page, sessions_and_dates=sessions_and_dates)

@system_admin_data.route("/system_admin/graph_data")
@login_required
def graph_data():
	return render_template("system_admin/data/graph_data.html", title="Graph Data")

@system_admin_data.route("/system_admin/graph_data/all_years")
@login_required
def graph_all_years():
	# Sessions come with these variable:
	# {id, duration, power_used, amount_paid, date_initiated, location, port, increment_size, increments}
	# variable that have numerical values that only work with graph are:
	# {id, duration, power_used, amount_paid, date_initiated, increment_size, increments}
	

	devi_id_number = Device_ID.query.first().id_number

	# Grab the sessions
	try:
		payload = requests.get(service_ip + '/device/all_sessions/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	pl_json = payload.json()

	# Check if registered
	if not pl_json["registered"]:
		return redirect(url_for('register.home'))

	# Get the sessions
	sess_list = pl_json["sessions"]
	settings = pl_json["settings"]

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

	return render_template("system_admin/data/graph_data_all_years.html", title="Years", pic_name=pic_name)

@system_admin_data.route("/system_admin/graph_data/year", methods=['GET', 'POST'])
@login_required
def graph_year():
	form = YearForm()
	if form.validate_on_submit():

		devi_id_number = Device_ID.query.first().id_number

		# Grab the sessions
		try:
			payload = requests.get(service_ip + '/device/all_sessions/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))
		
		pl_json = payload.json()

		# Check if registered
		if not pl_json["registered"]:
			return redirect(url_for('register.home'))

		# Get the sessions
		sess_list = pl_json["sessions"]
		settings = pl_json["settings"]

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

		return render_template("system_admin/data/graph_data_year.html", title="Year", form=form, pic_name=pic_name)

	return render_template("system_admin/data/graph_data_year.html", title="Year", form=form)

@system_admin_data.route("/system_admin/graph_data/month", methods=['GET', 'POST'])
@login_required
def graph_month():
	form = MonthForm()
	if form.validate_on_submit():

		devi_id_number = Device_ID.query.first().id_number

		# Grab the sessions
		try:
			payload = requests.get(service_ip + '/device/all_sessions/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		pl_json = payload.json()

		# Check if registered
		if not pl_json["registered"]:
			return redirect(url_for('register.home'))

		# Get the sessions
		sess_list = pl_json["sessions"]
		settings = pl_json["settings"]

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

		return render_template("system_admin/data/graph_data_month.html", title="Month", form=form, pic_name=pic_name)
	
	return render_template("system_admin/data/graph_data_month.html", title="Month", form=form)

@system_admin_data.route("/system_admin/graph_data/day", methods=['GET', 'POST'])
@login_required
def graph_day():
	form = DayForm()
	if form.validate_on_submit():

		devi_id_number = Device_ID.query.first().id_number

		# Grab the sessions
		try:
			payload = requests.get(service_ip + '/device/all_sessions/' + devi_id_number)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))
		
		pl_json = payload.json()

		# Check if registered
		if not pl_json["registered"]:
			return redirect(url_for('register.home'))

		# Get the sessions
		sess_list = pl_json["sessions"]
		settings = pl_json["settings"]

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

		return render_template("system_admin/data/graph_data_day.html", title="Day", form=form, pic_name=pic_name)

	return render_template("system_admin/data/graph_data_day.html", title="Day", form=form)

@system_admin_data.route("/system_admin/local_data")
@login_required
def view_local_data():
	devi_id_number = Device_ID.query.first().id_number

	# Later combine the two requests to speed up
	try:
		payload = requests.get(service_ip + '/device/get_settings/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	pl_json = payload.json()

	# Check if registered
	if not pl_json["registered"]:
		return redirect(url_for('register.home'))

	settings = pl_json

	sessions = current_sessions.local_sessions.values()
	date_strings = get_offset_dates_initiated(sessions=sessions, time_offset=settings["time_offset"], from_local_sess=True)

	sessions_and_dates = zip(sessions, date_strings)
	return render_template("system_admin/data/local_data.html", title="Local Data", 
							current_sessions=current_sessions, sessions_and_dates=sessions_and_dates)