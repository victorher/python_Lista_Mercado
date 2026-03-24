from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Instanciamos las extensiones
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

# Configuración de LoginManager usando setattr para evitar falsos positivos de Pylance
setattr(login_manager, 'login_view', 'auth.login')
setattr(login_manager, 'login_message', 'Por favor, inicia sesión para acceder.')
setattr(login_manager, 'login_message_category', 'info')
