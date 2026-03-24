from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Instanciamos las extensiones para que puedan ser importadas en cualquier parte
# sin causar importaciones circulares.
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Configuración básica de LoginManager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, inicia sesión para acceder.'
login_manager.login_message_category = 'info'
