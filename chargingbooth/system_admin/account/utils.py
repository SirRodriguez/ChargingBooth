from flask import url_for
from chargingbooth import service_ip, mail
from chargingbooth.models import Device_ID
from flask_mail import Message
import requests

def is_registered():
	devi_id = Device_ID.query.first()

	if devi_id == None:
		return False
	else:
		if devi_id.id_number == None:
			return False
		else:
			# Check here if id number is correct
			payload = requests.get(service_ip + '/device/is_registered/' + devi_id.id_number)		

			return payload.json()["registered"]


def send_reset_email(user, logged_in=False):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
	if logged_in:
		msg.body = f'''To reset your password, visit the following link:

{url_for('system_admin_account.change_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
'''
	else:
		msg.body = f'''To reset your password, visit the following link:

{url_for('system_admin_account.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
'''
	mail.send(msg)