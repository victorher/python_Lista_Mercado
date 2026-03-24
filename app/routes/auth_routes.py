from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from ..models.user import User
from ..services.auth_service import AuthService
from ..services.email_service import EmailService
from ..forms.auth_forms import LoginForm, RegistrationForm, ResetRequestForm, ResetPasswordForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('products.index'))
        flash('Usuario o contraseña incorrectos.', 'danger')
        
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user, error = AuthService.register_user(
            form.username.data, 
            form.email.data, 
            form.password.data
        )
        if not error:
            flash('Cuenta creada con éxito. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        flash(error, 'danger')
        
    return render_template('register.html', form=form)

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))
        
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = AuthService.get_reset_token(user)
            if EmailService.send_reset_password_email(user, token):
                flash('Se ha enviado un correo con instrucciones.', 'info')
            else:
                flash('Error al enviar el correo.', 'danger')
            return redirect(url_for('auth.login'))
        flash('No existe una cuenta con ese correo.', 'warning')
        
    return render_template('reset_request.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('products.index'))
        
    user = AuthService.verify_reset_token(token)
    if not user:
        flash('El token es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.reset_request'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        AuthService.reset_password(user, form.password.data)
        flash('Tu contraseña ha sido actualizada.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_token.html', form=form)
