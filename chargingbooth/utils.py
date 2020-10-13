from chargingbooth import service_ip
from chargingbooth.models import Device_ID
import requests

def is_registered():
	devi_id = Device_ID.query.first()

	if devi_id == None:
		# return redirect(url_for('register.home'))
		return False
	else:
		if devi_id.id_number == None:
			# return redirect(url_for('register.home'))
			return False
		else:
			# Check here if id number is correct
			payload = requests.get(service_ip + '/device/is_registered/' + devi_id.id_number)		

			if payload.json()["registered"]:
				# return redirect(url_for('kiosk_mode.home'))
				return True
			else:
				# return redirect(url_for('register.home'))
				return False