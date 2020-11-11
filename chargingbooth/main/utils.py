from chargingbooth import service_ip,  db
from flask_login import current_user, logout_user
from chargingbooth.models import Device_ID
import requests

def start_route():
	if current_user.is_authenticated:
		logout_user()


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

			if payload.json()["registered"]:
				return True
			else:
				return False