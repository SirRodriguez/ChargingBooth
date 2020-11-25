from flask import url_for
from chargingbooth import mail
from flask_mail import Message

def send_reset_email(email, user, logged_in=False):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[email])
	if logged_in:
# 		msg.body = f'''To reset your password, visit the following link:

# {url_for('system_admin_account.change_token', token=token, _external=True)}

# If you did not make this request then simply ignore this email and no change will be made.
# '''
		msg.body = "To reset your password, visit the following link:\n\n" + url_for('system_admin_account.change_token', token=token, _external=True) + "\n\nIf you did not make this request then simply ignore this email and no change will be made."
	else:
# 		msg.body = f'''To reset your password, visit the following link:

# {url_for('system_admin_account.reset_token', token=token, _external=True)}

# If you did not make this request then simply ignore this email and no change will be made.
# '''
		msg.body = "To reset your password, visit the following link:\n\n" + url_for('system_admin_account.change_token', token=token, _external=True) + "\n\nIf you did not make this request then simply ignore this email and no change will be made."
	mail.send(msg)