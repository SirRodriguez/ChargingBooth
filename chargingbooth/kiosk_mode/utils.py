from flask_login import current_user, logout_user

def start_route():
	if current_user.is_authenticated:
		logout_user()