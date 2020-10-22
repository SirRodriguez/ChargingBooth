from flask import Blueprint, render_template, redirect, url_for
from chargingbooth.utils import is_registered

error = Blueprint('error', __name__)

# Error
@error.route("/register/error")
def register():
	# Try again to see if it will connect
	try:
		if is_registered():
			return redirect(url_for('main.home'))
		else:
			return redirect(url_for('register.home'))
	except:
		return render_template("error/register.html")