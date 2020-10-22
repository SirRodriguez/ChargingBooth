from flask import Blueprint, redirect, url_for, render_template, flash
from flask_login import login_required
from chargingbooth import service_ip
from chargingbooth.utils import is_registered
from chargingbooth.models import Device_ID
from chargingbooth.system_admin.slide_show.forms import SlideShowPicsForm, RemovePictureForm
import secrets
import requests

system_admin_slide_show = Blueprint('system_admin_slide_show', __name__)


@system_admin_slide_show.route("/system_admin/slide_show_pics", methods=['GET', 'POST'])
@login_required
def slide_show_pics():
	return render_template("system_admin/slide_show/slide_show_pics.html", title="Slide Show Pictures")

@system_admin_slide_show.route("/system_admin/add_slides", methods=['GET', 'POST'])
@login_required
def upload_image():
	devi_id_number = Device_ID.query.first().id_number

	# Validate must be done first to allow the change of images before grabbing them again
	form = SlideShowPicsForm()
	if form.validate_on_submit():

		image_files = []
		for file in form.picture.data:
			image_files.append(('image', ( file.filename, file.read() )  ))

		# Do the post here
		response = requests.post(service_ip + '/device/images/upload/' + devi_id_number, files=image_files)

		flash('Pictures has been uploaded', 'success')
		return redirect(url_for('system_admin_slide_show.upload_image'))
	
	# Grab the number of images the service has
	try:
		payload = requests.get(service_ip + '/device/img_count/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))

	pl_json = payload.json()

	# Check if registered
	if not pl_json["registered"]:
		return redirect(url_for('register.home')) 

	img_count = pl_json["image_count"]

	random_hex = secrets.token_hex(8)

	return render_template("system_admin/slide_show/upload_image.html", 
							title="Upload Image", 
							form=form,
							service_ip=service_ip,
							devi_id_number=devi_id_number,
							img_count=img_count,
							random_hex=random_hex)

@system_admin_slide_show.route("/system_admin/remove_slides", methods=['GET', 'POST'])
@login_required
def remove_image():
	devi_id_number = Device_ID.query.first().id_number

	form = RemovePictureForm()
	if form.validate_on_submit():
		try:
			response = requests.delete(service_ip + '/device/remove_images/' + devi_id_number + '/' + form.removals.data)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('main.error'))

		if response.status_code == 204:
			flash('Images have been successfuly removed!', 'success')
		elif response.status_code == 400:
			flash('Image was not found in the server!', 'danger')
		else:
			flash("Oops! Something happened and the images were not deleted.", "danger")


	# Grab the number of images the service has
	try:
		payload = requests.get(service_ip + '/device/img_count/' + devi_id_number)
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.register'))

	pl_json = payload.json()

	# Check if registered
	if not pl_json["registered"]:
		return redirect(url_for('register.home')) 

	img_count = pl_json["image_count"]

	random_hex = secrets.token_hex(8)


	return render_template("system_admin/slide_show/remove_image.html", 
							title="Remove Images", 
							form=form,
							service_ip=service_ip,
							devi_id_number=devi_id_number,
							img_count=img_count,
							random_hex=random_hex)