from flask import Blueprint, url_for, redirect, flash
from chargingbooth.main.utils import start_route, is_registered

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
	start_route()

	try:
		if is_registered():
			return redirect(url_for('kiosk_mode.home'))
		else:
			return redirect(url_for('register.home'))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	return redirect(url_for('register.home'))