import os
from flask import Flask
from .extensions import db, login_manager, mail, csrf
from .config import config_dict

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
        
    app = Flask(__name__)
    app.config.from_object(config_dict.get(config_name, config_dict['default']))

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # User loader
    from .models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Registro de Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.product_routes import product_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp, url_prefix='/')

    # Registro de comandos CLI (Comando: flask create-admin)
    @app.cli.command("create-admin")
    def create_admin():
        """Crea un usuario administrador inicial."""
        from .services.auth_service import AuthService
        admin_user, error = AuthService.register_user(
            username="admin", 
            email="admin@mercado.com", 
            password="AdminPassword123*"
        )
        if error:
            print(f"Error: {error}")
        else:
            print("Usuario administrador creado exitosamente.")

    with app.app_context():
        db.create_all()

    return app
