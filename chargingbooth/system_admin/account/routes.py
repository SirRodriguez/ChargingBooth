from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user, current_user
from chargingbooth import bcrypt, db
from chargingbooth.models import User
from chargingbooth.system_admin.account.utils import is_registered, send_reset_email
from chargingbooth.system_admin.account.forms import (LoginForm, RegistrationForm, UpdateAccountForm, 
														RequestRestForm, ResetPasswordForm)

system_admin_account = Blueprint('system_admin_account', __name__)


@system_admin_account.route("/system_admin/login", methods=['GET', 'POST'])
def login():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	if current_user.is_authenticated:
		return redirect(url_for('system_admin.main'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next')
			return redirect(url_for('system_admin.main'))
		else:
			flash('Loging Unsuccessful. Please check username and password', 'danger')
	return render_template('system_admin/account/login.html', title='System Admin Login', form=form)

@system_admin_account.route("/system_admin/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('system_admin.home'))

# This is needed to be removed after production
# This is only used to adjust the database for an admin user
@system_admin_account.route("/system_admin/register", methods=['GET', 'POST'])
def register():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	if current_user.is_authenticated:
		return redirect(url_for('system_admin.main'))
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
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('system_admin_account.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('system_admin/account/account.html', title='Account', form=form)


# When logged out and forgot password
@system_admin_account.route("/system_admin/reset_password", methods=['GET', 'POST'])
def reset_request():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))

	if current_user.is_authenticated:
		return redirect(url_for('system_admin.home'))
	form = RequestRestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user, logged_in=False)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('system_admin_account.login'))
	return render_template('system_admin/account/reset_request.html', title='Reset Password', form=form)

@system_admin_account.route("/system_admin/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('system_admin.home'))

	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('system_admin_account.reset_request'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! You are now able to log in.', 'success')
		return redirect(url_for('system_admin_account.login'))
	return render_template('system_admin/account/reset_token.html', title='Reset Password', form=form)



#When logged in and changing password
@system_admin_account.route("/system_admin/change_password", methods=['GET', 'POST'])
@login_required
def change_request():
	# Check if registered
	if not is_registered():
		return redirect(url_for('register.home'))
		
	user = User.query.filter_by(email=current_user.email).first()
	send_reset_email(user, logged_in=True)
	flash('An email has been sent with instructions to reset your password.', 'info')
	return redirect(url_for('system_admin_account.account'))

@system_admin_account.route("/system_admin/change_password/<token>", methods=['GET', 'POST'])
@login_required 
def change_token(token):
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('system_admin_account.reset_request'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated!', 'success')
		return redirect(url_for('system_admin_account.login'))
	return render_template('system_admin/account/reset_token.html', title='Reset Password', form=form)