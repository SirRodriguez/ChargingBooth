from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from chargingbooth.config import Config
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'system_admin_account.login'
login_manager.login_message_category = 'info'
mail = Mail()
service_ip = os.environ.get('SERVICE_IP')

from chargingbooth.models import Sessions_Container, AdminKey, Settings_Cache
admin_key = AdminKey()
current_sessions = Sessions_Container()
settings_cache = Settings_Cache()


def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	print("secret key: ", os.environ.get('SECRET_KEY'))
	print("sql uri: ", os.environ.get('SQLALCHEMY_DATABASE_URI'))
	print("email user: ", os.environ.get('EMAIL_USER'))
	print("email pass: ", os.environ.get('EMAIL_PASS'))
	print("service ip: ", os.environ.get('SERVICE_IP'))

	print("secret key type: ", type(os.environ.get('SECRET_KEY')))
	print("sql uri type: ", type(os.environ.get('SQLALCHEMY_DATABASE_URI')))
	print("email user type: ", type(os.environ.get('EMAIL_USER')))
	print("email pass type: ", type(os.environ.get('EMAIL_PASS')))
	print("service ip type: ", type(os.environ.get('SERVICE_IP')))

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	current_sessions.init_app(app)

	from chargingbooth.main.routes import main
	from chargingbooth.system_admin.main.routes import system_admin_main
	from chargingbooth.system_admin.account.routes import system_admin_account
	from chargingbooth.system_admin.settings.routes import system_admin_settings
	from chargingbooth.system_admin.data.routes import system_admin_data
	from chargingbooth.system_admin.slide_show.routes import system_admin_slide_show
	from chargingbooth.kiosk_mode.routes import kiosk_mode
	from chargingbooth.register.routes import register
	from chargingbooth.error.routes import error

	app.register_blueprint(main)
	app.register_blueprint(system_admin_main)
	app.register_blueprint(system_admin_account)
	app.register_blueprint(system_admin_settings)
	app.register_blueprint(system_admin_data)
	app.register_blueprint(system_admin_slide_show)
	app.register_blueprint(kiosk_mode)
	app.register_blueprint(register)
	app.register_blueprint(error)

	return app