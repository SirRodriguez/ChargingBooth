import threading
import time
from datetime import datetime, timedelta
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from chargingbooth import db, login_manager
from flask_login import UserMixin
from typing import List



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
	power_used = db.Column(db.Float) #Watts
	amount_paid = db.Column(db.Integer) #Cents
	date_initiated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	location = db.Column(db.String(100))
	port = db.Column(db.String(100))
	increment_size = db.Column(db.Integer) #Seconds
	increments = db.Column(db.Integer)


class Settings(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	toggle_pay = db.Column(db.Boolean)
	cents_per_second = db.Column(db.Integer) #Cents per Second
	charge_time = db.Column(db.Integer) #Seconds


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



class Sessions_Container:
	def __init__(self):
		self.local_sessions = dict()
		self.completed_sessions = list()
		self.index = 0
		self.thread_pool = list()

	def add_session(self, amount_paid, location, port, increment_size, increments):
		# define an index for the dictionary
		if len(self.local_sessions.keys()) != 0:
			self.index = self.index + 1
		else:
			self.index = 0
		# Create the session
		self.local_sessions[self.index] = Local_Session(amount_paid, location, port, increment_size, increments, self.index)

		# Create a thread to handle the session and terminate when needed
		sess = threading.Thread(target=self.handler, args=[self.index])
		sess.start()
		self.thread_pool.append(sess)


	# Handler for the sessions
	def handler(self, index):
		running = True
		while(running):
			# Time has run out!
			if(self.local_sessions[index].get_time_remaining() == self.local_sessions[index].zero_time()):
				self.completed_sessions.append(self.local_sessions[index])
				self.local_sessions.pop(index)
				running = False

			# Save CPU Time, Check every second.
			time.sleep(1)
