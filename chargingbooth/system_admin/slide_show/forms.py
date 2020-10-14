from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import MultipleFileField, SubmitField, StringField
from wtforms.validators import ValidationError, DataRequired

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