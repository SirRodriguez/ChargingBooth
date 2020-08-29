from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, IntegerField,
					 SelectField)
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from flask_login import current_user
from chargingbooth.models import User

time_zone_array = [('+14', 		'LINT  - EX: Kiritimati'), # 1
					('+13', 	'TOT   - EX: Nukualofa'), # 2
					('+12:45', 	'CHAST - EX: Chatham Islands'), # 3
					('+12', 	'ANAT  - EX: Anadyr'), # 4
					('+11', 	'SBT   - EX: Honiara'), # 5
					('+10:30', 	'LHST  - EX: Lord Howe Island'), # 6
					('+10', 	'AEST  - EX: Melbourne'), # 7
					('+9:30', 	'ACST  - EX: Adelaide'), # 8
					('+9', 		'JST   - EX: Tokyo'), # 9
					('+8:45', 	'ACWST - EX: Eucla'), # 10
					('+8', 		'CST   - EX: Beijing'), # 11
					('+7', 		'WIB   - EX: Jakarta'), # 12
					('+6:30', 	'MMT   - EX: Yangon'), # 13
					('+6', 		'BST   - EX: Dhaka'), # 14
					('+5:45', 	'NPT   - EX: Kathmandu'), # 15
					('+5:30', 	'IST   - EX: New Delhi'), # 16
					('+5', 		'UZT   - EX: Tashkent'), # 17
					('+4:30', 	'IRDT  - EX: Tehran'), # 18
					('+4', 		'GST   - EX: Dubai'), # 19
					('+3', 		'MSK   - EX: Moscow'), # 20
					('+2', 		'CEST  - EX: Brussels'), # 21
					('+1', 		'BST   - EX: London'), # 22
					('+0', 		'GMT   - EX: Accra'), # 23
					('-1', 		'CVT   - EX: Praia'), # 24
					('-2', 		'WGST  - EX: Nuuk'), # 25
					('-2:30', 	'NDT   - EX: St. John\'s'), # 26
					('-3', 		'ART   - EX: Buenos Aires'), # 27
					('-4', 		'EDT   - EX: New York'), # 28
					('-5', 		'CDT   - EX: Mexico City'), # 29
					('-6', 		'CST   - EX: Guatemala City'), # 30
					('-7', 		'PDT   - EX: Los Angeles'), # 31
					('-8', 		'AKDT  - EX: Anchorage'), # 32
					('-9', 		'HDT   - EX: Adak'), # 33
					('-9:30', 	'MART  - EX: Taiohae'), # 34
					('-10', 	'HST   - EX: Honolulu'), # 35
					('-11', 	'NUT   - EX: Alofi'), # 36
					('-12', 	'AoE   - EX: Baker Island')] # 37

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
	time_zone = SelectField('Timezone', choices=time_zone_array)
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

