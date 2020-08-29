from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, IntegerField,
					 SelectField)
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from flask_login import current_user
from chargingbooth.models import User
import pytz


#Login
class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')

#Registration
class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')

#Update Account
class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one.')

#Request Reset
class RequestRestForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('There is no account with that email.')

# Reset Password
class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')


# Settings
class SettingsForm(FlaskForm):
	toggle_pay = BooleanField('Toggle Pay')
	cents_per_second = IntegerField('Price (cents/sec)', validators=[DataRequired()])
	charge_time = IntegerField('Allowed Charge Time (sec)', validators=[DataRequired()])
	time_zone = SelectField('Timezone', choices=pytz.all_timezones)
	submit = SubmitField('Update Settings')

# Slide Show Pictures
class SlideShowPicsForm(FlaskForm):
	picture = FileField('Upload Picture', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'png'])])
	submit = SubmitField('Upload Picture')

# Remove Picture Form
class RemovePictureForm(FlaskForm):
	removals = StringField('Image Files to be Removed.\
		(Use the image numbers separated by commas)', validators=[DataRequired()])
	submit = SubmitField('Remove Images')

	def validate_removals(self, removals):
		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ','])
		if not all(x in valid_characters for x in removals.data):
			raise ValidationError("Characters must only be numbers and commas. No white spaces")

