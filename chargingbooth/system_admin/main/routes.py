from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_required
from chargingbooth.utils import is_registered

system_admin_main = Blueprint('system_admin_main', __name__)

@system_admin_main.route("/system_admin")
def home():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	return redirect(url_for('system_admin_account.login'))

@system_admin_main.route("/system_admin/main")
@login_required
def main():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	return render_template('system_admin/main/main.html', title='System Admin Main')