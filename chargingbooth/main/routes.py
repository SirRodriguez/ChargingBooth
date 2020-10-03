from flask import Blueprint, url_for, redirect
# from chargingbooth import service_ip,  db
from chargingbooth.main.utils import start_route, is_registered
# from chargingbooth.models import Device_ID
# import requests

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
	start_route()


	try:
		if is_registered():
			return redirect(url_for('kiosk_mode.home'))
		else:
			return redirect(url_for('register.home'))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	# devi_id = Device_ID.query.first()

	# if devi_id == None:
	# 	return redirect(url_for('register.home'))
	# else:
	# 	if devi_id.id_number == None:
	# 		return redirect(url_for('register.home'))
	# 	else:
	# 		# Check here if id number is correct
	# 		try:
	# 			payload = requests.get(service_ip + '/device/is_registered/' + devi_id.id_number)		
	# 		except:
	# 			flash("Unable to Connect to Server!", "danger")
	# 			return redirect(url_for('register.error'))

	# 		if payload.json()["registered"]:
	# 			return redirect(url_for('kiosk_mode.home'))
	# 		else:
	# 			return redirect(url_for('register.home'))

	return redirect(url_for('register.home'))