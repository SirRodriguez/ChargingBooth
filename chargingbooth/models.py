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
	def __init__(self, amount_paid, location, port, increment_size, increments):
		self.date_initiated = datetime.utcnow()
		self.amount_paid = amount_paid
		self.location = location
		self.port = port
		self.increment_size = increment_size
		self.increments = increments

	def get_time_remaining(self):
		total_seconds = self.increment_size * self.increments
		elapsed_time = datetime.utcnow() - self.date_initiated
		time_remain = timedelta(seconds=total_seconds) - elapsed_time

		if time_remain < timedelta(seconds=0):
			return "0:00:00"
		else:
			return str(time_remain).split(".")[0]



class Sessions_Container:
	def __init__(self):
		self.local_sessions = list()

	def add_session(self, amount_paid, location, port, increment_size, increments):
		self.local_sessions.append(Local_Session(amount_paid, location, port, increment_size, increments))