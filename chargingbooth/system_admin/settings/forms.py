from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired, NumberRange, Length
import pytz

aspect_ratio_list = ['1:1', '5:4', '3:2', '16:10', '16:9', '1.85:1', '2.35:1']

# Settings
class SettingsForm(FlaskForm):
	toggle_pay = BooleanField('Toggle Pay')
	price = IntegerField('Price per session in cents (ex. $3.50 = 350c)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
	charge_time_min = IntegerField('Allowed Charge Time (minutes)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
	charge_time_sec = IntegerField('Allowed Charge Time (seconds)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
	time_zone = SelectField('Timezone', choices=pytz.all_timezones)
	location = StringField('Location', validators=[Length(max=100, message="Max character is 100")])
	aspect_ratio = SelectField('Aspect Ratio', choices=aspect_ratio_list)

	submit = SubmitField('Update Settings')