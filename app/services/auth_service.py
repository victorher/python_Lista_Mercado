from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
from ..extensions import db
from ..models.user import User

class AuthService:
    @staticmethod
    def register_user(username, email, password):
        """Lógica de registro de nuevo usuario."""
        if User.query.filter_by(username=username).first():
            return None, "El nombre de usuario ya existe."
        if User.query.filter_by(email=email).first():
            return None, "El correo electrónico ya está registrado."
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def get_reset_token(user, expires_sec=1800):
        """Genera un token seguro para recuperación de contraseña."""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': user.id})

    @staticmethod
    def verify_reset_token(token):
        """Verifica el token y devuelve al usuario correspondiente."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=1800)
            user_id = data.get('user_id')
        except:
            return None
        return db.session.get(User, user_id)

    @staticmethod
    def reset_password(user, new_password):
        """Actualiza la contraseña del usuario."""
        user.set_password(new_password)
        db.session.commit()
        return True
