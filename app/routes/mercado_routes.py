from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from ..models.producto import db, Producto, Usuario
from .. import mail

bp = Blueprint('mercado', __name__)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Solicitud de Restablecimiento de Contraseña',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
{url_for('mercado.reset_token', token=token, _external=True)}

Si no realizaste esta solicitud, simplemente ignora este correo y no se realizarán cambios.
'''
    mail.send(msg)

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('mercado.index'))
    if request.method == 'POST':
        email = request.form.get('email')
        user = Usuario.query.filter_by(email=email).first()
        if user:
            try:
                send_reset_email(user)
                flash('Se ha enviado un correo con instrucciones para restablecer tu contraseña.', 'info')
                return redirect(url_for('mercado.login'))
            except Exception as e:
                flash('Error al enviar el correo. Por favor, intenta más tarde.', 'danger')
                # print(f"Mail error: {e}")
        else:
            flash('No existe una cuenta con ese correo electrónico.', 'warning')
    return render_template('reset_request.html')

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('mercado.index'))
    user = Usuario.verify_reset_token(token)
    if user is None:
        flash('El token es inválido o ha expirado.', 'warning')
        return redirect(url_for('mercado.reset_request'))
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('reset_token.html', token=token)
        user.set_password(password)
        db.session.commit()
        flash('Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('mercado.login'))
    return render_template('reset_token.html', token=token)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('mercado.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = Usuario.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('mercado.login'))
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('mercado.index'))
        
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('mercado.login'))

@bp.route('/')
@login_required
def index():
    # Ordenamos por estado de compra (los comprados al final)
    productos = Producto.query.order_by(Producto.tengo_en_casa).all()
    return render_template('index.html', productos=productos)

@bp.route('/agregar', methods=['POST'])
@login_required
def agregar():
    nombre = request.form.get('nombre', '').strip()
    
    # Validación: no agregar si el nombre está vacío o es muy largo
    if not nombre:
        flash('El nombre del producto no puede estar vacío.', 'danger')
        return redirect(url_for('mercado.index'))
    
    if len(nombre) > 100:
        flash('El nombre del producto es demasiado largo (máx 100 caracteres).', 'danger')
        return redirect(url_for('mercado.index'))

    # Conversión segura a entero y validación de rango
    try:
        cantidad = int(request.form.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
    except (ValueError, TypeError):
        cantidad = 1
        
    vencimiento_str = request.form.get('vencimiento')
    
    vencimiento = None
    if vencimiento_str:
        try:
            vencimiento = datetime.strptime(vencimiento_str, '%Y-%m-%d').date()
        except ValueError:
            vencimiento = None
            flash('Formato de fecha de vencimiento inválido.', 'warning')
    
    try:
        nuevo_prod = Producto(nombre=nombre, cantidad=cantidad, fecha_vencimiento=vencimiento)
        db.session.add(nuevo_prod)
        db.session.commit()
        flash(f'Producto "{nombre}" agregado con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al guardar el producto.', 'danger')
    
    return redirect(url_for('mercado.index'))

@bp.route('/toggle/<int:id>')
@login_required
def toggle_comprado(id):
    # Uso moderno de Flask-SQLAlchemy 3.x
    producto = db.get_or_404(Producto, id)
    producto.tengo_en_casa = not producto.tengo_en_casa
    db.session.commit()
    estado = "marcado como comprado" if producto.tengo_en_casa else "devuelto a la lista"
    flash(f'"{producto.nombre}" {estado}.', 'info')
    return redirect(url_for('mercado.index'))
