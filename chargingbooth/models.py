import os
import threading
import time
from datetime import datetime, timedelta
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from chargingbooth import db, login_manager, service_ip
from flask_login import UserMixin
from typing import List
from os import listdir
from os.path import isfile, join
from PIL import Image
import requests



##################
#### Database ####
##################

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}')"

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)


class Session(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	duration = db.Column(db.Integer) #Seconds
	power_used = db.Column(db.Float) #Watts per second
	amount_paid = db.Column(db.Integer) #Cents
	date_initiated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	location = db.Column(db.String(100), default="No Location")
	port = db.Column(db.String(100), default="No Port")
	increment_size = db.Column(db.Integer) #Seconds
	increments = db.Column(db.Integer)


class Settings(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	toggle_pay = db.Column(db.Boolean)
	price = db.Column(db.Integer) #Cents per Session
	charge_time = db.Column(db.Integer) #Seconds
	time_offset = db.Column(db.String(20)) # timezone offset
	location = db.Column(db.String(100)) # Location of the device
	aspect_ratio_width = db.Column(db.Float) # Screen Ratio Width
	aspect_ratio_height = db.Column(db.Float) # Screen Ratio Height

class Device_ID(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	id_number = db.Column(db.String(50), unique=True)

###############
#### Local ####
###############


class Local_Session:
	def __init__(self, amount_paid, location, port, increment_size, increments, index):
		self.date_initiated = datetime.utcnow()
		self.amount_paid = amount_paid
		self.location = location
		self.port = port
		self.increment_size = increment_size
		self.increments = increments

		# When it needs to refer to itelf in the dictionary
		self.index = index

	# Will be changed later to check the amount of power used
	def power_used(self):
		power_constant = 1
		return self.total_seconds() * power_constant

	def zero_time(self):
		return "0:00:00"

	def total_seconds(self):
		return self.increment_size * self.increments

	def elapsed_time(self):
		return datetime.utcnow() - self.date_initiated

	def get_time_remaining(self):
		time_remain = timedelta(seconds=self.total_seconds()) - self.elapsed_time()

		if time_remain < timedelta(seconds=0):
			return self.zero_time()
		else:
			return str(time_remain).split(".")[0]

	def get_end_time(self):
		return timedelta( seconds=( self.total_seconds() ), ) + self.date_initiated

	def get_final_time(self):
		end_time = timedelta( seconds=( self.total_seconds() ), ) + self.date_initiated

		with_date = str( end_time ).split(".")[0]

		time_only = with_date.split(" ")[1]

		# Fix to 12 hour clock
		if(int(time_only.split(":")[0]) > 12 ): # if hour is greater than 12
			new_hour = str(int(time_only.split(":")[0]) - 12)

			time_only = new_hour + ":" + time_only.split(":", 1)[1]
			time_only += " PM"

		elif(int(time_only.split(":")[0]) == 12 ): # if it is 12 pm
			time_only += " PM"

		elif(int(time_only.split(":")[0]) == 0): # make 0 hour 12 am
			new_hour = "12"

			time_only = new_hour + ":" + time_only.split(":", 1)[1]
			time_only += " AM"

		else: # only add AM
			time_only += " AM"

		return time_only



class Sessions_Container:
	def __init__(self):
		self.local_sessions = dict()
		self.index = 0
		self.thread_pool = list()

	def init_app(self, application):
		self.app = application

		# Check here if there are any session files exist to continue working on them
		# Reason is because the application is needed for the app directory
		dir_path = os.path.join(self.app.root_path, 'static', 'session_files')
		files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

		if files:
			for file_name in files:
				# Place Holder file is there in order to push the session folder to git
				if file_name != "place_holder.txt":
					file_path = os.path.join(dir_path, file_name)
					with open(file_path, 'r') as file:
						session_info = file.readlines()


					# Incomplete session info
					# File line comes in as (all one line):
					# Start:<datetime>, Duration:60, End:<date time>, Amount Paid:<number>, 
					# Location:<location name>, Port:<port name>, Increment Size:<number>, 
					# Increments:<number>

					duration = int(session_info[0].split(", ")[1].split(":")[1])

					# File line comes in as:
					# Seconds elapsed: <number>
					# Where number is a float and is converted to an int by rounding down
					time_elapsed = int(float(session_info[1].split(": ")[1]))

					time_remaining = duration - time_elapsed

					amount_paid 	= int(session_info[0].split(", ")[3].split(":")[1])
					location 		= session_info[0].split(",")[4].split(":")[1]
					port 			= session_info[0].split(",")[5].split(":")[1]
					# increment_size 	= int(session_info[0].split(",")[6].split(":")[1])
					# increments 		= int(session_info[0].split(",")[7].split(":")[1])

					# Remove the old file so add_session creates a new one
					os.remove(file_path)

					# Add the session back in the container but this time the increment size will 
					# be the remaining duration and the increments will defualt to 1
					self.add_session(amount_paid=amount_paid, location=location, port=port,
										increment_size=time_remaining, increments=1)


	def add_session(self, amount_paid, location, port, increment_size, increments):
		# define an index for the dictionary
		if len(self.local_sessions.keys()) != 0:
			self.index = self.index + 1
		else:
			self.index = 0

		# Create the session
		self.local_sessions[self.index] = Local_Session(amount_paid, location, port, increment_size, increments, self.index)

		# Create the file for the session checkpoints
		file_name = 'session' + str(self.index) + '.txt'
		file_path = os.path.join(self.app.root_path, 'static', 'session_files', file_name)
		file = open(file_path, 'w')
		session_info = "Start:" + str(self.local_sessions[self.index].date_initiated) + \
						", Duration:" + str(self.local_sessions[self.index].total_seconds()) + \
						", End:" + str(self.local_sessions[self.index].get_end_time()) + \
						", Amount Paid:" + str(self.local_sessions[self.index].amount_paid) + \
						", Location:" + self.local_sessions[self.index].location + \
						", Port:" + self.local_sessions[self.index].port + \
						", Increment Size:" + str(self.local_sessions[self.index].increment_size) + \
						", Increments:" + str(self.local_sessions[self.index].increments) + '\n'
		file.write(session_info)
		file.write("Seconds elapsed: 0") # Place holder for second line
		file.close() # Close right away so that the handeler can open and use it for itself.

		# Create a thread to handle the session and terminate when needed
		sess = threading.Thread(target=self.handler, args=[self.index])
		sess.start()
		self.thread_pool.append(sess)


	# Handler for the sessions
	def handler(self, index):
		# Open the corresponding session file
		file_name = 'session' + str(index) + '.txt'
		file_path = os.path.join(self.app.root_path, 'static', 'session_files', file_name)

		running = True
		while(running):
			# Time has run out!
			if(self.local_sessions[index].get_time_remaining() == self.local_sessions[index].zero_time()):
				# Waits an extra second to catch up
				time.sleep(1)

				with self.app.app_context():
					devi_id_number = Device_ID.query.first().id_number

					# Send to the service here too
					payload_send = {}

					payload_send["duration"] = int(self.local_sessions[index].elapsed_time().total_seconds())
					payload_send["power_used"] = self.local_sessions[index].power_used()
					payload_send["amount_paid"] = self.local_sessions[index].amount_paid
					# Datetime was not json serializable
					payload_send["date_initiated_year"] = self.local_sessions[index].date_initiated.year
					payload_send["date_initiated_month"] = self.local_sessions[index].date_initiated.month
					payload_send["date_initiated_day"] = self.local_sessions[index].date_initiated.day
					payload_send["date_initiated_hour"] = self.local_sessions[index].date_initiated.hour
					payload_send["date_initiated_minute"] = self.local_sessions[index].date_initiated.minute
					payload_send["date_initiated_second"] = self.local_sessions[index].date_initiated.second
					payload_send["location"] = self.local_sessions[index].location
					payload_send["port"] = self.local_sessions[index].port if self.local_sessions[index].port != "" else "No Port Assigned"
					payload_send["increment_size"] = self.local_sessions[index].increment_size
					payload_send["increments"] = self.local_sessions[index].increments

					session = Session(duration=int(self.local_sessions[index].elapsed_time().total_seconds()), 
									power_used=self.local_sessions[index].power_used(), 
									amount_paid=self.local_sessions[index].amount_paid,
									date_initiated=self.local_sessions[index].date_initiated,
									location=self.local_sessions[index].location, 
									port=self.local_sessions[index].port if self.local_sessions[index].port != "" else "No Port Assigned",
									increment_size=self.local_sessions[index].increment_size, 
									increments=self.local_sessions[index].increments)

					response = requests.put(service_ip + '/device/add_session/' + devi_id_number, json=payload_send)

					# if response.status_code == 204 or response.status_code == 200:
					# 	flash('Settings have been updated!', 'success')
					# elif response.status_code == 400:
					# 	flash('Server could not find device!', 'danger')
					# else:
					# 	flash('Something happened and settings were not updated.', 'danger')

					db.session.add(session)
					db.session.commit()

				self.local_sessions.pop(index)
				running = False

				# delete the file
				os.remove(file_path)

			# This is where the file will be written too and updated for checkpoints
			else:
				with open(file_path, 'r') as file:
					file_data = file.readlines()

				file_data[1] = "Seconds elapsed: " + str(self.local_sessions[index].elapsed_time().total_seconds())

				with open(file_path, 'w') as file:
					file.writelines(file_data)


			# Save CPU Time, Check every second.
			time.sleep(1)


	def has_sessions(self):
		if len(self.local_sessions) > 0:
			return True
		else:
			return False

# Picture File Interface
class PFI:
	# Starts by grabbing the files and putting them in a list
	def __init__(self):
		self.set_up()

	def get_copy(self):
		return self.pic_files.copy()

	def get_resized_copy(self):
		return self.resized_pic_files.copy()

	def save_file(self, file, resize_width, resize_height):
		file_path = os.path.join(current_app.root_path, 'static', 'picture_files', file.filename)
		file.save(file_path)

		# Do resizing here
		# Last two values should be width and height of desired ratio
		background_color = 'black'
		re_img = self.resize_image(file, background_color, resize_width, resize_height)

		resized_file_path = os.path.join(current_app.root_path, 'static', 'picture_files', 'resized', file.filename)
		re_img.save(resized_file_path)

		# Reset the pic_files
		self.set_up()

	def save_resize_file(self, file):
		file_path = os.path.join(current_app.root_path, 'static', 'picture_files', 'resized', file.filename)
		file.save(file_path)

		# Reset the pic_files
		self.set_up()

	def remove_images(self, file_numbers): # File numbers will come index starting at 1 rather than 0
		index_list = file_numbers.split(",")
		for i in index_list:
			if i.isnumeric():
				index = int(i)-1
				if index >= 0 and index < len(self.pic_files):
					file_path = os.path.join(current_app.root_path, 'static', 'picture_files', self.pic_files[index])
					resized_file_path = os.path.join(current_app.root_path, 'static', 'picture_files', 'resized', self.pic_files[index])
					os.remove(file_path)
					os.remove(resized_file_path)
		# Reset the pic_files
		self.set_up()

	def get_length(self):
		return len(self.pic_files)

	def set_up(self):
		files_path = os.path.join(current_app.root_path, 'static', 'picture_files')
		self.pic_files = [f for f in listdir(files_path) if isfile(join(files_path, f))]

		resized_files_path = os.path.join(current_app.root_path, 'static', 'picture_files', 'resized')
		self.resized_pic_files = [f for f in listdir(resized_files_path) if isfile(join(resized_files_path, f))]

	def resize_all(self, resize_width, resize_height):
		background_color = 'black'
		for file in self.pic_files:
			file_path = os.path.join(current_app.root_path, 'static', 'picture_files', file)
			resized_file_path = os.path.join(current_app.root_path, 'static', 'picture_files', 'resized', file)

			# Delete old resized image
			os.remove(resized_file_path)

			# resize the original image
			re_img = self.resize_image(file_path, background_color, resize_width, resize_height)

			# Save the resized image
			re_img.save(resized_file_path)


	# Return a new image that is resized with black padding
	def resize_image(self, img_file, background_color, width, height):
		img = Image.open(img_file)

		img_width, img_height = img.size

		screen_ratio = width / height
		img_ratio = img_width / img_height

		if img_ratio == screen_ratio:
			return img

		elif img_ratio > screen_ratio:
			new_height = height * img_width / width
			result = Image.new(img.mode, (img_width, int(new_height)), background_color)
			result.paste(img, ( 0, (int(new_height) - img_height) // 2 ) )
			return result

		elif img_ratio < screen_ratio:
			new_width = width * img_height / height
			result = Image.new(img.mode, (int(new_width), img_height), background_color)
			result.paste(img, ( (int(new_width) - img_width) // 2, 0))
			return result