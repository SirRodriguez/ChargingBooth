from flask import Blueprint, render_template, redirect, url_for, json, flash
from chargingbooth import db, service_ip
from chargingbooth.models import Device_ID
import requests

register = Blueprint('register', __name__)

# Main Register
@register.route("/register/home")
def home():
	return render_template("register/home.html", title="Register Device")

# Device is registered
@register.route("/register/register_device")
def register_device():
	# Register device here
	try:
		payload = requests.get(service_ip + '/device/register')		
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))
	
	pl_json = payload.json()
	device_id = pl_json["device_id"]
	id = pl_json["id"]

	Device_ID.query.first().id_number = device_id
	db.session.commit()

	return render_template("register/registered.html", title="Registered", id=id)