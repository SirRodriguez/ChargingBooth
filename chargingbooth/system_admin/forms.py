from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, IntegerField,
					 SelectField, MultipleFileField)
from wtforms.validators import (DataRequired, Length, EqualTo, ValidationError, Email, 
								InputRequired, NumberRange)
from flask_login import current_user
from chargingbooth.models import User
import pytz


aspect_ratio_list = ['1:1', '5:4', '3:2', '16:10', '16:9', '1.85:1', '2.35:1']

# #Login
# class LoginForm(FlaskForm):
# 	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
# 	password = PasswordField('Password', validators=[DataRequired()])
# 	submit = SubmitField('Login')

# #Registration
# class RegistrationForm(FlaskForm):
# 	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
# 	email = StringField('Email', validators=[DataRequired(), Email()])
# 	password = PasswordField('Password', validators=[DataRequired()])
# 	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
# 	submit = SubmitField('Sign Up')

# 	def validate_username(self, username):
# 		user = User.query.filter_by(username=username.data).first()
# 		if user:
# 			raise ValidationError('That username is taken. Please choose a different one.')

# 	def validate_email(self, email):
# 		user = User.query.filter_by(email=email.data).first()
# 		if user:
# 			raise ValidationError('That email is taken. Please choose a different one.')

# #Update Account
# class UpdateAccountForm(FlaskForm):
# 	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
# 	email = StringField('Email', validators=[DataRequired(), Email()])
# 	submit = SubmitField('Update')

# 	def validate_username(self, username):
# 		if username.data != current_user.username:
# 			user = User.query.filter_by(username=username.data).first()
# 			if user:
# 				raise ValidationError('That username is taken. Please choose a different one.')

# 	def validate_email(self, email):
# 		if email.data != current_user.email:
# 			user = User.query.filter_by(email=email.data).first()
# 			if user:
# 				raise ValidationError('That email is taken. Please choose a different one.')

# #Request Reset
# class RequestRestForm(FlaskForm):
# 	email = StringField('Email', validators=[DataRequired(), Email()])
# 	submit = SubmitField('Request Password Reset')

# 	def validate_email(self, email):
# 		user = User.query.filter_by(email=email.data).first()
# 		if user is None:
# 			raise ValidationError('There is no account with that email.')

# # Reset Password
# class ResetPasswordForm(FlaskForm):
# 	password = PasswordField('Password', validators=[DataRequired()])
# 	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
# 	submit = SubmitField('Reset Password')


# # Settings
# class SettingsForm(FlaskForm):
# 	toggle_pay = BooleanField('Toggle Pay')
# 	price = IntegerField('Price per session in cents (ex. $3.50 = 350c)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
# 	charge_time_min = IntegerField('Allowed Charge Time (minutes)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
# 	charge_time_sec = IntegerField('Allowed Charge Time (seconds)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
# 	time_zone = SelectField('Timezone', choices=pytz.all_timezones)
# 	location = StringField('Location', validators=[Length(max=100, message="Max character is 100")])
# 	aspect_ratio = SelectField('Aspect Ratio', choices=aspect_ratio_list)

# 	submit = SubmitField('Update Settings')

# Slide Show Pictures
class SlideShowPicsForm(FlaskForm):
	picture = MultipleFileField('Upload Pictures', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'png'])])
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

# # Graph Year form
# class YearForm(FlaskForm):
# 	year = StringField('Year YYYY', validators=[DataRequired()])
# 	submit = SubmitField('Apply')

# 	def validate_year(self, year):
# 		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
# 		if not all(x in valid_characters for x in year.data):
# 			raise ValidationError("Numbers are only valid")
# 		elif len(year.data) != 4:
# 			raise ValidationError('Must be in the format YYYY')


# # Graph month form
# class MonthForm(FlaskForm):
# 	year = StringField('Year YYYY', validators=[DataRequired()])
# 	month = StringField('Month (ex Sep)', validators=[DataRequired()])
# 	submit = SubmitField('Apply')

# 	def validate_year(self, year):
# 		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
# 		if not all(x in valid_characters for x in year.data):
# 			raise ValidationError("Numbers are only valid")
# 		elif len(year.data) != 4:
# 			raise ValidationError('Must be in the format YYYY')

# 	def validate_month(self, month):
# 		valid_months = set(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

# 		valid = False
# 		for m in valid_months:
# 			if month.data == m:
# 				valid = True

# 		if not valid:
# 			raise ValidationError("Must be one of these: 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'")


# # Graph day form
# class DayForm(FlaskForm):
# 	year = StringField('Year YYYY', validators=[DataRequired()])
# 	month = StringField('Month (ex Sep)', validators=[DataRequired()])
# 	day = StringField('Day dd (ex 05)', validators=[DataRequired()])
# 	submit = SubmitField('Apply')

# 	def validate_year(self, year):
# 		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
# 		if not all(x in valid_characters for x in year.data):
# 			raise ValidationError("Numbers are only valid")
# 		elif len(year.data) != 4:
# 			raise ValidationError('Must be in the format YYYY')

# 	def validate_month(self, month):
# 		valid_months = set(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

# 		valid = False
# 		for m in valid_months:
# 			if month.data == m:
# 				valid = True

# 		if not valid:
# 			raise ValidationError("Must be one of these: 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'")

# 	def validate_day(self, day):
# 		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
# 		if not all(x in valid_characters for x in day.data):
# 			raise ValidationError("Numbers are only valid")

# 		if int(day.data) > 31:
# 			raise ValidationError("Number of days is too high!")