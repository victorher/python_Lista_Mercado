from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from ..models.user import User

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message="El usuario es obligatorio")])
    password = PasswordField('Contraseña', validators=[DataRequired(message="La contraseña es obligatoria")])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message="El usuario es obligatorio"),
        Length(min=4, max=20, message="El usuario debe tener entre 4 y 20 caracteres")
    ])
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message="El correo es obligatorio"),
        Email(message="Correo electrónico inválido")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria"),
        Length(min=8, message="La contraseña debe tener al menos 8 caracteres")
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message="Las contraseñas deben coincidir")
    ])
    submit = SubmitField('Registrarse')

    # Validación personalizada: Verificar si el usuario ya existe
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este correo electrónico ya está registrado.')

class ResetRequestForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message="El correo es obligatorio"),
        Email(message="Correo electrónico inválido")
    ])
    submit = SubmitField('Solicitar Recuperación')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=8, message="Mínimo 8 caracteres")
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message="Las contraseñas deben coincidir")
    ])
    submit = SubmitField('Cambiar Contraseña')
