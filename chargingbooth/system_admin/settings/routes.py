from flask import Blueprint, flash, redirect, url_for, request, render_template
from flask_login import login_required
from chargingbooth import service_ip
from chargingbooth.utils import is_registered
from chargingbooth.models import Device_ID
from chargingbooth.system_admin.settings.forms import SettingsForm
from chargingbooth.system_admin.settings.utils import get_min_sec
import requests


system_admin_settings = Blueprint('system_admin_settings', __name__)

@system_admin_settings.route("/system_admin/settings", methods=['GET', 'POST'])
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

	setting = payload.json()

	form = SettingsForm()
	if form.validate_on_submit():
		pl_send = {}

		pl_send["toggle_pay"] = form.toggle_pay.data
		pl_send["price"] = form.price.data
		minutes = form.charge_time_min.data
		seconds = form.charge_time_sec.data
		pl_send["charge_time"] = minutes*60 + seconds;
		pl_send["time_offset"] = form.time_zone.data
		pl_send["location"] = form.location.data
		pl_send["aspect_ratio_width"] = float(form.aspect_ratio.data.split(":")[0])
		pl_send["aspect_ratio_height"] = float(form.aspect_ratio.data.split(":")[1])

		response = requests.put(service_ip + '/device/update_setting/' + devi_id_number, json=pl_send)

		if response.status_code == 204 or response.status_code == 200:
			flash('Settings have been updated!', 'success')
		elif response.status_code == 400:
			flash('Server could not find device!', 'danger')
		else:
			flash('Something happened and settings were not updated.', 'danger')

		return redirect(url_for('system_admin_settings.settings'))
	elif request.method == 'GET':
		form.toggle_pay.data = setting["toggle_pay"]
		form.price.data = setting["price"]
		minutes, seconds = get_min_sec(seconds=setting["charge_time"])
		form.charge_time_min.data = minutes
		form.charge_time_sec.data = seconds
		form.time_zone.data = setting["time_offset"]
		form.location.data = setting["location"]
		form.aspect_ratio.data = str( int(setting["aspect_ratio_width"]) if (setting["aspect_ratio_width"]).is_integer() else setting["aspect_ratio_width"] ) \
									+ ":" + str( int(setting["aspect_ratio_height"]) if (setting["aspect_ratio_height"]).is_integer() else setting["aspect_ratio_height"] ) 

	return render_template('system_admin/settings/settings.html', title='Settings', form=form)