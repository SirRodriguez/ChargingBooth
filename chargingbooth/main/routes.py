from flask import Blueprint, url_for, redirect, flash, request, abort
from chargingbooth.main.utils import start_route, is_registered

main = Blueprint('main', __name__)

# This is the function that will be called so that no other device
# On the network can access the routes
@main.before_app_request
def ip_check():
	# Check if it is not localhost
	if request.remote_addr != "127.0.0.1":
		abort(403)

@main.route("/")
@main.route("/home")
def home():
	start_route()

	try:
		if is_registered():
			return redirect(url_for('system_admin_account.login'))
		else:
			return redirect(url_for('register.home'))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))

	return redirect(url_for('register.home'))