from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from chargingbooth.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'system_admin.login'
login_manager.login_message_category = 'info'
mail = Mail()

from chargingbooth.models import Sessions_Container

current_sessions = Sessions_Container()



def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)

	from chargingbooth.main.routes import main
	from chargingbooth.system_admin.routes import system_admin
	from chargingbooth.kiosk_mode.routes import kiosk_mode

	app.register_blueprint(main)
	app.register_blueprint(system_admin)
	app.register_blueprint(kiosk_mode)

	return app