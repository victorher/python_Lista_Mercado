from flask import current_app, render_template, url_for
from flask_mail import Message
from ..extensions import mail

class EmailService:
    @staticmethod
    def send_reset_password_email(user, token):
        """Envía un correo con el enlace de recuperación de contraseña."""
        msg = Message(
            'Recuperación de Contraseña - Mercado App',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email]
        )
        
        # Generamos la URL completa para el frontend
        reset_url = url_for('auth.reset_with_token', token=token, _external=True)
        
        msg.body = f'''Para resetear tu contraseña, visita el siguiente enlace:
{reset_url}

Si no solicitaste este cambio, simplemente ignora este correo.
El enlace expirará en 30 minutos.
'''
        # Opcional: podrías usar render_template para un HTML bonito
        # msg.html = render_template('emails/reset_password.html', user=user, reset_url=reset_url)
        
        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Error enviando email: {str(e)}")
            return False
