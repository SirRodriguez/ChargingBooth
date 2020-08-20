from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from chargingbooth.models import Session

class DataForm(FlaskForm):
	duration = IntegerField('Seconds (Integer)', validators=[DataRequired()])
	power_used = FloatField('Watts (Decimal)', validators=[DataRequired()])
	amount_paid = IntegerField('Cents (Integer)', validators=[DataRequired()])
	# Date
	location = StringField('Location', validators=[DataRequired()])
	port = StringField('Port', validators=[DataRequired()])
	increment_size = IntegerField('Increment Size (Seconds)', validators=[DataRequired()])
	increments = IntegerField('Amount of Increments (Integer)', validators=[DataRequired()])
	submit = SubmitField('Submit Session')

class RandomDataForm(FlaskForm):
	min_duration = IntegerField('Min Duration (Seconds)', validators=[DataRequired()])
	max_duration = IntegerField('Max Duration (Seconds)', validators=[DataRequired()])

	min_power_used = FloatField('Min Watts (Decimal)', validators=[DataRequired()])
	max_power_used = FloatField('Max Watts (Decimal)', validators=[DataRequired()])

	min_amount_paid = IntegerField('Min Cents (Integer)', validators=[DataRequired()])
	max_amount_paid = IntegerField('Max Cents (Integer)', validators=[DataRequired()])

	location = StringField('Location (Optional, Sets all session to this location)')

	min_port = IntegerField('Min Port (Integer)', validators=[DataRequired()])
	max_port = IntegerField('Max Port (Integer)', validators=[DataRequired()])

	min_increment_size = IntegerField('Min Increment Size (Integer)', validators=[DataRequired()])
	max_increment_size = IntegerField('Max Increment Size (Integer)', validators=[DataRequired()])
	
	num_sessions = IntegerField('Number of Sessions (Integer)', validators=[DataRequired()])

	submit = SubmitField('Submit Sessions')


	def validate_min_duration(self, min_duration):
		if min_duration.data <= 0:
			raise ValidationError('Min Duration must not be negative')

	def validate_min_power_used(self, min_power_used):
		if min_power_used.data < 0:
			raise ValidationError('Min Power Used must not be negative')

	def validate_min_amount_paid(self, min_amount_paid):
		if min_amount_paid.data < 0:
			raise ValidationError('Min Amount Paid must not be negative')

	def validate_min_increment_size(self, min_increment_size):
		if min_increment_size.data <= 0:
			raise ValidationError('Min Increment Size must be positive')

	def validate_num_sessions(self, num_sessions):
		if num_sessions.data < 1:
			raise ValidationError('Number of Sessions must be a possitive number.')


class SessionForm(FlaskForm):
	num_of_sessions = IntegerField('Number of sessions', validators=[DataRequired()])
	submit = SubmitField('Pay')

	def validate_num_sessions(self, num_of_sessions):
		if num_of_sessions.data < 1:
			raise ValidationError('Must be greater than 0.')