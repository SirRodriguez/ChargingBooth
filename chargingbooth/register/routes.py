from flask import Blueprint, render_template, redirect, url_for, json, flash
from chargingbooth import db, service_ip
from chargingbooth.models import Device_ID
from chargingbooth.register.forms import LoginForm
import requests

register = Blueprint('register', __name__)

# Main Register
@register.route("/register/home")
def home():
	return render_template("register/home.html", title="Register Device")

# Device is registered
@register.route("/register/register_device", methods=['GET', 'POST'])
def register_device():
	form = LoginForm()

	if form.validate_on_submit():
		json_send = {}
		json_send["username"] = form.username.data
		json_send["password"] = form.password.data

		# Register device here
		try:
			payload = requests.get(service_ip + '/device/register', json=json_send)		
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.register'))

		# Verify user
		if payload.status_code == 401:
			flash("Username or password not correct", 'danger')

		else:
			# Verified
			pl_json = payload.json()
			device_id = pl_json["device_id"]
			id = pl_json["id"]

			Device_ID.query.first().id_number = device_id
			db.session.commit()

			return render_template("register/registered.html", title="Registered", id=id)

	return render_template("register/verify.html", title="Verify", form=form)