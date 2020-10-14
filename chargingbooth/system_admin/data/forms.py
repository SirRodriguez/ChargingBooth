from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

# Graph Year form
class YearForm(FlaskForm):
	year = StringField('Year YYYY', validators=[DataRequired()])
	submit = SubmitField('Apply')

	def validate_year(self, year):
		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
		if not all(x in valid_characters for x in year.data):
			raise ValidationError("Numbers are only valid")
		elif len(year.data) != 4:
			raise ValidationError('Must be in the format YYYY')

# Graph month form
class MonthForm(FlaskForm):
	year = StringField('Year YYYY', validators=[DataRequired()])
	month = StringField('Month (ex Sep)', validators=[DataRequired()])
	submit = SubmitField('Apply')

	def validate_year(self, year):
		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
		if not all(x in valid_characters for x in year.data):
			raise ValidationError("Numbers are only valid")
		elif len(year.data) != 4:
			raise ValidationError('Must be in the format YYYY')

	def validate_month(self, month):
		valid_months = set(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

		valid = False
		for m in valid_months:
			if month.data == m:
				valid = True

		if not valid:
			raise ValidationError("Must be one of these: 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'")


# Graph day form
class DayForm(FlaskForm):
	year = StringField('Year YYYY', validators=[DataRequired()])
	month = StringField('Month (ex Sep)', validators=[DataRequired()])
	day = StringField('Day dd (ex 05)', validators=[DataRequired()])
	submit = SubmitField('Apply')

	def validate_year(self, year):
		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
		if not all(x in valid_characters for x in year.data):
			raise ValidationError("Numbers are only valid")
		elif len(year.data) != 4:
			raise ValidationError('Must be in the format YYYY')

	def validate_month(self, month):
		valid_months = set(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

		valid = False
		for m in valid_months:
			if month.data == m:
				valid = True

		if not valid:
			raise ValidationError("Must be one of these: 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'")

	def validate_day(self, day):
		valid_characters = set(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'])
		if not all(x in valid_characters for x in day.data):
			raise ValidationError("Numbers are only valid")

		if int(day.data) > 31:
			raise ValidationError("Number of days is too high!")