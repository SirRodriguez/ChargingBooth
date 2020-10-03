from flask import Blueprint, url_for, redirect
from chargingbooth import service_ip,  db
from chargingbooth.main.utils import start_route
from chargingbooth.models import Device_ID
import requests

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
	start_route()

	devi_id = Device_ID.query.first()

	if devi_id == None:
		return redirect(url_for('register.home'))
	else:
		if devi_id.id_number == None:
			return redirect(url_for('register.home'))
		else:
			# Check here if id number is correct
			pass

	return redirect(url_for('kiosk_mode.home'))