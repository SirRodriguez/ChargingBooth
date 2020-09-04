from flask import render_template, Blueprint, url_for, redirect
from chargingbooth.main.utils import start_route

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
	start_route()

	# return redirect(url_for('system_admin.home')) # Defualt
	return redirect(url_for('kiosk_mode.home'))