from flask import render_template, Blueprint, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from chargingbooth import db, bcrypt, current_sessions
from chargingbooth.models import User, Session, Settings, PFI
from chargingbooth.system_admin.forms import (LoginForm, RegistrationForm, UpdateAccountForm,
												RequestRestForm, RequestRestForm, ResetPasswordForm, 
												SettingsForm, SlideShowPicsForm, RemovePictureForm)
from chargingbooth.system_admin.utils import send_reset_email


system_admin = Blueprint('system_admin', __name__)

@system_admin.route("/system_admin")
def home():
	return redirect(url_for('system_admin.login'))

@system_admin.route("/system_admin/login", methods=['GET', 'POST'])
def login():
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
	return render_template('system_admin_login.html', title='System Admin Login', form=form)

@system_admin.route("/system_admin/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('system_admin.home'))


@system_admin.route("/system_admin/main")
@login_required
def main():
	return render_template('system_admin_main.html', title='System Admin Main')

@system_admin.route("/system_admin/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('system_admin.main'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('system_admin.login'))
	return render_template('system_admin_register.html', title='Register', form=form)


@system_admin.route("/system_admin/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('system_admin.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('system_admin_account.html', title='Account', form=form)


# When logged out and forgot password
@system_admin.route("/system_admin/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('system_admin.home'))
	form = RequestRestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user, logged_in=False)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('system_admin.login'))
	return render_template('system_admin_reset_request.html', title='Reset Password', form=form)

@system_admin.route("/system_admin/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('system_admin.home'))

	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('system_admin.reset_request'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! Ypu are now able to log in.', 'success')
		return redirect(url_for('system_admin.login'))
	return render_template('system_admin_reset_token.html', title='Reset Password', form=form)



#When logged in and changing password
@system_admin.route("/system_admin/change_password", methods=['GET', 'POST'])
@login_required
def change_request():
	user = User.query.filter_by(email=current_user.email).first()
	send_reset_email(user, logged_in=True)
	flash('An email has been sent with instructions to reset your password.', 'info')
	return redirect(url_for('system_admin.account'))

@system_admin.route("/system_admin/change_password/<token>", methods=['GET', 'POST'])
@login_required 
def change_token(token):
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('system_admin.reset_request'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated!', 'success')
		return redirect(url_for('system_admin.login'))
	return render_template('system_admin_reset_token.html', title='Reset Password', form=form)


@system_admin.route("/system_admin/settings", methods=['GET', 'POST'])
@login_required
def settings():
	form = SettingsForm()
	if form.validate_on_submit():
		Settings.query.first().toggle_pay = form.toggle_pay.data
		Settings.query.first().cents_per_second = form.cents_per_second.data
		Settings.query.first().charge_time = form.charge_time.data
		db.session.commit()
		flash('Settings have been updated!', 'success')
		return redirect(url_for('system_admin.settings'))
	elif request.method == 'GET':
		form.toggle_pay.data = Settings.query.first().toggle_pay
		form.cents_per_second.data = Settings.query.first().cents_per_second
		form.charge_time.data = Settings.query.first().charge_time

	return render_template('system_admin_settings.html', title='Settings', form=form)

@system_admin.route("/system_admin/data")
@login_required
def view_data():
	page = request.args.get('page', 1, type=int)
	sessions = Session.query.order_by(Session.date_initiated.desc()).paginate(page=page, per_page=10)
	return render_template("system_admin_data.html", title="Data", sessions=sessions)

@system_admin.route("/system_admin/local_data")
@login_required
def view_local_data():
	return render_template("system_admin_local_data.html", title="Local Data", 
							current_sessions=current_sessions)

@system_admin.route("/system_admin/slide_show_pics", methods=['GET', 'POST'])
@login_required
def slide_show_pics():

	remove_pic_form = RemovePictureForm()
	if remove_pic_form.validate_on_submit() and remove_pic_form.removals.data != "":
		flash('Picture Files have been removed', 'success')

	return render_template("system_admin_slide_show_pics.html", title="Slide Show Pictures")

@system_admin.route("/system_admin/add_slides", methods=['GET', 'POST'])
@login_required
def upload_image():
	pic_files = PFI()

	form = SlideShowPicsForm()
	if form.validate_on_submit():
		pic_files.save_file(form.picture.data)
		flash('Picture has been uploaded', 'success')
		return redirect(url_for('system_admin.upload_image'))

	return render_template("system_admin_upload_image.html", title="Upload Image", form=form,
							pic_files=pic_files.get_copy())

@system_admin.route("/system_admin/remove_slides", methods=['GET', 'POST'])
@login_required
def remove_image():
	pic_files = PFI()
	pic_files_length = pic_files.get_length()

	form = RemovePictureForm()
	if form.validate_on_submit():
		pic_files.remove_images(form.removals.data)
		flash("Images have been deleted!", 'success')
		return redirect(url_for('system_admin.remove_image'))

	return render_template("system_admin_remove_image.html", title="Remove Images", form=form,
							pic_files=pic_files.get_copy(), pic_files_length=pic_files_length)