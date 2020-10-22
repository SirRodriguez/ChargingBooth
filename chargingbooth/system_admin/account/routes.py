from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user, current_user
from chargingbooth import bcrypt, db, service_ip
from chargingbooth.models import User
from chargingbooth.utils import is_registered
from chargingbooth.system_admin.account.utils import send_reset_email
from chargingbooth.system_admin.account.forms import (LoginForm, RegistrationForm, UpdateAccountForm, 
														RequestRestForm, ResetPasswordForm)
import requests

system_admin_account = Blueprint('system_admin_account', __name__)


@system_admin_account.route("/system_admin/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('system_admin_main.main'))
	form = LoginForm()
	if form.validate_on_submit():
		try:
			payload = requests.get(service_ip + '/device/admin_user/verify_user/' + form.username.data + '/' + form.password.data)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.register'))

		user = User.query.first()
		if payload.json()["user_verified"]:
			login_user(user)
			next_page = request.args.get('next')
			return redirect(url_for('system_admin_main.main'))
		else:
			flash('Loging Unsuccessful. Please check username and password', 'danger')
	return render_template('system_admin/account/login.html', title='System Admin Login', form=form)

@system_admin_account.route("/system_admin/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('system_admin_main.home'))

# This is needed to be removed after production
# This is only used to adjust the database for an admin user
@system_admin_account.route("/system_admin/register", methods=['GET', 'POST'])
def register():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	if current_user.is_authenticated:
		return redirect(url_for('system_admin_main.main'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('system_admin_account.login'))
	return render_template('system_admin/account/register.html', title='Register', form=form)


@system_admin_account.route("/system_admin/account", methods=['GET', 'POST'])
@login_required
def account():
	# Get account info from service
	try:
		payload = requests.get(service_ip + '/device/admin_user/account_info')
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))

	form = UpdateAccountForm()
	if form.validate_on_submit():

		payload = {}

		# pack the updated account info
		payload["username"] = form.username.data
		payload["email"] = form.email.data

		# Send the updated account
		try:
			response = requests.put(service_ip + '/device/admin_user/update_account/', json=payload)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.register'))

		# Check response
		if response.status_code == 204 or response.status_code == 200:
			flash('Account has been updated!', 'success')
		else:
			flash('Something happened and settings were not updated.', 'danger')

		return redirect(url_for('system_admin_account.account'))

	elif request.method == 'GET':
		form.username.data = payload.json()["username"]
		form.email.data = payload.json()["email"]
	return render_template('system_admin/account/account.html', title='Account', form=form, payload=payload)


# When logged out and forgot password
@system_admin_account.route("/system_admin/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('system_admin_main.home'))

	# Get account info from service
	try:
		payload = requests.get(service_ip + '/device/admin_user/account_info')
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))

	user = User.query.first()
	send_reset_email(email=payload.json()["email"], user=user, logged_in=False)	

	flash('An email has been sent with instructions to reset your password.', 'info')

	return redirect(url_for('system_admin_account.login'))

@system_admin_account.route("/system_admin/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('system_admin_main.home'))

	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('system_admin_account.login'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		payload = {}
		payload["hashed_password"] = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

		try:
			response = requests.put(service_ip + '/device/admin_user/update_password/', json=payload)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.register'))

		flash('Your password has been updated! You are now able to log in.', 'success')
		return redirect(url_for('system_admin_account.login'))
	return render_template('system_admin/account/reset_token.html', title='Reset Password', form=form)



#When logged in and changing password
@system_admin_account.route("/system_admin/change_password", methods=['GET', 'POST'])
@login_required
def change_request():
	# Get account info from service
	try:
		payload = requests.get(service_ip + '/device/admin_user/account_info')
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))

	user = User.query.first()
	send_reset_email(email=payload.json()["email"], user=user, logged_in=True)	

	flash('An email has been sent with instructions to reset your password.', 'info')
	return redirect(url_for('system_admin_account.account'))

@system_admin_account.route("/system_admin/change_password/<token>", methods=['GET', 'POST'])
@login_required 
def change_token(token):
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('system_admin_account.login'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		payload = {}
		payload["hashed_password"] = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

		try:
			response = requests.put(service_ip + '/device/admin_user/update_password/', json=payload)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.register'))

		flash('Your password has been updated!', 'success')
		return redirect(url_for('system_admin_account.login'))
	return render_template('system_admin/account/reset_token.html', title='Reset Password', form=form)