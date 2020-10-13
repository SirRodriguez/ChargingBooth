from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from chargingbooth.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'system_admin_account.login'
login_manager.login_message_category = 'info'
mail = Mail()
service_ip = "http://localhost:7000"

from chargingbooth.models import Sessions_Container

current_sessions = Sessions_Container()


def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	current_sessions.init_app(app)

	from chargingbooth.main.routes import main

	from chargingbooth.system_admin.routes import system_admin
	from chargingbooth.system_admin.main.routes import system_admin_main
	from chargingbooth.system_admin.account.routes import system_admin_account
	from chargingbooth.system_admin.settings.routes import system_admin_settings

	from chargingbooth.kiosk_mode.routes import kiosk_mode

	from chargingbooth.register.routes import register

	app.register_blueprint(main)

	app.register_blueprint(system_admin)
	app.register_blueprint(system_admin_main)
	app.register_blueprint(system_admin_account)
	app.register_blueprint(system_admin_settings)

	app.register_blueprint(kiosk_mode)

	app.register_blueprint(register)

	return app