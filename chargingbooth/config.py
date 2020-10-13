import os

class Config:
	SECRET_KEY = '14c85b73853212ffbf2703072865d612'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = 'testflaskmailserver@gmail.com'
	MAIL_PASSWORD = 'ForTheTest@123'