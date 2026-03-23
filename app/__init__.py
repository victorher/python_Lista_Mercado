import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
from .models.producto import db, Usuario

# Cargar variables de entorno del archivo .env
load_dotenv()

csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()

def create_app(config_override=None):
    app = Flask(__name__)

    # Configuración de seguridad
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_default_123')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mercado.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_override:
        app.config.update(config_override)

    # ... rest of the config ...

    # Configuración de Mail (SMTP) con conversión segura
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    try:
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
    except (ValueError, TypeError):
        app.config['MAIL_PORT'] = 587

    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    # Inicializar extensiones
    db.init_app(app)
    csrf.init_app(app)
    
    # Configurar login_manager de forma segura (bypass Pylance type check)
    setattr(login_manager, 'login_view', 'mercado.login')
    setattr(login_manager, 'login_message', 'Por favor, inicia sesión para acceder.')
    setattr(login_manager, 'login_message_category', 'info')
    login_manager.init_app(app)
    
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Usar session.get es la forma recomendada en SQLAlchemy 2.0+
        return db.session.get(Usuario, int(user_id))

    # Pre-cargar rutas
    from .routes import mercado_routes
    app.register_blueprint(mercado_routes.bp)

    with app.app_context():
        # Asegurarse de que las tablas existan
        db.create_all()

        # Lógica de usuario administrador por defecto
        try:
            admin_user = Usuario.query.filter_by(username='admin').first()
            if not admin_user:
                admin = Usuario(username='admin', email='admin@ejemplo.com')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
            elif not admin_user.email:
                admin_user.email = 'admin@ejemplo.com'
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            # En un entorno real, usarías logging.error(e)
            print(f"Error al inicializar admin: {e}")

    return app